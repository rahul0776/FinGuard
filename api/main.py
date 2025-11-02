"""
FinGuard API - FastAPI backend with Lambda support (Mangum)
"""
import os
import time
import boto3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import json

from models import (
    Transaction, TransactionResponse, Alert, AlertListResponse, 
    KPIMetrics, ReplayRequest, FeatureContribution, Explanation
)
from scoring_simple import score_transaction, should_create_alert

# Initialize FastAPI
app = FastAPI(
    title="FinGuard API",
    description="Real-time fraud detection with rules-based scoring",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
apigateway_client = boto3.client('apigatewaymanagementapi')

# Environment variables
TRANSACTIONS_TABLE = os.environ.get('TRANSACTIONS_TABLE', 'finguard-transactions')
ALERTS_TABLE = os.environ.get('ALERTS_TABLE', 'finguard-alerts')
MERCHANTS_TABLE = os.environ.get('MERCHANTS_TABLE', 'finguard-merchants')
CONNECTIONS_TABLE = os.environ.get('CONNECTIONS_TABLE', 'finguard-connections')
WEBSOCKET_ENDPOINT = os.environ.get('WEBSOCKET_ENDPOINT', '')


def convert_floats_to_decimal(obj: Any) -> Any:
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    return obj


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "FinGuard AI API",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "transactions": "/api/transactions",
            "alerts": "/api/alerts",
            "replay": "/api/replay"
        }
    }


@app.get("/health")
async def health():
    """Health check for ALB"""
    return {"status": "healthy"}


@app.post("/api/transactions", response_model=TransactionResponse)
async def ingest_transaction(txn: Transaction):
    """
    Ingest and score a transaction
    """
    start_time = time.time()
    
    try:
        # Score transaction
        score, risk_level, triggered_rules, explanation = score_transaction(txn.dict())
        
        # Store in DynamoDB
        table = dynamodb.Table(TRANSACTIONS_TABLE)
        txn_item = {
            'PK': f'TXN#{txn.txn_id}',
            'SK': f'ts#{txn.ts}',
            **txn.dict(),
            'score': Decimal(str(score)),
            'risk_level': risk_level,
            'flags': triggered_rules,
        }
        # Convert floats to Decimals for DynamoDB
        txn_item = convert_floats_to_decimal(txn_item)
        table.put_item(Item=txn_item)
        
        # Create alert if needed
        alert_id = None
        if should_create_alert(score, risk_level):
            alert_id = await create_alert(txn, score, risk_level, triggered_rules, explanation)
        
        processing_time = (time.time() - start_time) * 1000
        
        return TransactionResponse(
            txn_id=txn.txn_id,
            score=score,
            risk_level=risk_level,
            is_alert=alert_id is not None,
            alert_id=alert_id,
            processing_time_ms=round(processing_time, 2)
        )
    
    except Exception as e:
        print(f"Error processing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def create_alert(
    txn: Transaction, 
    score: float, 
    risk_level: str, 
    triggered_rules: List[str],
    explanation: dict
) -> str:
    """Create an alert and notify via WebSocket"""
    
    alert_id = f"ALRT-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{txn.txn_id[-4:]}"
    
    alert = Alert(
        alert_id=alert_id,
        txn_id=txn.txn_id,
        card_id=txn.card_id,
        merchant_id=txn.merchant_id,
        merchant_name=txn.merchant_name,
        amount=txn.amount,
        score=score,
        risk_level=risk_level,
        rules=triggered_rules,
        explanation=Explanation(**explanation),
        status="NEW",
        created_at=txn.ts,
        timestamp=txn.timestamp
    )
    
    # Store in DynamoDB
    table = dynamodb.Table(ALERTS_TABLE)
    alert_item = {
        'PK': alert_id,
        'created_at': txn.ts,
        **alert.dict()
    }
    # Convert floats to Decimals for DynamoDB
    alert_item = convert_floats_to_decimal(alert_item)
    table.put_item(Item=alert_item)
    
    # Notify WebSocket clients
    await broadcast_alert(alert)
    
    return alert_id


async def broadcast_alert(alert: Alert):
    """Broadcast alert to all WebSocket connections"""
    try:
        # Get all active connections
        connections_table = dynamodb.Table(CONNECTIONS_TABLE)
        response = connections_table.scan()
        
        message = json.dumps({
            'type': 'alert',
            'data': alert.dict()
        })
        
        # Send to all connections
        for item in response.get('Items', []):
            connection_id = item['connectionId']
            try:
                # Parse WebSocket endpoint
                endpoint_url = WEBSOCKET_ENDPOINT.replace('wss://', 'https://').replace('/Prod', '/@connections')
                
                client = boto3.client(
                    'apigatewaymanagementapi',
                    endpoint_url=endpoint_url
                )
                
                client.post_to_connection(
                    ConnectionId=connection_id,
                    Data=message.encode('utf-8')
                )
            except Exception as e:
                print(f"Failed to send to {connection_id}: {e}")
                # Remove stale connection
                connections_table.delete_item(Key={'connectionId': connection_id})
    
    except Exception as e:
        print(f"Broadcast failed: {e}")


