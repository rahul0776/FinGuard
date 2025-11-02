#!/bin/bash
# FinGuard AI Deployment Script (Bash)
# Deploys the full stack to AWS using SAM CLI

set -e

echo "🏦 FinGuard AI - AWS Deployment"
echo "================================="
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
for cmd in aws sam python; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ Error: $cmd is not installed"
        exit 1
    fi
done
echo "✓ All prerequisites met"
echo ""

# Get AWS Account ID
echo "2. Getting AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to get AWS Account ID. Is AWS CLI configured?"
    exit 1
fi
echo "✓ AWS Account ID: $AWS_ACCOUNT_ID"
echo ""

# Set variables
REGION="us-east-1"
STACK_NAME="finguard-stack"
MODEL_BUCKET="finguard-models-$AWS_ACCOUNT_ID"
RAW_BUCKET="finguard-raw-$AWS_ACCOUNT_ID"

# Generate seed data
echo "3. Generating synthetic data..."
cd seed-data
python generate.py --merchants 100 --transactions 5000
cd ..
echo "✓ Seed data generated"
echo ""

# Train ML model
echo "4. Training ML model..."
cd ml
pip install -q -r requirements.txt
python train.py
cd ..
echo "✓ Model trained"
echo ""

# Create S3 buckets
echo "5. Creating S3 buckets..."
aws s3 mb "s3://$MODEL_BUCKET" --region $REGION 2>/dev/null || true
aws s3 mb "s3://$RAW_BUCKET" --region $REGION 2>/dev/null || true
echo "✓ S3 buckets ready"
echo ""

# Upload model to S3
echo "6. Uploading ML model to S3..."
aws s3 cp ml/model.pkl "s3://$MODEL_BUCKET/model.pkl"
aws s3 cp ml/scaler.pkl "s3://$MODEL_BUCKET/scaler.pkl"
aws s3 cp ml/features.json "s3://$MODEL_BUCKET/features.json"
echo "✓ Model uploaded"
echo ""

# Upload seed data to S3
echo "7. Uploading seed data to S3..."
aws s3 cp seed-data/replay_day_01.csv "s3://$RAW_BUCKET/replay_day_01.csv"
aws s3 cp seed-data/merchants.json "s3://$RAW_BUCKET/merchants.json"
echo "✓ Seed data uploaded"
echo ""

# Build SAM application
echo "8. Building SAM application..."
cd infrastructure
sam build
cd ..
echo "✓ SAM build complete"
echo ""

# Deploy SAM application
echo "9. Deploying to AWS..."
cd infrastructure
sam deploy \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset
cd ..
echo "✓ Stack deployed"
echo ""

# Get outputs
echo "10. Retrieving endpoints..."
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)

WS_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='WebSocketEndpoint'].OutputValue" \
    --output text)

echo ""
echo "================================="
echo "✅ Deployment Complete!"
echo "================================="
echo ""
echo "API Endpoint:"
echo "  $API_ENDPOINT"
echo ""
echo "WebSocket Endpoint:"
echo "  $WS_ENDPOINT"
echo ""
echo "Next Steps:"
echo "  1. Update frontend/.env with these endpoints"
echo "  2. Deploy frontend: cd frontend && npm run build"
echo "  3. Visit: $API_ENDPOINT"
echo ""
echo "💡 Seed merchants to DynamoDB:"
echo "  python scripts/seed-dynamodb.py"
echo ""



