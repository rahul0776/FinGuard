"""
Synthetic data generator for FinGuard AI demo
Generates realistic merchants and fraudulent/legitimate transactions
"""
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import csv

# Merchant Category Codes with risk profiles
MCC_PROFILES = {
    "5411": {"category": "Grocery Stores", "risk": "LOW", "avg_amount": 75},
    "5812": {"category": "Restaurants", "risk": "LOW", "avg_amount": 45},
    "5541": {"category": "Gas Stations", "risk": "LOW", "avg_amount": 60},
    "5912": {"category": "Pharmacies", "risk": "LOW", "avg_amount": 35},
    "5311": {"category": "Department Stores", "risk": "MEDIUM", "avg_amount": 120},
    "5999": {"category": "Misc Retail", "risk": "MEDIUM", "avg_amount": 85},
    "5732": {"category": "Electronics", "risk": "HIGH", "avg_amount": 450},
    "7995": {"category": "Online Gaming", "risk": "HIGH", "avg_amount": 200},
    "5960": {"category": "Direct Marketing", "risk": "HIGH", "avg_amount": 180},
    "6211": {"category": "Securities", "risk": "HIGH", "avg_amount": 1500},
    "7273": {"category": "Dating Services", "risk": "HIGH", "avg_amount": 90},
    "5967": {"category": "Online Marketplaces", "risk": "MEDIUM", "avg_amount": 130},
}

# Geographic coordinates for major cities
CITIES = [
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "country": "US"},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "country": "US"},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "country": "US"},
    {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "country": "US"},
    {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740, "country": "US"},
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "GB"},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "country": "JP"},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "country": "IN"},
    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792, "country": "NG"},
    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333, "country": "BR"},
]

# Sample merchant names by category
MERCHANT_NAMES = {
    "Grocery Stores": ["FreshMart", "QuickStop Grocers", "GreenLeaf Market", "ValueSave", "FarmFresh"],
    "Restaurants": ["The Burger Joint", "Pizza Palace", "Sushi Express", "Taco Town", "Bistro 360"],
    "Gas Stations": ["SpeedFuel", "QuickGas", "Premium Petro", "FuelStop", "RoadRunner Gas"],
    "Pharmacies": ["HealthPlus Pharmacy", "MediCare Drugs", "Wellness Rx", "QuickMeds"],
    "Department Stores": ["MegaMart", "ShopSmart", "Value Center", "The Big Store"],
    "Misc Retail": ["Variety Shop", "Odds & Ends", "General Store", "Everything Plus"],
    "Electronics": ["TechZone", "Gadget Galaxy", "ElectroMart", "Digital Dreams"],
    "Online Gaming": ["GameVault", "PlayZone", "Virtual Arena", "eSports Hub"],
    "Direct Marketing": ["DirectDeal", "HomeShop Network", "TeleSale Plus"],
    "Securities": ["TradeFast Securities", "InvestPro", "StockMasters"],
    "Dating Services": ["LoveConnect", "MatchMaker Pro", "DateNow"],
    "Online Marketplaces": ["EZBuy", "QuickSell", "MarketPlace365"],
}


def generate_merchants(count=100):
    """Generate synthetic merchant data"""
    merchants = []
    merchant_id = 1000
    
    for _ in range(count):
        mcc = random.choice(list(MCC_PROFILES.keys()))
        profile = MCC_PROFILES[mcc]
        category = profile["category"]
        city = random.choice(CITIES)
        
        # Select merchant name
        names = MERCHANT_NAMES.get(category, ["Generic Store"])
        name = random.choice(names)
        if random.random() > 0.7:
            name = f"{name} - {city['name']}"
        
        merchant = {
            "merchant_id": f"MRCH-{merchant_id}",
            "name": name,
            "mcc": mcc,
            "category": category,
            "risk_level": profile["risk"],
            "avg_amount": profile["avg_amount"],
            "geo": {
                "lat": city["lat"] + random.uniform(-0.5, 0.5),
                "lon": city["lon"] + random.uniform(-0.5, 0.5),
                "city": city["name"],
                "country": city["country"]
            }
        }
        merchants.append(merchant)
        merchant_id += 1
    
    return merchants


def generate_card_profile():
    """Generate a synthetic cardholder profile"""
    card_id = f"CARD-{random.randint(1000000, 9999999)}"
    home_city = random.choice(CITIES)
    device_id = f"DEV-{random.randint(10000, 99999)}"
    
    return {
        "card_id": card_id,
        "home_geo": home_city,
        "device_id": device_id,
        "typical_merchants": [],
        "avg_daily_txns": random.randint(2, 8),
    }


def calculate_distance(geo1, geo2):
    """Calculate distance in km between two lat/lon points (Haversine)"""
    from math import radians, cos, sin, asin, sqrt
    
    lat1, lon1 = radians(geo1["lat"]), radians(geo1["lon"])
    lat2, lon2 = radians(geo2["lat"]), radians(geo2["lon"])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r


