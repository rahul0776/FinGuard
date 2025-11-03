# Vercel Deployment Guide for FinGuard Frontend

This guide walks you through deploying the FinGuard frontend to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code must be in a Git repository (GitHub, GitLab, or Bitbucket)
3. **AWS Backend Deployed**: Ensure your AWS backend is deployed and you have:
   - API Gateway REST API endpoint URL
   - API Gateway WebSocket endpoint URL

## Step 1: Get Your AWS API Endpoints

**Important**: You must deploy your AWS backend first to get these endpoints.

After deploying your AWS backend (using `./scripts/deploy.sh` or `./scripts/deploy.ps1`), you'll see the endpoints printed at the end:

```
API Endpoint:
  https://abc123.execute-api.us-east-1.amazonaws.com/Prod

WebSocket Endpoint:
  wss://xyz789.execute-api.us-east-1.amazonaws.com/Prod
```

**These are your `VITE_API_URL` and `VITE_WS_URL` values.**

If you didn't save them, you can get them from:
- **AWS CloudFormation Console** → Your stack → Outputs tab
- Or run: `aws cloudformation describe-stacks --stack-name finguard-stack --query "Stacks[0].Outputs"`

**For detailed instructions, see [GET_ENDPOINTS.md](../../GET_ENDPOINTS.md) in the root directory.**

Save these URLs for Step 3.

## Step 2: Install Vercel CLI (Optional)

You can deploy via Vercel dashboard or CLI. For CLI deployment:

```bash
npm install -g vercel
```

## Step 3: Configure Environment Variables

You need to set two environment variables in Vercel:

- `VITE_API_URL`: Your AWS API Gateway REST endpoint
- `VITE_WS_URL`: Your AWS API Gateway WebSocket endpoint

### Option A: Via Vercel Dashboard

1. Go to your project in Vercel dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables:

   | Name | Value |
   |------|-------|
   | `VITE_API_URL` | `https://your-api.execute-api.us-east-1.amazonaws.com/Prod` |
   | `VITE_WS_URL` | `wss://your-ws.execute-api.us-east-1.amazonaws.com/Prod` |

4. Select **Production**, **Preview**, and **Development** environments
5. Click **Save**

### Option B: Via Vercel CLI

```bash
cd frontend
vercel env add VITE_API_URL production
# Paste your REST API URL when prompted

vercel env add VITE_WS_URL production
# Paste your WebSocket URL when prompted
```

## Step 4: Deploy to Vercel

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add Vercel configuration"
   git push origin main
   ```

2. **Import Project in Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click **Import Git Repository**
   - Select your repository
   - Click **Import**

3. **Configure Project**:
   - **Root Directory**: ⚠️ **IMPORTANT**: Set to `frontend` (this is the critical setting)
   - **Framework Preset**: Vercel should auto-detect Vite, or select "Vite"
   - **Build Command**: `npm run build` (auto-filled, should work if root directory is correct)
   - **Output Directory**: `dist` (auto-filled)
   - **Install Command**: `npm install` (auto-filled)
   
   **If you don't see Root Directory option**: Go to **Settings** → **General** → **Root Directory** and set it to `frontend`

4. **Add Environment Variables** (if not done in Step 3):
   - Add `VITE_API_URL` and `VITE_WS_URL` before deploying
   - Click **Add** for each variable

5. **Deploy**:
   - Click **Deploy**
   - Wait for build to complete (2-3 minutes)

### Option B: Deploy via Vercel CLI

```bash
cd frontend

# First deployment - will prompt for configuration
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N (for first deployment)
# - Project name: finguard-frontend
# - Directory: ./
# - Override settings? N
```

For subsequent deployments:

```bash
vercel --prod
```

## Step 5: Verify Deployment

After deployment:

1. **Check the deployment URL**: Vercel will provide a URL like `https://finguard-frontend.vercel.app`
2. **Test the application**:
   - Open the URL in your browser
   - Navigate to the dashboard
   - Check that WebSocket connection shows "Connected"
   - Try the "Replay Demo Day" feature

## Troubleshooting

### Issue: WebSocket shows "Disconnected"

**Solution**: 
- Verify `VITE_WS_URL` is set correctly in Vercel environment variables
- Ensure your WebSocket URL starts with `wss://` (secure WebSocket)
- Check CORS settings on your API Gateway WebSocket API

### Issue: API calls failing

**Solution**:
- Verify `VITE_API_URL` is set correctly
- Check that your API Gateway has CORS enabled
- Ensure the API endpoint is accessible (try opening it in browser)

### Issue: 404 errors on page refresh

**Solution**: 
- The `vercel.json` file includes rewrites for SPA routing
- Ensure `vercel.json` is in the `frontend/` directory
- Redeploy if you just added `vercel.json`

### Issue: Build fails - "Could not read package.json: ENOENT"

**Error**: `npm error enoent Could not read package.json: Error: ENOENT: no such file or directory`

**Solution**:
- **Root Directory not set**: This means Vercel is trying to build from the repository root instead of the `frontend/` directory
- Go to your Vercel project **Settings** → **General** → **Root Directory**
- Set it to `frontend` (without trailing slash)
- Save and redeploy

**If you can't find Root Directory setting**:
- Create a new deployment or reimport the project
- During setup, look for "Root Directory" or "Project Root" option
- Enter `frontend` as the value

### Issue: Build fails (other errors)

**Solution**:
- Check that all dependencies are in `package.json`
- Ensure Node.js version is compatible (Vercel uses Node 18+ by default)
- Check build logs in Vercel dashboard for specific errors
- Make sure you're deploying from the `main` or `master` branch

## Environment-Specific Deployments

Vercel supports three environments:

- **Production**: Main deployment (e.g., `finguard.vercel.app`)
- **Preview**: Automatic for each PR/branch
- **Development**: For local development

You can set different environment variables for each environment in Vercel dashboard.

## Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your custom domain (e.g., `finguard.example.com`)
3. Follow DNS configuration instructions
4. Wait for DNS propagation (can take up to 24 hours)

## Continuous Deployment

Once connected to Git:

- **Automatic deployments** on every push to `main` branch
- **Preview deployments** for pull requests
- **Rollback** to previous deployments with one click

## Monitoring

Vercel provides:
- **Analytics**: Page views, performance metrics
- **Logs**: Real-time function logs and build logs
- **Speed Insights**: Core Web Vitals and performance metrics

## Next Steps

After successful deployment:

1. Update your README.md with the live Vercel URL
2. Share the demo URL with stakeholders
3. Set up monitoring and alerts (optional)

---

**Deployment complete!** Your FinGuard frontend is now live on Vercel. 🎉

