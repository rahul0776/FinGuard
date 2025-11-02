# 🚀 FinGuard AI - Quick Start

## ✅ What's Complete

Your **complete FinGuard AI project** is ready:

- ✅ **Backend API** (FastAPI on AWS Lambda)
- ✅ **Frontend Dashboard** (React + Vite)
- ✅ **ML Model** (RandomForest + SHAP)
- ✅ **Transaction Simulator** (AWS Lambda)
- ✅ **Infrastructure** (AWS SAM templates)
- ✅ **Deployment Scripts** (PowerShell & Bash)
- ✅ **Documentation** (README, guides)

## ⚠️ Before Deployment

You need to install 2 tools:

### 1. Install AWS SAM CLI
```powershell
pip install aws-sam-cli
```

### 2. Configure AWS Credentials
```powershell
aws configure
```

Enter your AWS Access Key ID and Secret Access Key.

**Don't have AWS keys?** See [SETUP.md](SETUP.md) for instructions.

## 🎯 Deploy in 3 Commands

Once AWS tools are configured:

```powershell
# 1. Generate data & train model
python seed-data/generate.py
python ml/train.py

# 2. Deploy to AWS (10-15 minutes)
.\scripts\deploy.ps1

# 3. Test your API
curl https://your-api-endpoint/Prod/health
```

## 📁 Project Structure

```
FinGuard/
├── 📄 README.md              ← Start here (project overview)
├── 📄 SETUP.md               ← Prerequisites & AWS setup
├── 📄 DEPLOYMENT_GUIDE.md    ← Detailed deployment steps
├── 📄 QUICKSTART.md          ← You are here
│
├── 🔧 api/                   ← FastAPI backend
│   ├── main.py              (Lambda handler with Mangum)
│   ├── scoring.py           (ML + rules engine)
│   ├── websocket.py         (Real-time alerts)
│   ├── reports.py           (PDF generation)
│   └── requirements.txt
│
├── 🎨 frontend/              ← React dashboard
│   ├── src/
│   │   ├── pages/           (Dashboard, AlertDetail, Replay)
│   │   ├── components/      (KPICard, AlertCard, Navbar)
│   │   └── hooks/           (useWebSocket)
│   ├── package.json
│   └── vite.config.ts
│
├── 🤖 ml/                    ← ML model training
│   ├── train.py             (RandomForest + SHAP)
│   └── requirements.txt
│
├── 🔄 simulator/             ← Transaction replay
│   ├── handler.py
│   └── requirements.txt
│
├── ☁️ infrastructure/        ← AWS SAM
│   └── template.yaml        (DynamoDB, S3, Lambda, API Gateway)
│
├── 📊 seed-data/             ← Synthetic data
│   └── generate.py          (5K transactions, 100 merchants)
│
└── 🚀 scripts/               ← Deployment automation
    ├── deploy.ps1           (Windows)
    ├── deploy.sh            (Linux/Mac)
    └── seed-dynamodb.py     (Initialize DB)
```

## 🎬 Demo Features

### Live Dashboard (`/demo`)
- Real-time transaction stream
- Fraud alerts with WebSocket
- KPI metrics (transactions, alerts, latency)
- Alert table with risk levels

### Alert Deep Dive (`/case/:alertId`)
- Transaction details
- Fraud score breakdown
- Triggered rules
- SHAP feature contributions (bar chart)
- PDF report download

### Replay Control (`/replay`)
- Stream 5K synthetic transactions
- Watch fraud detection in real-time

## 📊 Tech Stack

**Backend**:
- FastAPI 0.109
- AWS Lambda (Python 3.12)
- DynamoDB (pay-per-request)
- S3 (model & data storage)
- API Gateway (REST + WebSocket)

**Frontend**:
- React 18
- Vite 5
- TypeScript
- Tailwind CSS
- Recharts (data viz)

**ML**:
- scikit-learn 1.3
- SHAP 0.44
- RandomForest (50 trees)
- <150ms inference

**Infrastructure**:
- AWS SAM
- CloudFormation
- IAM roles (least-privilege)

## 💰 Costs

**Free Tier (12 months)**:
- **$0/month** for demo usage
- Stays within AWS Free Tier limits

**After Free Tier**:
- Lambda: ~$5/month
- DynamoDB: ~$5/month
- S3: ~$1/month
- API Gateway: ~$3/month

**Total**: ~$15/month for production-level traffic

## 🔒 Security Features

- ✅ Synthetic data only (no PII)
- ✅ Read-only public endpoints
- ✅ Signed webhooks for admin actions
- ✅ CORS restricted
- ✅ Least-privilege IAM roles
- ✅ Presigned S3 URLs (5-min expiry)

## 📖 Documentation

| File | Purpose |
|------|---------|
| **README.md** | Project overview, features, architecture |
| **SETUP.md** | Install prerequisites, get AWS keys |
| **DEPLOYMENT_GUIDE.md** | Step-by-step deployment |
| **QUICKSTART.md** | This file - get started fast |

## 🛠️ Immediate Next Steps

1. **Read SETUP.md** - Install AWS tools
2. **Run deploy script** - `.\scripts\deploy.ps1`
3. **Test the API** - Visit your endpoint
4. **Deploy frontend** - Vercel or S3
5. **Share your demo** - Add to resume/portfolio!

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Serverless architecture (Lambda, API Gateway)
- ✅ Real-time systems (WebSockets)
- ✅ ML inference at scale (<150ms)
- ✅ Explainable AI (SHAP)
- ✅ Full-stack development (FastAPI + React)
- ✅ Infrastructure as Code (SAM/CloudFormation)
- ✅ Cloud cost optimization (Free Tier)

## 🚨 Troubleshooting

**"Unable to locate credentials"**
→ Run `aws configure` and enter your AWS Access Key

**"SAM CLI not found"**
→ Run `pip install aws-sam-cli`

**"Access Denied"**
→ Check IAM permissions (see SETUP.md)

**Questions?**
→ Check DEPLOYMENT_GUIDE.md for detailed solutions

---

## 🎉 Ready to Deploy?

1. Install prerequisites: See [SETUP.md](SETUP.md)
2. Deploy: `.\scripts\deploy.ps1`
3. Done! 🚀

**Questions or issues?** Check the detailed guides above.

---

**Built with ❤️ for your portfolio • MIT License • Free to use**



