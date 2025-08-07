#!/bin/bash

# E-ink Pregnancy Tracker Auto-Update Script
# This script pulls the latest changes from GitHub and restarts the tracker

# Configuration
REPO_DIR="$HOME/e-ink-pregnancy-tracker"
LOG_FILE="$HOME/pregnancy-tracker-update.log"
BRANCH="master"
REPO_URL="https://github.com/foleykyle01/e-ink-pregnancy-tracker.git"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Start update process
log_message "Starting auto-update check..."

# Navigate to repository directory
cd "$REPO_DIR" || {
    log_message "ERROR: Could not navigate to $REPO_DIR"
    exit 1
}

# Store current commit hash
CURRENT_COMMIT=$(git rev-parse HEAD)

# Fetch latest changes
git fetch origin "$BRANCH" >> "$LOG_FILE" 2>&1

# Check if there are updates
UPSTREAM_COMMIT=$(git rev-parse origin/"$BRANCH")

if [ "$CURRENT_COMMIT" = "$UPSTREAM_COMMIT" ]; then
    log_message "No updates available. Current version is up to date."
else
    log_message "Updates found. Pulling changes..."
    
    # Pull the latest changes
    git pull origin "$BRANCH" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log_message "Successfully pulled updates from GitHub"
        
        # Check if requirements.txt has changed
        if git diff HEAD@{1} HEAD --name-only | grep -q "requirements.txt"; then
            log_message "requirements.txt changed. Installing new dependencies..."
            pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
        fi
        
        # Check if display_config.json has changed
        if git diff HEAD@{1} HEAD --name-only | grep -q "settings/display_config.json"; then
            log_message "display_config.json changed. Updating display cron jobs..."
            if [ -f "$REPO_DIR/manage_display_cron.sh" ]; then
                bash "$REPO_DIR/manage_display_cron.sh" >> "$LOG_FILE" 2>&1
                log_message "Display cron jobs updated based on new configuration"
            fi
        fi
        
        # Kill any existing pregnancy tracker process
        pkill -f "python.*main.py" 2>/dev/null
        
        # Wait a moment for process to fully terminate
        sleep 2
        
        # Run the updated tracker
        log_message "Starting updated pregnancy tracker..."
        cd "$REPO_DIR"
        sudo python3 main.py >> "$LOG_FILE" 2>&1 &
        
        log_message "Update complete. Tracker restarted with PID $!"
    else
        log_message "ERROR: Failed to pull updates from GitHub"
        exit 1
    fi
fi

log_message "Auto-update check completed"