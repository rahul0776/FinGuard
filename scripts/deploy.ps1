# FinGuard AI Deployment Script (PowerShell)
# Deploys the full stack to AWS using SAM CLI

Write-Host "FinGuard AWS Deployment" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "1. Checking prerequisites..." -ForegroundColor Yellow

$commands = @("aws", "sam", "python")
foreach ($cmd in $commands) {
    if (!(Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] $cmd is not installed" -ForegroundColor Red
        exit 1
    }
}
Write-Host "All prerequisites met" -ForegroundColor Green
Write-Host ""

# Get AWS Account ID
Write-Host "2. Getting AWS Account ID..." -ForegroundColor Yellow
$AWS_ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to get AWS Account ID. Is AWS CLI configured?" -ForegroundColor Red
    exit 1
}
Write-Host "AWS Account ID: $AWS_ACCOUNT_ID" -ForegroundColor Green
Write-Host ""

# Set variables
$REGION = "us-east-1"
$STACK_NAME = "finguard-stack"
$MODEL_BUCKET = "finguard-models-$AWS_ACCOUNT_ID"
$RAW_BUCKET = "finguard-raw-$AWS_ACCOUNT_ID"

# Generate seed data
Write-Host "3. Generating synthetic data..." -ForegroundColor Yellow
Set-Location seed-data
python generate.py --merchants 100 --transactions 5000
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Data generation failed" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Move generated files if generator created nested directory
$nestedDir = Join-Path "seed-data" "seed-data"
$replaySource = Join-Path $nestedDir "replay_day_01.csv"
$merchantsSource = Join-Path $nestedDir "merchants.json"
$replayTarget = Join-Path "seed-data" "replay_day_01.csv"
$merchantsTarget = Join-Path "seed-data" "merchants.json"

if (Test-Path $replaySource) {
    Move-Item -Force $replaySource $replayTarget
}

if (Test-Path $merchantsSource) {
    Move-Item -Force $merchantsSource $merchantsTarget
}

Write-Host "Seed data generated" -ForegroundColor Green
Write-Host ""

# Train ML model
Write-Host "4. Training model..." -ForegroundColor Yellow
Set-Location ml
python -m pip install -q -r requirements.txt
python train.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Model training failed" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host "Model training complete" -ForegroundColor Green
Write-Host ""

# Create S3 buckets
Write-Host "5. Creating S3 buckets..." -ForegroundColor Yellow
aws s3 mb "s3://$MODEL_BUCKET" --region $REGION 2>$null
aws s3 mb "s3://$RAW_BUCKET" --region $REGION 2>$null
Write-Host "S3 buckets ready" -ForegroundColor Green
Write-Host ""

# Upload model to S3
Write-Host "6. Uploading model artifacts to S3..." -ForegroundColor Yellow
aws s3 cp ml/model.pkl "s3://$MODEL_BUCKET/model.pkl"
aws s3 cp ml/scaler.pkl "s3://$MODEL_BUCKET/scaler.pkl"
aws s3 cp ml/features.json "s3://$MODEL_BUCKET/features.json"
Write-Host "Model artifacts uploaded" -ForegroundColor Green
Write-Host ""

# Upload seed data to S3
Write-Host "7. Uploading seed data to S3..." -ForegroundColor Yellow
aws s3 cp seed-data/replay_day_01.csv "s3://$RAW_BUCKET/replay_day_01.csv"
aws s3 cp seed-data/merchants.json "s3://$RAW_BUCKET/merchants.json"
Write-Host "Seed data uploaded" -ForegroundColor Green
Write-Host ""

# Build SAM application
Write-Host "8. Building SAM application..." -ForegroundColor Yellow
Set-Location infrastructure
sam build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] SAM build failed" -ForegroundColor Red
    exit 1
}
Write-Host "SAM build complete" -ForegroundColor Green
Write-Host ""

# Deploy SAM application
Write-Host "9. Deploying to AWS..." -ForegroundColor Yellow
sam deploy `
    --stack-name $STACK_NAME `
    --capabilities CAPABILITY_IAM `
    --region $REGION `
    --resolve-s3 `
    --no-confirm-changeset `
    --no-fail-on-empty-changeset
    
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] SAM deployment failed" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host "Stack deployment complete" -ForegroundColor Green
Write-Host ""

# Get outputs
Write-Host "10. Retrieving endpoints..." -ForegroundColor Yellow
$API_ENDPOINT = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" `
    --output text

$WS_ENDPOINT = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --query "Stacks[0].Outputs[?OutputKey=='WebSocketEndpoint'].OutputValue" `
    --output text

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Deployment Complete" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Endpoint:" -ForegroundColor Yellow
Write-Host "  $API_ENDPOINT" -ForegroundColor White
Write-Host ""
Write-Host "WebSocket Endpoint:" -ForegroundColor Yellow
Write-Host "  $WS_ENDPOINT" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update frontend/.env with these endpoints" -ForegroundColor White
Write-Host "  2. Deploy frontend: cd frontend ; npm run build" -ForegroundColor White
Write-Host "  3. Visit: $API_ENDPOINT" -ForegroundColor White
Write-Host ""
Write-Host "Seed merchants to DynamoDB:" -ForegroundColor Yellow
Write-Host "  python scripts/seed-dynamodb.py" -ForegroundColor White
Write-Host ""



