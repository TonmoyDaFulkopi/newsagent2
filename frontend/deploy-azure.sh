#!/bin/bash

# Azure Static Web Apps Deployment Script
echo "🚀 Starting Azure deployment..."

# Build the application
echo "📦 Building the application..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Build output is in the 'out' directory"
    echo ""
    echo "🔗 To deploy to Azure Static Web Apps:"
    echo "1. Go to Azure Portal"
    echo "2. Create a new Static Web App"
    echo "3. Connect your GitHub repository"
    echo "4. Set build configuration:"
    echo "   - App location: /"
    echo "   - Output location: out"
    echo "5. Deploy!"
else
    echo "❌ Build failed!"
    exit 1
fi 