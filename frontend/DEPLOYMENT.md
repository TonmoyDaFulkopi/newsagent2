# 🚀 Azure Deployment Guide

This guide will walk you through deploying your RMG News AI frontend to Azure.

## 📋 Prerequisites

- Azure account (free tier available)
- GitHub account
- Your code pushed to a GitHub repository

## 🎯 Deployment Options

### Option 1: Azure Static Web Apps (Recommended)

**Pros:**
- Free tier available
- Automatic deployments from GitHub
- Built-in CDN and global distribution
- Perfect for static sites

**Steps:**

#### 1. Prepare Your Repository
```bash
# Make sure your code is pushed to GitHub
git add .
git commit -m "Prepare for Azure deployment"
git push origin main
```

#### 2. Create Azure Static Web App

1. **Go to Azure Portal**: https://portal.azure.com
2. **Search for "Static Web Apps"**
3. **Click "Create"**
4. **Fill in the details:**
   - **Subscription**: Choose your subscription
   - **Resource Group**: Create new or use existing
   - **Name**: `rmg-news-ai-frontend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Hosting plan**: Free
   - **Source**: GitHub

#### 3. Connect GitHub Repository

1. **Click "Sign in with GitHub"**
2. **Authorize Azure**
3. **Select your repository**
4. **Select branch**: `main`

#### 4. Configure Build Settings

Set these build configuration values:
- **Build Preset**: Custom
- **App location**: `/`
- **API location**: (leave empty)
- **Output location**: `out`
- **App artifact location**: `out`

#### 5. Deploy

1. **Click "Review + Create"**
2. **Click "Create"**
3. **Wait for deployment** (usually 2-5 minutes)

#### 6. Access Your App

Once deployed, you'll get a URL like:
`https://your-app-name.azurestaticapps.net`

### Option 2: Azure App Service

**Pros:**
- Full server-side support
- More control over environment
- Better for complex applications

**Steps:**

#### 1. Build Your Application
```bash
npm run build
```

#### 2. Create Azure App Service

1. **Go to Azure Portal**
2. **Search for "App Services"**
3. **Click "Create"**
4. **Fill in details:**
   - **Name**: `rmg-news-ai-app`
   - **Runtime stack**: Node.js 18 LTS
   - **Operating System**: Linux
   - **Region**: Choose closest to users

#### 3. Deploy Using Azure CLI

```bash
# Install Azure CLI if not installed
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Create deployment package
npm run build
zip -r deploy.zip out/

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group your-resource-group \
  --name your-app-name \
  --src deploy.zip
```

### Option 3: Azure Container Instances

**Pros:**
- Container-based deployment
- Scalable
- Good for microservices

**Steps:**

#### 1. Create Dockerfile
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. Create nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
```

#### 3. Deploy to Azure Container Registry

```bash
# Build and push to ACR
az acr build --registry your-registry --image rmg-news-ai:latest .

# Deploy to Container Instances
az container create \
  --resource-group your-resource-group \
  --name rmg-news-ai-container \
  --image your-registry.azurecr.io/rmg-news-ai:latest \
  --dns-name-label rmg-news-ai \
  --ports 80
```

## 🔧 Environment Configuration

### Update API Endpoint

Before deploying, update your API endpoint in `src/app/api.ts`:

```typescript
// Change from localhost to your backend URL
const API_BASE_URL = 'https://your-backend-url.azurewebsites.net';
```

### Environment Variables

For Azure Static Web Apps, you can set environment variables in the Azure Portal:

1. **Go to your Static Web App**
2. **Click "Configuration"**
3. **Add application settings:**
   - `NEXT_PUBLIC_API_URL`: Your backend API URL

## 📊 Monitoring and Analytics

### Azure Application Insights

1. **Create Application Insights resource**
2. **Add to your Static Web App**
3. **Monitor performance and errors**

### Custom Domain

1. **Go to your Static Web App**
2. **Click "Custom domains"**
3. **Add your domain**
4. **Configure DNS records**

## 🔒 Security Considerations

### HTTPS
- Azure Static Web Apps provides HTTPS by default
- Custom domains also get automatic HTTPS

### CORS Configuration
Make sure your backend allows requests from your Azure domain.

## 💰 Cost Estimation

### Azure Static Web Apps (Free Tier)
- **Free**: 2 GB bandwidth/month
- **Standard**: $0.40/GB after free tier

### Azure App Service
- **Basic**: ~$13/month
- **Standard**: ~$73/month

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check GitHub Actions logs
   - Verify build configuration
   - Ensure all dependencies are in package.json

2. **API Connection Issues**
   - Verify CORS settings on backend
   - Check API URL configuration
   - Test API endpoints directly

3. **Styling Issues**
   - Ensure Tailwind CSS is properly built
   - Check for missing CSS imports

### Useful Commands

```bash
# Test build locally
npm run build

# Check build output
ls -la out/

# Test locally with static export
npx serve out/
```

## 📞 Support

- **Azure Documentation**: https://docs.microsoft.com/azure/static-web-apps/
- **Azure Support**: Available in Azure Portal
- **GitHub Issues**: For code-related problems

## 🎉 Success!

Once deployed, your RMG News AI frontend will be available at your Azure URL. The deployment will automatically update whenever you push changes to your main branch. 