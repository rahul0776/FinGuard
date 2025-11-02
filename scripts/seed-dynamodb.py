"""
Seed DynamoDB tables with initial data
"""
import json
import os
from decimal import Decimal
import boto3
from pathlib import Path

dynamodb = boto3.resource('dynamodb')


def _convert_to_decimal(value):
    """Recursively convert floats to Decimal for DynamoDB."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _convert_to_decimal(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_convert_to_decimal(v) for v in value]
    return value


def seed_merchants():
    """Seed merchants table"""
    table_name = os.environ.get('MERCHANTS_TABLE', 'finguard-merchants-finguard-main')
    table = dynamodb.Table(table_name)
    
    merchants_file = Path('seed-data/merchants.json')
    with open(merchants_file) as f:
        merchants = json.load(f)
    
    print(f"Seeding {len(merchants)} merchants...")
    
    with table.batch_writer() as batch:
        for merchant in merchants:
            item = {
                'PK': f"MRCH#{merchant['merchant_id']}",
                **_convert_to_decimal(merchant)
            }
            batch.put_item(Item=item)
    
    print(f"Seeded {len(merchants)} merchants")


def main():
    print("Seeding DynamoDB tables...")
    print("=" * 50)
    
    try:
        seed_merchants()
        print("\n" + "=" * 50)
        print("Seeding complete!")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

