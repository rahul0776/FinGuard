"""
Fraud scoring engine with rules and ML model
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import boto3
import numpy as np

try:
    import onnxruntime as ort
    ONNXRUNTIME_AVAILABLE = True
except ImportError:
    ort = None
    ONNXRUNTIME_AVAILABLE = False

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Load environment variables
MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'finguard-models')
TRANSACTIONS_TABLE = os.environ.get('TRANSACTIONS_TABLE', 'finguard-transactions')

# Global model cache
_onnx_session = None
_features_config = None


def load_model() -> Tuple[object, Dict]:
    """Load ONNX model from S3 (cached)."""

    global _onnx_session, _features_config

    if _onnx_session is not None:
        return _onnx_session, _features_config

    if not ONNXRUNTIME_AVAILABLE:
        print("ONNX Runtime not available; falling back to rules engine.")
        _features_config = {"features": [], "feature_importances": []}
        return None, _features_config

    print("Loading ONNX model from S3...")

    model_path = "/tmp/model.onnx"
    features_path = "/tmp/features.json"

    try:
        s3_client.download_file(MODEL_BUCKET, "model.onnx", model_path)
        s3_client.download_file(MODEL_BUCKET, "features.json", features_path)

        with open(features_path) as f:
            _features_config = json.load(f)

        _onnx_session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )

        print(f"Model loaded (v{_features_config.get('version', '1.0.0')})")

    except Exception as exc:
        print(f"Model load failed: {exc}")
        _onnx_session = None
        _features_config = {"features": [], "feature_importances": []}

    return _onnx_session, _features_config


def get_card_history(card_id: str, lookback_hours: int = 2) -> List[Dict]:
    """Fetch recent transactions for a card from DynamoDB"""
    table = dynamodb.Table(TRANSACTIONS_TABLE)
    
    cutoff_ts = int((datetime.now() - timedelta(hours=lookback_hours)).timestamp())
    
    try:
        response = table.query(
            IndexName='card-index',
            KeyConditionExpression='card_id = :card_id AND SK >= :cutoff',
            ExpressionAttributeValues={
                ':card_id': card_id,
                ':cutoff': f'ts#{cutoff_ts}'
            },
            Limit=100
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error fetching card history: {e}")
        return []


def calculate_distance(geo1: Dict, geo2: Dict) -> float:
    """Calculate distance in km between two geo points"""
    from math import radians, cos, sin, asin, sqrt
    
    lat1, lon1 = radians(geo1['lat']), radians(geo1['lon'])
    lat2, lon2 = radians(geo2['lat']), radians(geo2['lon'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371


def _extract_probability(outputs: List[np.ndarray]) -> float:
    """Extract fraud probability from ONNX outputs."""

    for value in outputs:
        if isinstance(value, np.ndarray):
            if value.ndim == 2:
                return float(value[0, -1])
            if value.ndim == 1:
                return float(value[-1])
        if isinstance(value, list) and value and isinstance(value[0], dict):
            prob_dict = value[0]
            fraud_key = sorted(prob_dict.keys())[-1]
            return float(prob_dict[fraud_key])

    return 0.0


def apply_rules(txn: Dict, card_history: List[Dict]) -> Tuple[List[str], Dict]:
    """Apply rule-based fraud detection"""
    triggered_rules = []
    rule_scores = {}
    
    # Rule 1: Velocity - More than 3 transactions in 2 minutes
    if card_history:
        recent_2min = [
            t for t in card_history 
            if txn['ts'] - t.get('ts', 0) <= 120
        ]
        if len(recent_2min) >= 3:
            triggered_rules.append("VELOCITY_HIGH")
            rule_scores['velocity_2min'] = len(recent_2min)
    
    # Rule 2: Amount threshold - Unusually high transaction
    if txn['amount'] > 1000:
        triggered_rules.append("AMOUNT_HIGH")
        rule_scores['amount'] = txn['amount']
    
    # Rule 3: High-risk MCC categories
    high_risk_mccs = ['5732', '7995', '5960', '6211', '7273']
    if txn['mcc'] in high_risk_mccs:
        triggered_rules.append("MCC_HIGH_RISK")
        rule_scores['mcc_risk'] = 1
    
    # Rule 4: Geo-impossible travel
    if card_history:
        last_txn = max(card_history, key=lambda t: t.get('ts', 0))
        if last_txn:
            distance = calculate_distance(txn['geo'], last_txn.get('geo', txn['geo']))
            time_diff_hours = (txn['ts'] - last_txn.get('ts', txn['ts'])) / 3600
            
            if time_diff_hours > 0 and distance / time_diff_hours > 800:  # >800 km/h
                triggered_rules.append("GEO_IMPOSSIBLE")
                rule_scores['geo_jump_km'] = distance
    
    # Rule 5: Device mismatch
    if card_history:
        primary_device = max(
            set([t.get('device_id') for t in card_history if t.get('device_id')]),
            key=lambda d: sum(1 for t in card_history if t.get('device_id') == d),
            default=txn['device_id']
        )
        if txn['device_id'] != primary_device:
            triggered_rules.append("DEVICE_MISMATCH")
            rule_scores['device_match'] = 0
    
    # Rule 6: Night transactions (00:00 - 06:00)
    hour = datetime.fromtimestamp(txn['ts']).hour
    if 0 <= hour < 6:
        triggered_rules.append("TIME_NIGHT")
        rule_scores['hour'] = hour
    
    return triggered_rules, rule_scores


def engineer_features(
    txn: Dict,
    card_history: List[Dict],
    rule_scores: Dict,
    feature_names: List[str],
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Engineer ordered feature vector and raw feature mapping."""

    txn_dt = datetime.fromtimestamp(txn["ts"])

    feature_map: Dict[str, float] = {
        "amount_log": float(np.log1p(txn["amount"])),
        "merchant_risk_score": float(rule_scores.get("mcc_risk", 0)),
        "hour": float(txn_dt.hour),
        "is_weekend": float(1 if txn_dt.weekday() >= 5 else 0),
        "is_night": float(1 if 0 <= txn_dt.hour < 6 else 0),
        "mcc_num": float(int(txn.get("mcc", 0) or 0)),
        "txn_velocity_2h": float(rule_scores.get("velocity_2min", 0)),
        "device_mismatch": float(1 if rule_scores.get("device_match", 1) == 0 else 0),
        "distance_from_home": float(rule_scores.get("geo_jump_km", 0)),
        "geo_jump": float(1 if rule_scores.get("geo_jump_km", 0) > 2000 else 0),
    }

    ordered_values = [feature_map.get(name, 0.0) for name in feature_names]
    features_array = np.array([ordered_values], dtype=np.float32)

    return features_array, feature_map


