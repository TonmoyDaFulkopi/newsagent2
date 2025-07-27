# Azure Web App Deployment Script for Frontend
# Run this script to deploy the frontend to Azure

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$WebAppName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US"
)

Write-Host "🚀 Starting Frontend Deployment to Azure..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Create resource group if it doesn't exist
Write-Host "📦 Creating/Checking Resource Group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create App Service Plan (Free tier)
Write-Host "📋 Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create --name "$WebAppName-plan" --resource-group $ResourceGroupName --sku F1 --is-linux

# Create Web App
Write-Host "🌐 Creating Web App..." -ForegroundColor Yellow
az webapp create --name $WebAppName --resource-group $ResourceGroupName --plan "$WebAppName-plan" --runtime "NODE|18-lts"

# Configure Node.js version
Write-Host "⚙️ Configuring Node.js..." -ForegroundColor Yellow
az webapp config appsettings set --name $WebAppName --resource-group $ResourceGroupName --settings WEBSITE_NODE_DEFAULT_VERSION=18-lts

# Set environment variables
Write-Host "🔧 Setting Environment Variables..." -ForegroundColor Yellow
az webapp config appsettings set --name $WebAppName --resource-group $ResourceGroupName --settings NODE_ENV=production

# Deploy the frontend code
Write-Host "📤 Deploying Frontend Code..." -ForegroundColor Yellow
az webapp deployment source config-local-git --name $WebAppName --resource-group $ResourceGroupName

# Get the deployment URL
$deploymentUrl = az webapp deployment list-publishing-credentials --name $WebAppName --resource-group $ResourceGroupName --query publishingUserName --output tsv

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your app is available at: https://$WebAppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📝 Deployment URL: $deploymentUrl" -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update the API URL in your frontend code to point to your backend" -ForegroundColor White
Write-Host "2. Deploy your backend to Azure" -ForegroundColor White
Write-Host "3. Configure CORS settings in your backend" -ForegroundColor White 