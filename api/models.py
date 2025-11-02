"""
Pydantic models for FinGuard API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class GeoLocation(BaseModel):
    lat: float
    lon: float
    city: str
    country: str


class Transaction(BaseModel):
    txn_id: str
    card_id: str
    merchant_id: str
    merchant_name: str
    mcc: str
    category: str
    amount: float
    timestamp: str
    ts: int
    device_id: str
    geo: GeoLocation


class FeatureContribution(BaseModel):
    name: str
    value: float
    contribution: float
    contribution_pct: float


class Explanation(BaseModel):
    top_features: List[FeatureContribution]
    text: str


class Alert(BaseModel):
    alert_id: str
    txn_id: str
    card_id: str
    merchant_id: str
    merchant_name: str
    amount: float
    score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    rules: List[str]
    explanation: Explanation
    status: str = "NEW"
    created_at: int
    timestamp: str


class TransactionResponse(BaseModel):
    txn_id: str
    score: float
    risk_level: str
    is_alert: bool
    alert_id: Optional[str] = None
    processing_time_ms: float


class AlertListResponse(BaseModel):
    alerts: List[Alert]
    total: int
    page: int
    page_size: int


class KPIMetrics(BaseModel):
    total_transactions: int
    total_alerts: int
    alert_rate: float
    avg_score: float
    avg_latency_ms: float
    high_risk_count: int


class ReplayRequest(BaseModel):
    replay_file: str = "replay_day_01.csv"
    speed_multiplier: float = 1.0
    webhook_signature: str



