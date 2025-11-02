"""
WebSocket connection handler for real-time alerts
"""
import os
import boto3
import json
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')

CONNECTIONS_TABLE = os.environ.get('CONNECTIONS_TABLE', 'finguard-connections')


def handler(event, context):
    """
    Handle WebSocket connections
    """
    route_key = event.get('requestContext', {}).get('routeKey')
    connection_id = event.get('requestContext', {}).get('connectionId')
    
    connections_table = dynamodb.Table(CONNECTIONS_TABLE)
    
    if route_key == '$connect':
        # Store connection
        ttl = int((datetime.now() + timedelta(hours=2)).timestamp())
        
        connections_table.put_item(
            Item={
                'connectionId': connection_id,
                'ttl': ttl,
                'connected_at': int(datetime.now().timestamp())
            }
        )
        
        return {'statusCode': 200, 'body': 'Connected'}
    
    elif route_key == '$disconnect':
        # Remove connection
        connections_table.delete_item(
            Key={'connectionId': connection_id}
        )
        
        return {'statusCode': 200, 'body': 'Disconnected'}
    
    else:
        # Handle messages (if needed)
        return {'statusCode': 200, 'body': 'Message received'}

