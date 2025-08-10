#!/bin/bash
# Manual update script for the pregnancy tracker
# Run this to force an immediate update check

echo "======================================"
echo "  Manual Update - Pregnancy Tracker  "
echo "======================================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect the default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$DEFAULT_BRANCH" ]; then
    # Try to detect from available branches
    if git branch -r | grep -q "origin/main"; then
        DEFAULT_BRANCH="main"
    else
        DEFAULT_BRANCH="master"
    fi
fi

echo "📍 Current directory: $SCRIPT_DIR"
echo "🌿 Default branch: $DEFAULT_BRANCH"
echo ""

# Show current status
echo "📊 Current status:"
git status --short
echo ""

# Fetch latest from GitHub
echo "🔄 Fetching latest changes from GitHub..."
git fetch origin

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$DEFAULT_BRANCH)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Already up to date!"
else
    echo "📦 Updates available!"
    echo ""
    
    # Show what will be updated
    echo "Changes to be applied:"
    git log HEAD..origin/$DEFAULT_BRANCH --oneline
    echo ""
    
    # Stash any local changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "💾 Stashing local changes..."
        git stash
    fi
    
    # Pull updates
    echo "⬇️  Pulling updates..."
    git pull origin $DEFAULT_BRANCH
    
    if [ $? -eq 0 ]; then
        echo "✅ Updates applied successfully!"
        
        # Restart the service
        echo ""
        echo "🔄 Restarting tracker service..."
        sudo systemctl restart pregnancy-tracker-auto
        
        echo "✅ Service restarted!"
    else
        echo "❌ Update failed! Please check for conflicts."
        exit 1
    fi
fi

echo ""
echo "📊 Service status:"
sudo systemctl status pregnancy-tracker-auto --no-pager | head -n 5
echo ""
echo "💡 To view logs: sudo journalctl -u pregnancy-tracker-auto -f"