#!/bin/bash

# Monitor script for pregnancy tracker updates and health
# This script provides diagnostic information and log monitoring

REPO_DIR="$HOME/e-ink-pregnancy-tracker"
LOG_FILE="$HOME/pregnancy-tracker-update.log"
TRACKER_LOG="$HOME/pregnancy-tracker.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==================================="
echo "Pregnancy Tracker Monitor"
echo "==================================="
echo

# Check if tracker is running
if pgrep -f "python.*main.py" > /dev/null; then
    PID=$(pgrep -f "python.*main.py")
    echo -e "${GREEN}✓${NC} Tracker is running (PID: $PID)"
else
    echo -e "${RED}✗${NC} Tracker is not running"
fi

# Check last update time
if [ -f "$LOG_FILE" ]; then
    LAST_UPDATE=$(grep "Starting auto-update check" "$LOG_FILE" | tail -1 | cut -d' ' -f1-2 | tr -d '[]')
    if [ -n "$LAST_UPDATE" ]; then
        echo -e "${GREEN}✓${NC} Last update check: $LAST_UPDATE"
    fi
fi

# Check for recent errors
echo
echo "Recent errors (last 24 hours):"
echo "-------------------------------"
if [ -f "$LOG_FILE" ]; then
    ERRORS=$(grep -i "error" "$LOG_FILE" | tail -5)
    if [ -n "$ERRORS" ]; then
        echo -e "${YELLOW}$ERRORS${NC}"
    else
        echo -e "${GREEN}No recent errors${NC}"
    fi
else
    echo "Log file not found"
fi

# Check display configuration
echo
echo "Display configuration:"
echo "--------------------"
if [ -f "$REPO_DIR/settings/display_config.json" ] && command -v jq &> /dev/null; then
    DISPLAY_ENABLED=$(jq -r '.display_update.enabled' "$REPO_DIR/settings/display_config.json")
    FREQUENCY=$(jq -r '.display_update.frequency_minutes' "$REPO_DIR/settings/display_config.json")
    SCREEN_SWITCH=$(jq -r '.screen_switching.switch_interval_minutes' "$REPO_DIR/settings/display_config.json")
    echo "Display updates: $DISPLAY_ENABLED (every $FREQUENCY minutes)"
    echo "Screen switching: every $SCREEN_SWITCH minutes"
else
    echo "Configuration file not found or jq not installed"
fi

# Check cron jobs
echo
echo "Configured cron jobs:"
echo "--------------------"
crontab -l 2>/dev/null | grep -E "(auto_update|main.py|PREGNANCY_TRACKER)" || echo "No cron jobs found"
sudo crontab -l 2>/dev/null | grep "PREGNANCY_TRACKER_DISPLAY" | head -3 || echo "No display cron jobs found"

# Check git status
echo
echo "Repository status:"
echo "-----------------"
if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
    BRANCH=$(git branch --show-current 2>/dev/null)
    COMMIT=$(git rev-parse --short HEAD 2>/dev/null)
    echo "Branch: $BRANCH"
    echo "Commit: $COMMIT"
    
    # Check if behind remote
    git fetch origin >/dev/null 2>&1
    BEHIND=$(git rev-list HEAD..origin/$BRANCH --count 2>/dev/null)
    if [ "$BEHIND" -gt 0 ]; then
        echo -e "${YELLOW}Repository is $BEHIND commits behind origin/$BRANCH${NC}"
    else
        echo -e "${GREEN}Repository is up to date${NC}"
    fi
fi

# Disk space check
echo
echo "System resources:"
echo "----------------"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}Warning: Disk usage is at $DISK_USAGE%${NC}"
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${YELLOW}Disk usage: $DISK_USAGE%${NC}"
else
    echo -e "${GREEN}Disk usage: $DISK_USAGE%${NC}"
fi

# Memory check
MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100}')
echo "Memory usage: ${MEM_USAGE}%"

echo
echo "==================================="
echo "Commands:"
echo "  View update log:  tail -f $LOG_FILE"
echo "  View tracker log: tail -f $TRACKER_LOG"
echo "  Manual update:    $REPO_DIR/auto_update.sh"
echo "  Restart tracker:  sudo systemctl restart pregnancy-tracker"
echo "===================================" 