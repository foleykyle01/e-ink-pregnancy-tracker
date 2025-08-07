#!/bin/bash

# Display Cron Manager for Pregnancy Tracker
# This script manages the display update cron jobs based on display_config.json

REPO_DIR="/home/pi/e-ink-pregnancy-tracker"
CONFIG_FILE="$REPO_DIR/settings/display_config.json"
LOG_FILE="/home/pi/display-cron.log"
CRON_IDENTIFIER="# PREGNANCY_TRACKER_DISPLAY"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if jq is installed for JSON parsing
if ! command -v jq &> /dev/null; then
    log_message "Installing jq for JSON parsing..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Navigate to repository directory
cd "$REPO_DIR" || {
    log_message "ERROR: Could not navigate to $REPO_DIR"
    exit 1
}

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    log_message "ERROR: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Read configuration
DISPLAY_ENABLED=$(jq -r '.display_update.enabled' "$CONFIG_FILE")
FREQUENCY_MINUTES=$(jq -r '.display_update.frequency_minutes' "$CONFIG_FILE")
SCREEN_SWITCH_ENABLED=$(jq -r '.screen_switching.enabled' "$CONFIG_FILE")
SCREEN_SWITCH_INTERVAL=$(jq -r '.screen_switching.switch_interval_minutes' "$CONFIG_FILE")
UPDATE_TYPE=$(jq -r '.update_schedule.type' "$CONFIG_FILE")

log_message "Reading display configuration..."
log_message "  Display updates: $DISPLAY_ENABLED (every $FREQUENCY_MINUTES minutes)"
log_message "  Screen switching: $SCREEN_SWITCH_ENABLED (every $SCREEN_SWITCH_INTERVAL minutes)"
log_message "  Update type: $UPDATE_TYPE"

# Function to remove existing display cron jobs
remove_existing_crons() {
    log_message "Removing existing display cron jobs..."
    # Remove lines with our identifier
    sudo crontab -l 2>/dev/null | grep -v "$CRON_IDENTIFIER" | sudo crontab -
}

# Function to add new cron job
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local description="$3"
    
    # Add the new cron job with identifier
    (sudo crontab -l 2>/dev/null; echo "$schedule $command $CRON_IDENTIFIER - $description") | sudo crontab -
    log_message "Added cron job: $description"
}

# Remove existing display-related cron jobs
remove_existing_crons

if [ "$DISPLAY_ENABLED" = "true" ]; then
    # Build the main display update command
    DISPLAY_CMD="cd $REPO_DIR && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1"
    
    if [ "$UPDATE_TYPE" = "interval" ]; then
        # Create interval-based cron schedule
        if [ "$FREQUENCY_MINUTES" -lt 60 ]; then
            # For intervals less than an hour
            CRON_SCHEDULE="*/$FREQUENCY_MINUTES * * * *"
        elif [ "$FREQUENCY_MINUTES" -eq 60 ]; then
            # Every hour
            CRON_SCHEDULE="0 * * * *"
        elif [ "$FREQUENCY_MINUTES" -eq 1440 ]; then
            # Once daily at 3 AM
            CRON_SCHEDULE="0 3 * * *"
        else
            # For other intervals, calculate hours
            HOURS=$((FREQUENCY_MINUTES / 60))
            if [ $((FREQUENCY_MINUTES % 60)) -eq 0 ]; then
                CRON_SCHEDULE="0 */$HOURS * * *"
            else
                # For non-standard intervals, use minutes
                CRON_SCHEDULE="*/$FREQUENCY_MINUTES * * * *"
            fi
        fi
        
        add_cron_job "$CRON_SCHEDULE" "$DISPLAY_CMD" "Display update every $FREQUENCY_MINUTES minutes"
        
    elif [ "$UPDATE_TYPE" = "custom" ]; then
        # Add custom time-based updates
        CUSTOM_TIMES=$(jq -r '.update_schedule.custom_times[]' "$CONFIG_FILE")
        
        for TIME in $CUSTOM_TIMES; do
            HOUR=$(echo "$TIME" | cut -d: -f1)
            MINUTE=$(echo "$TIME" | cut -d: -f2)
            CRON_SCHEDULE="$MINUTE $HOUR * * *"
            add_cron_job "$CRON_SCHEDULE" "$DISPLAY_CMD" "Display update at $TIME"
        done
    fi
    
    # Calculate optimal update frequency for screen switching
    if [ "$SCREEN_SWITCH_ENABLED" = "true" ]; then
        # Ensure we update at least twice per screen switch interval
        OPTIMAL_FREQUENCY=$((SCREEN_SWITCH_INTERVAL / 2))
        
        if [ "$FREQUENCY_MINUTES" -gt "$OPTIMAL_FREQUENCY" ]; then
            log_message "WARNING: Display updates every $FREQUENCY_MINUTES minutes may miss screen switches (recommended: $OPTIMAL_FREQUENCY minutes or less)"
        else
            log_message "Display update frequency is optimal for screen switching"
        fi
    fi
else
    log_message "Display updates are disabled in configuration"
fi

# Show current cron configuration
echo
log_message "Current display cron jobs:"
sudo crontab -l 2>/dev/null | grep "$CRON_IDENTIFIER" | while read -r line; do
    log_message "  $line"
done

# If no display crons found, show that
if ! sudo crontab -l 2>/dev/null | grep -q "$CRON_IDENTIFIER"; then
    log_message "  No display cron jobs configured"
fi

log_message "Display cron configuration complete!"