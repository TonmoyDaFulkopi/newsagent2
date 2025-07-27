# 🚀 Frontend Deployment with GitHub Actions

## Quick Setup

### 1. Create Azure Web App
```bash
# Create resource group
az group create --name rmg-news-rg --location "East US"

# Create App Service Plan (Free tier)
az appservice plan create --name "rmg-news-plan" --resource-group rmg-news-rg --sku F1 --is-linux

# Create Web App for frontend
az webapp create --name rmg-news-frontend --resource-group rmg-news-rg --plan "rmg-news-plan" --runtime "NODE|18-lts"
```

### 2. Get Publish Profile
```bash
# Download publish profile
az webapp deployment list-publishing-credentials --name rmg-news-frontend --resource-group rmg-news-rg --query publishingUserName --output tsv
```

### 3. Add GitHub Secret
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add new secret: `AZURE_WEBAPP_PUBLISH_PROFILE`
4. Paste the publish profile content

### 4. Deploy
Just push to `main` or `features` branch and the workflow will automatically deploy!

## What the Workflow Does
- ✅ Installs Node.js 18
- ✅ Installs dependencies
- ✅ Builds the Next.js app
- ✅ Deploys to Azure Web App

## Your App URL
After deployment: `https://rmg-news-frontend.azurewebsites.net` 