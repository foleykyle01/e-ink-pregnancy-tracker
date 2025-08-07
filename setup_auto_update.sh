#!/bin/bash

# Setup script for auto-update cron job
# Run this on the Raspberry Pi to configure automatic updates

echo "E-ink Pregnancy Tracker Auto-Update Setup"
echo "=========================================="
echo

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Warning: This doesn't appear to be a Raspberry Pi."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the repository directory - auto-detect current directory
DEFAULT_DIR="$(pwd)"
if [ ! -d ".git" ]; then
    # If not in a git repo, try common locations
    DEFAULT_DIR="$HOME/e-ink-pregnancy-tracker"
fi
read -p "Enter the repository directory [$DEFAULT_DIR]: " REPO_DIR
REPO_DIR="${REPO_DIR:-$DEFAULT_DIR}"

# Verify directory exists
if [ ! -d "$REPO_DIR" ]; then
    echo "Error: Directory $REPO_DIR does not exist!"
    exit 1
fi

# Update the auto_update.sh script with correct path
sed -i "s|REPO_DIR=\".*\"|REPO_DIR=\"$REPO_DIR\"|" "$REPO_DIR/auto_update.sh"

# Make sure the script is executable
chmod +x "$REPO_DIR/auto_update.sh"

echo
echo "Choose update frequency:"
echo "1) Every hour"
echo "2) Every 6 hours" 
echo "3) Every 12 hours"
echo "4) Once daily (at 3 AM)"
echo "5) Twice daily (3 AM and 3 PM)"
echo "6) Custom"
read -p "Select option (1-6): " FREQ_OPTION

case $FREQ_OPTION in
    1)
        CRON_SCHEDULE="0 * * * *"
        FREQ_DESC="every hour"
        ;;
    2)
        CRON_SCHEDULE="0 */6 * * *"
        FREQ_DESC="every 6 hours"
        ;;
    3)
        CRON_SCHEDULE="0 */12 * * *"
        FREQ_DESC="every 12 hours"
        ;;
    4)
        CRON_SCHEDULE="0 3 * * *"
        FREQ_DESC="daily at 3 AM"
        ;;
    5)
        CRON_SCHEDULE="0 3,15 * * *"
        FREQ_DESC="twice daily at 3 AM and 3 PM"
        ;;
    6)
        echo "Enter custom cron schedule (e.g., '0 */4 * * *' for every 4 hours):"
        read CRON_SCHEDULE
        FREQ_DESC="custom schedule"
        ;;
    *)
        echo "Invalid option. Defaulting to daily updates."
        CRON_SCHEDULE="0 3 * * *"
        FREQ_DESC="daily at 3 AM"
        ;;
esac

# Create the cron job
CRON_CMD="$CRON_SCHEDULE $REPO_DIR/auto_update.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "auto_update.sh"; then
    echo
    echo "An auto-update cron job already exists. Replacing it..."
    # Remove existing auto_update.sh entries
    crontab -l 2>/dev/null | grep -v "auto_update.sh" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo
echo "✓ Auto-update cron job configured successfully!"
echo "  Updates will run: $FREQ_DESC"
echo "  Log file: /home/pi/pregnancy-tracker-update.log"
echo

# Set up display update cron jobs
echo
echo "Configuring display update schedule..."
if [ -f "$REPO_DIR/manage_display_cron.sh" ]; then
    bash "$REPO_DIR/manage_display_cron.sh"
else
    echo "Display cron manager not found. Will use default schedule."
fi

# Also set up the main tracker to run on boot
echo
echo "Would you like to also run the tracker on system boot? (y/n): "
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    BOOT_CMD="@reboot sleep 30 && cd $REPO_DIR && /usr/bin/sudo /usr/bin/python3 main.py > $HOME/pregnancy-tracker.log 2>&1 &"
    
    # Check if boot job already exists
    if crontab -l 2>/dev/null | grep -q "@reboot.*main.py"; then
        echo "Boot job already exists. Replacing it..."
        crontab -l 2>/dev/null | grep -v "@reboot.*main.py" | crontab -
    fi
    
    (crontab -l 2>/dev/null; echo "$BOOT_CMD") | crontab -
    echo "✓ Boot startup configured!"
fi

echo
echo "Setup complete! Your cron jobs:"
echo "================================"
crontab -l | grep -E "(auto_update|main.py)" || echo "No cron jobs found"
echo
echo "To monitor updates, run: tail -f /home/pi/pregnancy-tracker-update.log"
echo "To manually trigger an update, run: $REPO_DIR/auto_update.sh"