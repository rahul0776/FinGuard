#!/bin/bash
# Get API Endpoints from CloudFormation Stack
# This script retrieves the VITE_API_URL and VITE_WS_URL values

echo "🔍 Retrieving API Endpoints from AWS..."
echo ""

STACK_NAME="finguard-stack"

# Get API Endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text 2>&1)

# Get WebSocket Endpoint
WS_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='WebSocketEndpoint'].OutputValue" \
    --output text 2>&1)

if [ $? -eq 0 ] && [ ! -z "$API_ENDPOINT" ] && [ ! -z "$WS_ENDPOINT" ]; then
    echo "================================="
    echo "✅ Found Endpoints!"
    echo "================================="
    echo ""
    echo "VITE_API_URL:"
    echo "  $API_ENDPOINT"
    echo ""
    echo "VITE_WS_URL:"
    echo "  $WS_ENDPOINT"
    echo ""
    echo "================================="
    echo "Copy these values for Vercel:"
    echo ""
    echo "VITE_API_URL = $API_ENDPOINT"
    echo "VITE_WS_URL = $WS_ENDPOINT"
else
    echo "❌ Stack not found or endpoints not available"
    echo ""
    echo "Please deploy your backend first:"
    echo "  ./scripts/deploy.sh"
fi