def generate_transactions(merchants, count=5000, fraud_rate=0.02):
    """Generate synthetic transactions with fraud patterns"""
    transactions = []
    cards = [generate_card_profile() for _ in range(count // 10)]  # ~10 txns per card
    
    txn_id = 100000
    start_time = datetime.now() - timedelta(hours=24)
    
    # Track recent transactions per card for velocity checks
    card_history = {card["card_id"]: [] for card in cards}
    
    for _ in range(count):
        card = random.choice(cards)
        merchant = random.choice(merchants)
        
        # Determine if this should be fraudulent
        is_fraud = random.random() < fraud_rate
        
        # Transaction timestamp
        ts = start_time + timedelta(seconds=random.randint(0, 86400))
        
        # Base transaction
        txn = {
            "txn_id": f"TXN-{txn_id}",
            "card_id": card["card_id"],
            "merchant_id": merchant["merchant_id"],
            "merchant_name": merchant["name"],
            "mcc": merchant["mcc"],
            "category": merchant["category"],
            "timestamp": ts.isoformat(),
            "ts": int(ts.timestamp()),
            "device_id": card["device_id"],
            "geo": merchant["geo"],
            "is_fraud": is_fraud
        }
        
        # Amount generation
        base_amount = merchant["avg_amount"]
        if is_fraud:
            # Fraudulent transactions often have unusual amounts
            if random.random() < 0.3:
                amount = random.randint(int(base_amount * 3), int(base_amount * 10))
            else:
                amount = random.randint(int(base_amount * 0.5), int(base_amount * 2))
        else:
            amount = random.normalvariate(base_amount, base_amount * 0.3)
            amount = max(1, int(amount))
        
        txn["amount"] = round(amount, 2)
        
        # Inject fraud patterns
        if is_fraud:
            fraud_type = random.choice(["velocity", "geo_jump", "high_risk_merchant", "device_mismatch"])
            
            if fraud_type == "velocity":
                # Multiple transactions in short time
                recent = card_history[card["card_id"]]
                if recent:
                    last_ts = datetime.fromisoformat(recent[-1]["timestamp"])
                    ts = last_ts + timedelta(seconds=random.randint(10, 120))
                    txn["timestamp"] = ts.isoformat()
                    txn["ts"] = int(ts.timestamp())
            
            elif fraud_type == "geo_jump":
                # Transaction far from home
                distant_city = random.choice([c for c in CITIES if c["name"] != card["home_geo"]["name"]])
                txn["geo"] = {
                    "lat": distant_city["lat"] + random.uniform(-0.5, 0.5),
                    "lon": distant_city["lon"] + random.uniform(-0.5, 0.5),
                    "city": distant_city["name"],
                    "country": distant_city["country"]
                }
            
            elif fraud_type == "high_risk_merchant":
                # Choose a high-risk merchant
                high_risk_merchants = [m for m in merchants if m["risk_level"] == "HIGH"]
                if high_risk_merchants:
                    merchant = random.choice(high_risk_merchants)
                    txn["merchant_id"] = merchant["merchant_id"]
                    txn["merchant_name"] = merchant["name"]
                    txn["mcc"] = merchant["mcc"]
            
            elif fraud_type == "device_mismatch":
                # Different device
                txn["device_id"] = f"DEV-{random.randint(10000, 99999)}"
        
        # Store in history
        card_history[card["card_id"]].append(txn)
        
        transactions.append(txn)
        txn_id += 1
    
    # Sort by timestamp
    transactions.sort(key=lambda x: x["ts"])
    
    return transactions


def save_merchants(merchants, output_dir):
    """Save merchants to JSON"""
    output_path = Path(output_dir) / "merchants.json"
    with open(output_path, 'w') as f:
        json.dump(merchants, f, indent=2)
    print(f"Generated {len(merchants)} merchants -> {output_path}")


def save_transactions(transactions, output_dir):
    """Save transactions to CSV for replay"""
    output_path = Path(output_dir) / "replay_day_01.csv"
    
    fieldnames = [
        "txn_id", "card_id", "merchant_id", "merchant_name", "mcc", "category",
        "amount", "timestamp", "ts", "device_id", 
        "geo_lat", "geo_lon", "geo_city", "geo_country", "is_fraud"
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for txn in transactions:
            row = {
                **{k: v for k, v in txn.items() if k != "geo"},
                "geo_lat": txn["geo"]["lat"],
                "geo_lon": txn["geo"]["lon"],
                "geo_city": txn["geo"]["city"],
                "geo_country": txn["geo"]["country"],
            }
            writer.writerow(row)
    
    fraud_count = sum(1 for t in transactions if t["is_fraud"])
    print(f"Generated {len(transactions)} transactions ({fraud_count} fraudulent) -> {output_path}")
    print(f"  Fraud rate: {fraud_count/len(transactions)*100:.2f}%")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data for FinGuard AI")
    parser.add_argument("--merchants", type=int, default=100, help="Number of merchants")
    parser.add_argument("--transactions", type=int, default=5000, help="Number of transactions")
    parser.add_argument("--fraud-rate", type=float, default=0.02, help="Fraud rate (0.02 = 2%)")
    parser.add_argument("--output", type=str, default="seed-data", help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    print("FinGuard AI - Data Generator")
    print("=" * 50)
    
    # Generate data
    print("\n1. Generating merchants...")
    merchants = generate_merchants(args.merchants)
    save_merchants(merchants, output_dir)
    
    print("\n2. Generating transactions...")
    transactions = generate_transactions(merchants, args.transactions, args.fraud_rate)
    save_transactions(transactions, output_dir)
    
    print("\n" + "=" * 50)
    print("Data generation complete!")
    print(f"Output directory: {output_dir.absolute()}")


if __name__ == "__main__":
    main()

