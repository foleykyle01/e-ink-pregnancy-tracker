#!/bin/bash
# One-time setup script for the Pregnancy Tracker
# Run this ONCE after cloning the repository

echo "======================================"
echo "  E-ink Pregnancy Tracker Installer  "
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📦 Installing required packages..."
# Install required system packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy git

# Install Python packages (using break-system-packages for dedicated Pi)
pip3 install --break-system-packages RPi.GPIO spidev pillow

echo ""
echo "🔧 Setting up auto-start service..."

# Stop any existing service
sudo systemctl stop pregnancy-tracker 2>/dev/null
sudo systemctl stop pregnancy-tracker-auto 2>/dev/null
sudo systemctl disable pregnancy-tracker 2>/dev/null
sudo systemctl disable pregnancy-tracker-auto 2>/dev/null

# Copy the new service file
sudo cp "$SCRIPT_DIR/pregnancy-tracker-auto.service" /etc/systemd/system/

# Update the service file with correct path
sudo sed -i "s|/home/kylefoley/e-ink-pregnancy-tracker|$SCRIPT_DIR|g" /etc/systemd/system/pregnancy-tracker-auto.service

# Update the tracker script with correct path
sed -i "s|REPO_DIR = \"/home/kylefoley/e-ink-pregnancy-tracker\"|REPO_DIR = \"$SCRIPT_DIR\"|g" "$SCRIPT_DIR/tracker_with_updates.py"

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable pregnancy-tracker-auto.service
sudo systemctl start pregnancy-tracker-auto.service

echo ""
echo "✅ Installation complete!"
echo ""
echo "The tracker is now running and will:"
echo "  • Start automatically when the Pi boots"
echo "  • Check for updates from GitHub every hour"
echo "  • Apply updates automatically"
echo "  • Restart if there are any errors"
echo ""
echo "📱 Button Controls:"
echo "  Button 1: Progress screen"
echo "  Button 2: Baby size comparison"
echo "  Button 3: Next appointment"
echo "  Button 4: Development milestones"
echo ""
echo "🔧 Useful commands:"
echo "  Check status:  sudo systemctl status pregnancy-tracker-auto"
echo "  View logs:     sudo journalctl -u pregnancy-tracker-auto -f"
echo "  Restart:       sudo systemctl restart pregnancy-tracker-auto"
echo ""
echo "To update appointments, edit appointments.json and push to GitHub."
echo "The display will update automatically within an hour."
echo ""