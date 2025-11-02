# FinGuard AI - Deployment Guide

Complete step-by-step guide to deploy FinGuard AI to AWS.

## Prerequisites

### 1. Install Required Tools

**AWS CLI** (if not installed):
```bash
# Windows (PowerShell)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify
aws --version
```

**AWS SAM CLI**:
```bash
# Windows (PowerShell)
pip install aws-sam-cli

# Verify
sam --version
```

**Python 3.12**:
- Already installed ✓

**Node.js 18+** (for frontend):
```bash
node --version
npm --version
```

### 2. Configure AWS Credentials

```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region: `us-east-1`
- Default output format: `json`

Verify:
```bash
aws sts get-caller-identity
```

## Deployment Steps

### Step 1: Generate Seed Data

```bash
cd seed-data
python generate.py --merchants 100 --transactions 5000
cd ..
```

Expected output: `merchants.json` and `replay_day_01.csv`

### Step 2: Train ML Model

```bash
cd ml
pip install -r requirements.txt
python train.py
cd ..
```

Expected output: `model.pkl`, `scaler.pkl`, `features.json` in `ml/` folder

### Step 3: Run Deployment Script

**Windows (PowerShell)**:
```powershell
.\scripts\deploy.ps1
```

**Linux/Mac (Bash)**:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

The script will:
1. ✓ Check prerequisites
2. ✓ Get AWS Account ID
3. ✓ Generate synthetic data
4. ✓ Train ML model
5. ✓ Create S3 buckets
6. ✓ Upload model to S3
7. ✓ Upload seed data to S3
8. ✓ Build SAM application
9. ✓ Deploy to AWS (~5-10 minutes)
10. ✓ Output endpoints

### Step 4: Seed DynamoDB

```bash
python scripts/seed-dynamodb.py
```

### Step 5: Configure Frontend

Create `frontend/.env`:
```env
VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
VITE_WS_URL=wss://your-ws-id.execute-api.us-east-1.amazonaws.com/Prod
```

(Use the endpoints from Step 3 output)

### Step 6: Build & Deploy Frontend

```bash
cd frontend
npm install
npm run build
```

**Deploy to Vercel** (recommended):
1. Push code to GitHub
2. Import repo to Vercel
3. Add environment variables
4. Deploy

**OR Deploy to S3 + CloudFront**:
```bash
aws s3 sync dist/ s3://your-frontend-bucket/
```

## Verification

### Test API
```bash
curl https://your-api-endpoint/Prod/health
```

Expected: `{"status":"healthy"}`

### Test Frontend
Open `http://localhost:3000` (dev) or your deployed URL

### Trigger Replay
1. Go to `/replay` page
2. Click "Replay Demo Day"
3. Watch alerts appear on `/demo` page

## Troubleshooting

### SAM Build Fails
```bash
cd infrastructure
sam build --use-container
```

### Lambda Import Errors
- Check `requirements.txt` in `api/` and `simulator/`
- Ensure Python 3.12 is used

### WebSocket Connection Fails
- Check CORS settings in `infrastructure/template.yaml`
- Verify `VITE_WS_URL` in frontend `.env`

### DynamoDB Access Denied
- Check IAM roles in SAM template
- Verify Lambda execution role has DynamoDB permissions

### Model Not Found
```bash
aws s3 ls s3://finguard-models-{account-id}/
```

Should show: `model.pkl`, `scaler.pkl`, `features.json`

## Cost Monitoring

### Set Up Billing Alerts

```bash
aws cloudwatch put-metric-alarm \
    --alarm-name finguard-cost-alert \
    --alarm-description "Alert if costs exceed $10" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold
```

### Check Current Costs

```bash
aws ce get-cost-and-usage \
    --time-period Start=2025-10-01,End=2025-10-31 \
    --granularity MONTHLY \
    --metrics BlendedCost
```

## Cleanup

To delete all resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name finguard-stack

# Delete S3 buckets
aws s3 rb s3://finguard-models-{account-id} --force
aws s3 rb s3://finguard-raw-{account-id} --force
aws s3 rb s3://finguard-reports-{account-id} --force
```

## Next Steps

- [ ] Add custom domain to API Gateway
- [ ] Set up CloudWatch dashboards
- [ ] Configure SNS alerts for high-risk transactions
- [ ] Add authentication for admin endpoints
- [ ] Integrate with Datadog/New Relic for monitoring
- [ ] Set up CI/CD with GitHub Actions

## Support

For issues:
1. Check CloudWatch Logs: `/aws/lambda/finguard-api`
2. Review SAM template: `infrastructure/template.yaml`
3. Test API directly with curl/Postman
4. Check AWS service quotas

---

**Happy Deploying! 🚀**