@app.get("/api/alerts", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    risk_level: Optional[str] = None
):
    """List recent alerts"""
    try:
        table = dynamodb.Table(ALERTS_TABLE)
        
        # Scan with filters (in production, use GSI for better performance)
        response = table.scan()
        items = response.get('Items', [])
        
        # Filter by risk level if specified
        if risk_level:
            items = [item for item in items if item.get('risk_level') == risk_level]
        
        # Sort by created_at descending
        items.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = items[start_idx:end_idx]
        
        # Convert to Alert models
        alerts = []
        for item in page_items:
            try:
                alert = Alert(**item)
                alerts.append(alert)
            except Exception as e:
                print(f"Error parsing alert: {e}")
        
        return AlertListResponse(
            alerts=alerts,
            total=len(items),
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        print(f"Error listing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Get alert details"""
    try:
        table = dynamodb.Table(ALERTS_TABLE)
        response = table.get_item(Key={'PK': alert_id})
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return Alert(**response['Item'])
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics", response_model=KPIMetrics)
async def get_metrics():
    """Get KPI metrics"""
    try:
        # Query transactions and alerts tables
        txns_table = dynamodb.Table(TRANSACTIONS_TABLE)
        alerts_table = dynamodb.Table(ALERTS_TABLE)
        
        # Get counts (simplified for demo)
        txns_response = txns_table.scan(Select='COUNT')
        alerts_response = alerts_table.scan()
        
        total_transactions = txns_response['Count']
        alerts = alerts_response.get('Items', [])
        total_alerts = len(alerts)
        
        # Calculate metrics
        alert_rate = (total_alerts / total_transactions * 100) if total_transactions > 0 else 0
        avg_score = sum(a.get('score', 0) for a in alerts) / len(alerts) if alerts else 0
        high_risk_count = sum(1 for a in alerts if a.get('risk_level') in ['HIGH', 'CRITICAL'])
        
        return KPIMetrics(
            total_transactions=total_transactions,
            total_alerts=total_alerts,
            alert_rate=round(alert_rate, 2),
            avg_score=round(avg_score, 3),
            avg_latency_ms=95.5,  # Placeholder
            high_risk_count=high_risk_count
        )
    
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{alert_id}")
async def generate_report(alert_id: str):
    """Generate PDF report for an alert"""
    try:
        from reports import generate_pdf_report
        
        # Get alert
        alert = await get_alert(alert_id)
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(alert)
        
        # Upload to S3
        reports_bucket = os.environ.get('REPORTS_BUCKET', 'finguard-reports')
        report_key = f"reports/{alert_id}.pdf"
        
        s3_client.put_object(
            Bucket=reports_bucket,
            Key=report_key,
            Body=pdf_bytes,
            ContentType='application/pdf'
        )
        
        # Generate presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': reports_bucket, 'Key': report_key},
            ExpiresIn=300  # 5 minutes
        )
        
        return {"download_url": url}
    
    except Exception as e:
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/replay")
async def trigger_replay(request: ReplayRequest):
    """Trigger transaction replay (webhook from frontend)"""
    import hashlib
    import hmac
    
    try:
        # Verify webhook signature
        webhook_secret = os.environ.get('WEBHOOK_SECRET', 'dev-secret-key')
        
        # In production, verify HMAC signature
        # For demo, simplified validation
        
        # Invoke simulator Lambda
        lambda_client = boto3.client('lambda')
        
        # Get simulator function name from environment variable
        simulator_function = os.environ.get('SIMULATOR_FUNCTION', 'finguard-simulator')
        
        # Get AWS region
        region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Get account ID from STS
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        
        # Use full ARN for Lambda invoke (more reliable for IAM permissions)
        simulator_arn = f"arn:aws:lambda:{region}:{account_id}:function:{simulator_function}"
        
        payload = {
            'replay_file': request.replay_file,
            'speed_multiplier': request.speed_multiplier
        }
        
        response = lambda_client.invoke(
            FunctionName=simulator_arn,
            InvocationType='Event',  # Async
            Payload=json.dumps(payload)
        )
        
        return {
            "status": "started",
            "message": f"Replay initiated for {request.replay_file}",
            "replay_file": request.replay_file
        }
    
    except Exception as e:
        print(f"Error triggering replay: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Lambda handler (Mangum adapter)
handler = Mangum(app, lifespan="off")

