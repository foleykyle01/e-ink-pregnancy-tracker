#!/bin/bash
# Script to deploy the update fix to the Raspberry Pi
# Run this on the Pi after pulling the latest changes

echo "Deploying auto-restart fix..."

# Make sure we're in the right directory
cd /home/kylefoley/e-ink-pregnancy-tracker

# Pull latest changes
echo "Pulling latest changes..."
git pull

# Restart the service to apply the fix
echo "Restarting service..."
sudo systemctl restart pregnancy-tracker-auto

echo "Done! The service should now properly restart after pulling updates."
echo ""
echo "Check status with: sudo systemctl status pregnancy-tracker-auto"
echo "View logs with: sudo journalctl -u pregnancy-tracker-auto -f"