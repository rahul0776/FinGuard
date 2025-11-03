# Get API Endpoints from CloudFormation Stack
# This script retrieves the VITE_API_URL and VITE_WS_URL values

Write-Host "Retrieving API Endpoints from AWS..." -ForegroundColor Cyan
Write-Host ""

$STACK_NAME = "finguard-stack"

# Check if stack exists first
Write-Host "Checking if stack exists..." -ForegroundColor Yellow
$stackExists = aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].StackName" --output text 2>$null

if ($LASTEXITCODE -ne 0 -or $stackExists -eq $null) {
    Write-Host ""
    Write-Host "[ERROR] CloudFormation stack '$STACK_NAME' not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "The backend has not been deployed yet." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get the endpoints, you need to deploy your AWS backend first:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Run: .\scripts\deploy.ps1" -ForegroundColor White
    Write-Host "  2. Wait for deployment to complete" -ForegroundColor White
    Write-Host "  3. The endpoints will be displayed at the end of deployment" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run this script again after deployment." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Stack found: $stackExists" -ForegroundColor Green
Write-Host ""

# Get API Endpoint
Write-Host "Retrieving API endpoint..." -ForegroundColor Yellow
$API_ENDPOINT = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" `
    --output text 2>$null

# Get WebSocket Endpoint
Write-Host "Retrieving WebSocket endpoint..." -ForegroundColor Yellow
$WS_ENDPOINT = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --query "Stacks[0].Outputs[?OutputKey=='WebSocketEndpoint'].OutputValue" `
    --output text 2>$null

# Validate endpoints (should start with https:// or wss://)
$isValidApi = $API_ENDPOINT -and $API_ENDPOINT.StartsWith("https://")
$isValidWs = $WS_ENDPOINT -and $WS_ENDPOINT.StartsWith("wss://")

if ($isValidApi -and $isValidWs -and $LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "[OK] Found Endpoints!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "VITE_API_URL:" -ForegroundColor Yellow
    Write-Host "  $API_ENDPOINT" -ForegroundColor White
    Write-Host ""
    Write-Host "VITE_WS_URL:" -ForegroundColor Yellow
    Write-Host "  $WS_ENDPOINT" -ForegroundColor White
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "Copy these values for Vercel:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "VITE_API_URL = $API_ENDPOINT" -ForegroundColor White
    Write-Host "VITE_WS_URL = $WS_ENDPOINT" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Could not retrieve valid endpoints" -ForegroundColor Red
    Write-Host ""
    Write-Host "API Endpoint: $API_ENDPOINT" -ForegroundColor Yellow
    Write-Host "WebSocket Endpoint: $WS_ENDPOINT" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The stack exists but endpoints are not available." -ForegroundColor Yellow
    Write-Host "Check the CloudFormation console to verify the stack outputs." -ForegroundColor Cyan
}

