"""
Transaction Replay Simulator Lambda
Streams synthetic transactions to the API for demo purposes
"""
import os
import json
import time
import csv
import boto3
import requests
from io import StringIO

s3_client = boto3.client('s3')

RAW_BUCKET = os.environ.get('RAW_BUCKET', 'finguard-raw')
API_ENDPOINT = os.environ.get('API_ENDPOINT', '')


def lambda_handler(event, context):
    """
    Replay transactions from S3 CSV file
    """
    print(f"Replay event received: {json.dumps(event)}")
    print(f"API_ENDPOINT: {API_ENDPOINT}")
    print(f"RAW_BUCKET: {RAW_BUCKET}")
    
    # Parse request - handle both direct dict and string-wrapped payloads
    if isinstance(event, str):
        event = json.loads(event)
    elif isinstance(event, dict) and 'body' in event:
        # API Gateway wrapped event
        event = json.loads(event['body'])
    
    replay_file = event.get('replay_file', 'replay_day_01.csv')
    speed_multiplier = float(event.get('speed_multiplier', 1.0))
    
    try:
        # Download CSV from S3
        print(f"Downloading {replay_file} from S3...")
        response = s3_client.get_object(Bucket=RAW_BUCKET, Key=replay_file)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(StringIO(csv_content))
        transactions = list(csv_reader)
        
        print(f"Loaded {len(transactions)} transactions")
        
        # Stream transactions to API
        successful = 0
        failed = 0
        
        api_url = f"{API_ENDPOINT}/api/transactions"
        
        for idx, txn_row in enumerate(transactions):
            # Convert CSV row to Transaction model format
            txn = {
                "txn_id": txn_row['txn_id'],
                "card_id": txn_row['card_id'],
                "merchant_id": txn_row['merchant_id'],
                "merchant_name": txn_row['merchant_name'],
                "mcc": txn_row['mcc'],
                "category": txn_row['category'],
                "amount": float(txn_row['amount']),
                "timestamp": txn_row['timestamp'],
                "ts": int(txn_row['ts']),
                "device_id": txn_row['device_id'],
                "geo": {
                    "lat": float(txn_row['geo_lat']),
                    "lon": float(txn_row['geo_lon']),
                    "city": txn_row['geo_city'],
                    "country": txn_row['geo_country']
                }
            }
            
            try:
                # Post to API
                response = requests.post(
                    api_url,
                    json=txn,
                    timeout=10
                )
                
                if response.status_code == 200:
                    successful += 1
                    result = response.json()
                    
                    if result.get('is_alert'):
                        print(f"🚨 Alert: {result['alert_id']} (score: {result['score']:.3f})")
                else:
                    failed += 1
                    print(f"❌ Failed: {response.status_code} - {response.text[:100]}")
            
            except Exception as e:
                failed += 1
                print(f"❌ Error posting transaction: {e}")
            
            # Rate limiting based on speed multiplier
            if idx % 100 == 0:
                print(f"Progress: {idx}/{len(transactions)} ({successful} successful, {failed} failed)")
            
            # Sleep to control replay speed
            if speed_multiplier < 100:  # Don't sleep for super fast replays
                time.sleep(0.01 / speed_multiplier)
        
        print(f"✅ Replay complete: {successful} successful, {failed} failed")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'completed',
                'total': len(transactions),
                'successful': successful,
                'failed': failed
            })
        }
    
    except Exception as e:
        print(f"❌ Replay failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'failed',
                'error': str(e)
            })
        }

