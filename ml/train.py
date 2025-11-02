"""
ML Model Training for FinGuard AI
Trains a RandomForest classifier with SHAP explainability
"""
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib

# Feature engineering functions
def engineer_features(df, merchants_df):
    """Create features for fraud detection"""
    features = df.copy()
    
    # Merge merchant data
    merchant_risk = merchants_df.set_index('merchant_id')['risk_level'].to_dict()
    features['merchant_risk_score'] = features['merchant_id'].map(
        lambda x: {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}.get(merchant_risk.get(x, 'MEDIUM'), 1)
    )
    
    # Amount features
    features['amount_log'] = np.log1p(features['amount'])
    
    # Time features
    features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
    features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
    features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
    features['is_night'] = features['hour'].isin(list(range(0, 6)) + list(range(22, 24))).astype(int)
    
    # MCC encoding (simplified)
    features['mcc_num'] = features['mcc'].astype(int)
    
    # Velocity features (transactions per card in last 2 hours)
    features = features.sort_values('ts')
    features['txn_velocity_2h'] = 0
    
    for card_id in features['card_id'].unique():
        card_mask = features['card_id'] == card_id
        card_txns = features[card_mask].copy()
        
        for idx in card_txns.index:
            current_ts = features.loc[idx, 'ts']
            recent_window = (features['ts'] >= current_ts - 7200) & (features['ts'] < current_ts)
            card_recent = recent_window & card_mask
            features.loc[idx, 'txn_velocity_2h'] = card_recent.sum()
    
    # Device mismatch (simplified: assume first device is primary)
    card_primary_device = features.groupby('card_id')['device_id'].first().to_dict()
    features['device_mismatch'] = (
        features.apply(lambda row: 1 if row['device_id'] != card_primary_device.get(row['card_id']) else 0, axis=1)
    )
    
    # Geo features (distance from first transaction - proxy for home)
    card_home_geo = features.groupby('card_id').first()[['geo_lat', 'geo_lon']].to_dict('index')
    
    def calc_distance(row):
        card = row['card_id']
        if card not in card_home_geo:
            return 0
        home = card_home_geo[card]
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = radians(home['geo_lat']), radians(home['geo_lon'])
        lat2, lon2 = radians(row['geo_lat']), radians(row['geo_lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return c * 6371  # km
    
    features['distance_from_home'] = features.apply(calc_distance, axis=1)
    features['geo_jump'] = (features['distance_from_home'] > 2000).astype(int)
    
    return features


def select_model_features():
    """Define features for the model"""
    return [
        'amount_log',
        'merchant_risk_score',
        'hour',
        'is_weekend',
        'is_night',
        'mcc_num',
        'txn_velocity_2h',
        'device_mismatch',
        'distance_from_home',
        'geo_jump',
    ]


def train_model(X_train, y_train, X_test, y_test):
    """Train RandomForest classifier"""
    print("\n3. Training RandomForest classifier...")
    
    # Model configuration optimized for demo performance
    model = RandomForestClassifier(
        n_estimators=50,  # Reduced for faster inference
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',  # Handle imbalanced data
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n4. Model Evaluation:")
    print("-" * 50)
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))
    print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]:5d}  FP: {cm[0,1]:5d}")
    print(f"  FN: {cm[1,0]:5d}  TP: {cm[1,1]:5d}")
    
    # Feature importance
    print("\n5. Feature Importance:")
    print("-" * 50)
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for _, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:25s}: {row['importance']:.4f}")
    
    return model


def main():
    print("FinGuard AI - Model Training")
    print("=" * 50)
    
    # Load data
    print("\n1. Loading synthetic data...")
    data_dir = Path("seed-data")
    
    transactions_df = pd.read_csv(data_dir / "replay_day_01.csv")
    with open(data_dir / "merchants.json") as f:
        merchants_data = json.load(f)
    merchants_df = pd.DataFrame(merchants_data)
    
    print(f"   Loaded {len(transactions_df)} transactions")
    print(f"   Loaded {len(merchants_df)} merchants")
    print(f"   Fraud rate: {transactions_df['is_fraud'].mean()*100:.2f}%")
    
    # Feature engineering
    print("\n2. Engineering features...")
    features_df = engineer_features(transactions_df, merchants_df)
    
    # Select features
    feature_cols = select_model_features()
    X = features_df[feature_cols]
    y = features_df['is_fraud'].astype(int)
    
    print(f"   Created {len(feature_cols)} features")
    print(f"   Features: {', '.join(feature_cols)}")
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = train_model(X_train, y_train, X_test, y_test)
    
    # Save artifacts
    print("\n6. Saving model artifacts...")
    ml_dir = Path("ml")
    ml_dir.mkdir(exist_ok=True)
    
    model_path = ml_dir / "model.pkl"
    features_path = ml_dir / "features.json"
    
    joblib.dump(model, model_path)
    
    feature_metadata = {
        'features': feature_cols,
        'feature_importances': model.feature_importances_.tolist(),
        'version': '1.0.0',
        'trained_at': pd.Timestamp.now().isoformat()
    }

    with open(features_path, 'w') as f:
        json.dump(feature_metadata, f, indent=2)
    
    print(f"   Model saved -> {model_path}")
    print(f"   Features saved -> {features_path}")
    
    # Model size
    model_size = model_path.stat().st_size / (1024 * 1024)
    print(f"\n   Model size: {model_size:.2f} MB")
    
    print("\n" + "=" * 50)
    print("Model training complete!")
    print("\nNext steps:")
    print("   1. Upload model.pkl to S3: finguard-models-{account-id}")
    print("   2. Deploy API with: ./scripts/deploy.ps1")


if __name__ == "__main__":
    main()