def build_model_explanation(
    feature_names: List[str],
    feature_map: Dict[str, float],
    features_config: Dict,
    txn: Dict,
    rule_scores: Dict,
) -> Dict:
    """Create lightweight feature importance explanation."""

    importances = features_config.get("feature_importances", [])
    contributions = []

    for idx, name in enumerate(feature_names):
        importance = float(importances[idx]) if idx < len(importances) else 0.0
        value = float(feature_map.get(name, 0.0))
        score = abs(value) * importance
        contributions.append(
            {
                "name": name,
                "value": value,
                "importance": importance,
                "contribution": score,
            }
        )

    contributions.sort(key=lambda item: item["contribution"], reverse=True)

    total = sum(c["contribution"] for c in contributions) or 1.0
    for c in contributions:
        c["contribution_pct"] = (c["contribution"] / total) * 100

    # Generate a simple narrative from the top drivers
    reasons: List[str] = []
    top_features = contributions[:3]

    for feature in top_features:
        name = feature["name"]
        if "amount" in name:
            reasons.append(f"elevated amount (${txn['amount']:.2f})")
        elif "velocity" in name and feature_map.get("txn_velocity_2h", 0) > 0:
            reasons.append(
                f"recent activity spike ({int(feature_map.get('txn_velocity_2h', 0))} txns)"
            )
        elif "geo" in name and feature_map.get("distance_from_home", 0) > 0:
            reasons.append(
                f"geo change (~{feature_map.get('distance_from_home', 0):.0f} km)"
            )
        elif "device" in name and feature_map.get("device_mismatch", 0) == 1:
            reasons.append("new device usage")
        elif "merchant" in name and rule_scores.get("mcc_risk"):
            reasons.append("high-risk merchant category")

    if not reasons:
        reasons.append("patterns deviating from typical behaviour")

    explanation_text = "Model signals " + ", ".join(reasons) + "."

    return {
        "top_features": contributions[:5],
        "text": explanation_text,
    }


def score_transaction(txn: Dict) -> Tuple[float, str, List[str], Dict]:
    """
    Score a transaction for fraud
    Returns: (score, risk_level, triggered_rules, explanation)
    """
    
    # Get card history
    card_history = get_card_history(txn['card_id'])
    
    # Apply rules
    triggered_rules, rule_scores = apply_rules(txn, card_history)
    
    # Base rule score
    rule_score = len(triggered_rules) * 0.15
    
    # Try ML model
    ml_score = 0.0
    explanation = {'top_features': [], 'text': 'Rules-based detection.'}
    
    session, features_config = load_model()

    if session is not None:
        try:
            feature_names = features_config.get("features", [])
            features_array, feature_map = engineer_features(
                txn, card_history, rule_scores, feature_names
            )

            input_name = session.get_inputs()[0].name
            outputs = session.run(None, {input_name: features_array})
            ml_score = _extract_probability(outputs)

            explanation = build_model_explanation(
                feature_names,
                feature_map,
                features_config,
                txn,
                rule_scores,
            )

        except Exception as exc:
            print(f"ML scoring failed: {exc}")
            ml_score = 0.0
    
    # Combine scores
    final_score = max(rule_score, ml_score)
    final_score = min(final_score, 1.0)  # Cap at 1.0
    
    # Determine risk level
    if final_score >= 0.8:
        risk_level = "CRITICAL"
    elif final_score >= 0.6:
        risk_level = "HIGH"
    elif final_score >= 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return final_score, risk_level, triggered_rules, explanation


def should_create_alert(score: float, risk_level: str) -> bool:
    """Determine if an alert should be created"""
    return risk_level in ["HIGH", "CRITICAL"] or score >= 0.6

