export interface GeoLocation {
  lat: number;
  lon: number;
  city: string;
  country: string;
}

export interface Transaction {
  txn_id: string;
  card_id: string;
  merchant_id: string;
  merchant_name: string;
  mcc: string;
  category: string;
  amount: number;
  timestamp: string;
  ts: number;
  device_id: string;
  geo: GeoLocation;
}

export interface FeatureContribution {
  name: string;
  value: number;
  contribution: number;
  contribution_pct: number;
}

export interface Explanation {
  top_features: FeatureContribution[];
  text: string;
}

export interface Alert {
  alert_id: string;
  txn_id: string;
  card_id: string;
  merchant_id: string;
  merchant_name: string;
  amount: number;
  score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  rules: string[];
  explanation: Explanation;
  status: string;
  created_at: number;
  timestamp: string;
}

export interface KPIMetrics {
  total_transactions: number;
  total_alerts: number;
  alert_rate: number;
  avg_score: number;
  avg_latency_ms: number;
  high_risk_count: number;
}



