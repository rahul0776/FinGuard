# FinGuard AI - Setup Instructions

## Current Status

✅ **Project Structure Created**
✅ **All Code Complete** (API, Frontend, ML, Simulator)
✅ **Deployment Scripts Ready**

⚠️ **Action Required**: Install AWS tools & configure credentials

## Prerequisites to Install

### 1. AWS SAM CLI (Required for deployment)

**Install via pip**:
```powershell
pip install aws-sam-cli
```

**Verify installation**:
```powershell
sam --version
```

Expected output: `SAM CLI, version 1.x.x`

### 2. AWS CLI Configuration (Required)

You already have AWS CLI installed. Now configure it:

```powershell
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security Credentials
- **AWS Secret Access Key**: Same location
- **Default region name**: Enter `us-east-1`
- **Default output format**: Enter `json`

**Verify configuration**:
```powershell
aws sts get-caller-identity
```

Should show your AWS Account ID and user info.

### 3. Python Dependencies

Install required packages:
```powershell
pip install boto3 aws-sam-cli
```

## Quick Start Guide

Once AWS tools are configured, run:

### Option 1: Automated Deployment (Recommended)

```powershell
.\scripts\deploy.ps1
```

This will:
1. Generate synthetic data
2. Train the ML model
3. Create S3 buckets
4. Upload model and data
5. Deploy all AWS resources
6. Output your API endpoints

**Duration**: ~10-15 minutes

### Option 2: Step-by-Step Deployment

#### Step 1: Generate Seed Data
```powershell
cd seed-data
python generate.py --merchants 100 --transactions 5000
cd ..
```

#### Step 2: Train ML Model
```powershell
cd ml
pip install -r requirements.txt
python train.py
cd ..
```

#### Step 3: Deploy Infrastructure
```powershell
cd infrastructure
sam build
sam deploy --guided
cd ..
```

Follow the prompts:
- Stack name: `finguard-stack`
- AWS Region: `us-east-1`
- Confirm changes: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Save arguments to config: `Y`

#### Step 4: Upload Model & Data
```powershell
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
aws s3 cp ml/model.pkl "s3://finguard-models-$ACCOUNT_ID/model.pkl"
aws s3 cp ml/scaler.pkl "s3://finguard-models-$ACCOUNT_ID/scaler.pkl"
aws s3 cp ml/features.json "s3://finguard-models-$ACCOUNT_ID/features.json"
aws s3 cp seed-data/replay_day_01.csv "s3://finguard-raw-$ACCOUNT_ID/replay_day_01.csv"
```

#### Step 5: Seed Database
```powershell
python scripts/seed-dynamodb.py
```

#### Step 6: Setup Frontend
```powershell
cd frontend
npm install

# Create .env file with your API endpoints
"VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod" | Out-File .env -Encoding UTF8
"VITE_WS_URL=wss://your-ws-id.execute-api.us-east-1.amazonaws.com/Prod" | Out-File .env -Append -Encoding UTF8

# Run locally
npm run dev
```

Visit `http://localhost:3000`

## Getting AWS Access Keys

1. **Log into AWS Console**: https://console.aws.amazon.com
2. **Navigate to IAM**:
   - Search for "IAM" in the search bar
   - Click "IAM" (Identity and Access Management)
3. **Create Access Key**:
   - Click "Users" in left sidebar
   - Click your username (or create a new user)
   - Click "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Choose "CLI" as use case
   - Download the `.csv` file with credentials

**Important**: Save these credentials securely. They won't be shown again.

## Estimated AWS Costs

With **AWS Free Tier**, you'll pay:
- **$0/month** for demo usage (within limits)
- **$0-5/month** if you share widely

### Free Tier Limits (12 months):
- Lambda: 1M requests/month
- DynamoDB: 25GB storage + 25 RCU/WCU
- S3: 5GB storage
- API Gateway: 1M requests/month

### Always Free:
- Lambda: 400K GB-seconds compute
- DynamoDB: 25GB storage forever

## Troubleshooting

### "Unable to locate credentials"
Run: `aws configure` and enter your Access Key and Secret Key

### "SAM CLI not found"
Run: `pip install aws-sam-cli`

### "Access Denied" errors
Check that your IAM user has these permissions:
- CloudFormation (full)
- Lambda (full)
- DynamoDB (full)
- S3 (full)
- API Gateway (full)
- IAM (create roles)

Attach these managed policies to your IAM user:
- `AdministratorAccess` (for demo/testing)
- OR create custom policy with specific permissions

### Python not found
Make sure Python 3.12 is in your PATH:
```powershell
python --version
```

### Port 3000 already in use
Frontend dev server:
```powershell
npm run dev -- --port 3001
```

## Project Structure

```
FinGuard/
├── api/                  ✅ FastAPI backend (Lambda)
├── frontend/             ✅ React dashboard
├── simulator/            ✅ Transaction replay Lambda
├── ml/                   ✅ ML model training
├── infrastructure/       ✅ AWS SAM templates
├── scripts/              ✅ Deployment automation
├── seed-data/           ✅ Synthetic data generators
├── README.md            ✅ Project overview
├── DEPLOYMENT_GUIDE.md  ✅ Detailed deployment steps
└── SETUP.md             📍 You are here
```

## Next Steps

1. ✅ Install AWS SAM CLI: `pip install aws-sam-cli`
2. ✅ Configure AWS: `aws configure`
3. ✅ Run deployment: `.\scripts\deploy.ps1`
4. ✅ Test the demo: Open your API endpoint in browser
5. ✅ Deploy frontend to Vercel (optional)

## Need Help?

Check the detailed guides:
- **README.md** - Project overview and features
- **DEPLOYMENT_GUIDE.md** - Complete deployment walkthrough
- **AWS Documentation** - https://docs.aws.amazon.com

---

**Ready to deploy?** Install the prerequisites above, then run `.\scripts\deploy.ps1`



