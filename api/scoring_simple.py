"""
Simplified fraud scoring engine (rules-only, no ML dependencies)
"""
import os
import boto3
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Load environment variables
TRANSACTIONS_TABLE = os.environ.get('TRANSACTIONS_TABLE', 'finguard-transactions')


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


def apply_rules(txn: Dict, card_history: List[Dict]) -> Tuple[float, List[str], Dict]:
    """Apply rule-based fraud detection"""
    triggered_rules = []
    score = 0.0
    rule_details = {}
    
    # Rule 1: Velocity - More than 3 transactions in 2 minutes
    if card_history:
        recent_2min = [
            t for t in card_history 
            if txn['ts'] - t.get('ts', 0) <= 120
        ]
        if len(recent_2min) >= 3:
            triggered_rules.append("VELOCITY_HIGH")
            score += 0.3
            rule_details['velocity'] = len(recent_2min)
    
    # Rule 2: Amount threshold - Unusually high transaction
    if txn['amount'] > 1000:
        triggered_rules.append("AMOUNT_HIGH")
        score += 0.25
        rule_details['amount'] = txn['amount']
    
    # Rule 3: Very high amount
    if txn['amount'] > 5000:
        triggered_rules.append("AMOUNT_CRITICAL")
        score += 0.4
    
    # Rule 4: High-risk MCC categories
    high_risk_mccs = ['5732', '7995', '5960', '6211', '7273']
    if txn['mcc'] in high_risk_mccs:
        triggered_rules.append("MCC_HIGH_RISK")
        score += 0.2
        rule_details['mcc'] = txn['mcc']
    
    # Rule 5: Geo-impossible travel
    if card_history:
        last_txn = max(card_history, key=lambda t: t.get('ts', 0))
        if last_txn:
            distance = calculate_distance(txn['geo'], last_txn.get('geo', txn['geo']))
            time_diff_hours = (txn['ts'] - last_txn.get('ts', txn['ts'])) / 3600
            
            if time_diff_hours > 0 and distance / time_diff_hours > 800:  # >800 km/h
                triggered_rules.append("GEO_IMPOSSIBLE")
                score += 0.5
                rule_details['geo_jump_km'] = distance
    
    # Rule 6: Device mismatch
    if card_history:
        devices = [t.get('device_id') for t in card_history if t.get('device_id')]
        if devices:
            primary_device = max(set(devices), key=devices.count)
            if txn['device_id'] != primary_device:
                triggered_rules.append("DEVICE_MISMATCH")
                score += 0.15
                rule_details['device_match'] = 0
    
    # Rule 7: Night transactions (00:00 - 06:00)
    hour = datetime.fromtimestamp(txn['ts']).hour
    if 0 <= hour < 6:
        triggered_rules.append("TIME_NIGHT")
        score += 0.1
        rule_details['hour'] = hour
    
    # Cap score at 1.0
    score = min(score, 1.0)
    
    return score, triggered_rules, rule_details


def generate_explanation(triggered_rules: List[str], rule_details: Dict) -> Dict:
    """Generate explanation for the fraud score"""
    
    feature_contributions = []
    
    # Map rules to features
    if 'VELOCITY_HIGH' in triggered_rules:
        feature_contributions.append({
            'name': 'transaction_velocity',
            'value': rule_details.get('velocity', 0),
            'contribution': 0.3,
            'contribution_pct': 30.0
        })
    
    if 'AMOUNT_HIGH' in triggered_rules or 'AMOUNT_CRITICAL' in triggered_rules:
        contrib = 0.4 if 'AMOUNT_CRITICAL' in triggered_rules else 0.25
        feature_contributions.append({
            'name': 'transaction_amount',
            'value': rule_details.get('amount', 0),
            'contribution': contrib,
            'contribution_pct': contrib * 100
        })
    
    if 'MCC_HIGH_RISK' in triggered_rules:
        feature_contributions.append({
            'name': 'merchant_risk_category',
            'value': int(rule_details.get('mcc', 0)),
            'contribution': 0.2,
            'contribution_pct': 20.0
        })
    
    if 'GEO_IMPOSSIBLE' in triggered_rules:
        feature_contributions.append({
            'name': 'geographic_jump',
            'value': rule_details.get('geo_jump_km', 0),
            'contribution': 0.5,
            'contribution_pct': 50.0
        })
    
    if 'DEVICE_MISMATCH' in triggered_rules:
        feature_contributions.append({
            'name': 'device_anomaly',
            'value': 1,
            'contribution': 0.15,
            'contribution_pct': 15.0
        })
    
    if 'TIME_NIGHT' in triggered_rules:
        feature_contributions.append({
            'name': 'unusual_time',
            'value': rule_details.get('hour', 0),
            'contribution': 0.1,
            'contribution_pct': 10.0
        })
    
    # Generate text explanation
    if triggered_rules:
        reasons = []
        if 'VELOCITY_HIGH' in triggered_rules:
            reasons.append(f"high transaction velocity ({rule_details.get('velocity', 0)} txns in 2 min)")
        if 'AMOUNT_CRITICAL' in triggered_rules:
            reasons.append(f"critical amount (${rule_details.get('amount', 0):,.2f})")
        elif 'AMOUNT_HIGH' in triggered_rules:
            reasons.append(f"unusual amount (${rule_details.get('amount', 0):,.2f})")
        if 'GEO_IMPOSSIBLE' in triggered_rules:
            reasons.append(f"impossible travel distance ({rule_details.get('geo_jump_km', 0):.0f} km)")
        if 'MCC_HIGH_RISK' in triggered_rules:
            reasons.append("high-risk merchant category")
        if 'DEVICE_MISMATCH' in triggered_rules:
            reasons.append("unrecognized device")
        if 'TIME_NIGHT' in triggered_rules:
            reasons.append("late night transaction")
        
        explanation_text = f"Transaction flagged due to: {', '.join(reasons)}."
    else:
        explanation_text = "Transaction appears normal based on available patterns."
    
    return {
        'top_features': feature_contributions[:5],
        'text': explanation_text
    }


def score_transaction(txn: Dict) -> Tuple[float, str, List[str], Dict]:
    """
    Score a transaction for fraud (rules-only)
    Returns: (score, risk_level, triggered_rules, explanation)
    """
    
    # Get card history
    card_history = get_card_history(txn['card_id'])
    
    # Apply rules
    score, triggered_rules, rule_details = apply_rules(txn, card_history)
    
    # Determine risk level
    if score >= 0.8:
        risk_level = "CRITICAL"
    elif score >= 0.6:
        risk_level = "HIGH"
    elif score >= 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Generate explanation
    explanation = generate_explanation(triggered_rules, rule_details)
    
    return score, risk_level, triggered_rules, explanation


def should_create_alert(score: float, risk_level: str) -> bool:
    """Determine if an alert should be created"""
    return risk_level in ["HIGH", "CRITICAL"] or score >= 0.6



