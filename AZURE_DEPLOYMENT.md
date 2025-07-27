# 🚀 Azure Web App Deployment Guide

## Frontend Deployment

### Prerequisites
1. **Azure CLI** installed on your machine
2. **Azure Account** with active subscription
3. **Git** installed

### Step 1: Install Azure CLI
```bash
# Windows (using winget)
winget install Microsoft.AzureCLI

# Or download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

### Step 2: Login to Azure
```bash
az login
```

### Step 3: Deploy Frontend

#### Option A: Using PowerShell Script (Recommended)
```powershell
# Run the deployment script
.\deploy-frontend.ps1 -ResourceGroupName "rmg-news-rg" -WebAppName "rmg-news-frontend" -Location "East US"
```

#### Option B: Manual Deployment
```bash
# Create resource group
az group create --name rmg-news-rg --location "East US"

# Create App Service Plan (Free tier)
az appservice plan create --name "rmg-news-plan" --resource-group rmg-news-rg --sku F1 --is-linux

# Create Web App
az webapp create --name rmg-news-frontend --resource-group rmg-news-rg --plan "rmg-news-plan" --runtime "NODE|18-lts"

# Configure Node.js
az webapp config appsettings set --name rmg-news-frontend --resource-group rmg-news-rg --settings WEBSITE_NODE_DEFAULT_VERSION=18-lts

# Set environment variables
az webapp config appsettings set --name rmg-news-frontend --resource-group rmg-news-rg --settings NODE_ENV=production

# Deploy from local git
az webapp deployment source config-local-git --name rmg-news-frontend --resource-group rmg-news-rg
```

### Step 4: Deploy Code
```bash
# Navigate to frontend directory
cd frontend

# Initialize git if not already done
git init
git add .
git commit -m "Initial frontend deployment"

# Add Azure remote
az webapp deployment source config-local-git --name rmg-news-frontend --resource-group rmg-news-rg

# Push to Azure
git push azure master
```

## Backend Deployment (Next Step)

After frontend is deployed, you'll need to:

1. **Create another Web App** for the backend
2. **Configure Python runtime**
3. **Set up database** (Azure Database for PostgreSQL)
4. **Configure environment variables**
5. **Update frontend API URL**

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.azurewebsites.net
```

### Backend (Azure App Settings)
```env
DATABASE_URL=postgresql://user:password@host:port/database
DEEPSEEK_API_KEY=your_deepseek_api_key
NODE_ENV=production
```

## Troubleshooting

### Common Issues:
1. **Build fails**: Check Node.js version compatibility
2. **Runtime errors**: Verify environment variables
3. **CORS issues**: Configure backend CORS settings
4. **Database connection**: Check connection strings

### Useful Commands:
```bash
# View logs
az webapp log tail --name rmg-news-frontend --resource-group rmg-news-rg

# Restart app
az webapp restart --name rmg-news-frontend --resource-group rmg-news-rg

# View app settings
az webapp config appsettings list --name rmg-news-frontend --resource-group rmg-news-rg
```

## Cost Optimization

- **Free Tier**: Use F1 App Service Plan (limited but free)
- **Database**: Start with Azure Database for PostgreSQL Basic tier
- **Monitoring**: Use Azure Application Insights (free tier available)

## Security

1. **Environment Variables**: Store secrets in Azure App Settings
2. **HTTPS**: Enabled by default on Azure Web Apps
3. **CORS**: Configure properly for production
4. **API Keys**: Never commit to repository 