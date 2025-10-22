#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🚀 Video Downloader - Auto Deploy Script              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this from the downloader folder."
    exit 1
fi

echo "📦 Project found in: $(pwd)"
echo ""

# Option menu
echo "Choose deployment platform:"
echo ""
echo "1) 🟢 Render.com (Recommended - Free & Always On)"
echo "2) 🚂 Railway.app (Fast & Free)"
echo "3) 🔵 Heroku (Classic)"
echo "4) 📋 Show manual instructions"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🟢 Deploying to Render.com..."
        echo ""
        echo "Opening Render.com in your browser..."
        open "https://render.com/deploy"
        echo ""
        echo "📝 Follow these steps:"
        echo "1. Sign up/Login to Render"
        echo "2. Click 'New +' → 'Web Service'"
        echo "3. Upload this folder: $(pwd)"
        echo "4. Use these settings:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn app:app"
        echo "5. Click 'Create Web Service'"
        echo ""
        echo "✅ Your app will be live in 2-3 minutes!"
        ;;
    2)
        echo ""
        echo "🚂 Deploying to Railway.app..."
        echo ""
        echo "Opening Railway.app in your browser..."
        open "https://railway.app/new"
        echo ""
        echo "📝 Follow these steps:"
        echo "1. Login to Railway"
        echo "2. Click 'Deploy from GitHub' or 'Deploy from local'"
        echo "3. Select this folder: $(pwd)"
        echo "4. Railway will auto-detect and deploy!"
        echo ""
        echo "✅ Your app will be live in 1-2 minutes!"
        ;;
    3)
        echo ""
        echo "🔵 Deploying to Heroku..."
        echo ""
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "Installing Heroku CLI..."
            brew tap heroku/brew && brew install heroku
        fi
        
        echo "Logging into Heroku..."
        heroku login
        
        echo "Creating Heroku app..."
        heroku create video-downloader-$(date +%s)
        
        echo "Deploying..."
        git push heroku master
        
        echo ""
        echo "✅ Deployment complete!"
        heroku open
        ;;
    4)
        echo ""
        echo "📋 Manual Deployment Instructions"
        echo ""
        echo "See DEPLOY_NOW.md for detailed instructions"
        open "DEPLOY_NOW.md"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 Deployment Started!                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
