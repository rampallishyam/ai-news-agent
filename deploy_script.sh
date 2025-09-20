#!/bin/bash

# AI News Agent - Quick Deployment Script
# This script helps you quickly set up and deploy your AI News Agent

echo "🤖 AI News Agent - Quick Deploy"
echo "================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ This doesn't appear to be a git repository."
    echo "Please run this script from your cloned repository directory."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Git repository detected"
echo "✅ Python 3 is available"

# Generate all repository files
echo ""
echo "📁 Generating repository files..."
python3 generate_repo.py

if [ $? -eq 0 ]; then
    echo "✅ Repository files generated successfully!"
else
    echo "❌ Failed to generate repository files"
    exit 1
fi

# Install dependencies for testing
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Git add and commit
echo ""
echo "📝 Adding files to git..."
git add .
git commit -m "🚀 Initial AI News Agent setup

- Added GitHub Actions workflow for daily automation
- Implemented news collection from 6 AI sources  
- Integrated Claude API for intelligent summarization
- Added Notion API integration for page updates
- Included comprehensive error handling and logging
- Added setup and deployment scripts

Ready for production deployment!"

echo "✅ Files committed to git"

# Check if we have a remote
if git remote -v | grep -q origin; then
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push origin main || git push origin master
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to GitHub!"
        echo ""
        echo "🎉 DEPLOYMENT COMPLETE!"
        echo "======================"
        echo ""
        echo "Next steps:"
        echo "1. 🔐 Add your API keys to GitHub Secrets:"
        echo "   - Go to your repo → Settings → Secrets and variables → Actions"
        echo "   - Add: ANTHROPIC_API_KEY, NOTION_TOKEN, NOTION_PAGE_ID"
        echo ""
        echo "2. ⏰ Enable GitHub Actions:"
        echo "   - Go to Actions tab and enable workflows"
        echo "   - The agent will run daily at 8 AM UTC"
        echo ""
        echo "3. 🧪 Test manually:"
        echo "   - Go to Actions → Daily AI News Update → Run workflow"
        echo ""
        echo "4. 📱 Check your Notion page for updates!"
        echo ""
        echo "📚 For detailed setup instructions, see README.md"
        echo ""
        echo "🎯 Your AI News Agent is now deployed and ready!"
    else
        echo "❌ Failed to push to GitHub"
        echo "Please check your git configuration and try: git push"
    fi
else
    echo ""
    echo "⚠️  No git remote found."
    echo "Please add your GitHub repository as remote:"
    echo "git remote add origin https://github.com/yourusername/ai-news-agent.git"
    echo "Then run: git push -u origin main"
fi

echo ""
echo "🤖 AI News Agent deployment script completed!"
