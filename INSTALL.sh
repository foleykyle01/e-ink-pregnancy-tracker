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

# Install Waveshare e-Paper library
echo ""
echo "📺 Installing Waveshare e-Paper library..."
# Clone the Waveshare library files if they don't exist
if [ ! -d "$SCRIPT_DIR/waveshare_epd" ]; then
    echo "  Downloading Waveshare display drivers..."
    git clone https://github.com/waveshare/e-Paper.git "$SCRIPT_DIR/temp_epaper" 2>/dev/null
    cp -r "$SCRIPT_DIR/temp_epaper/RaspberryPi_JetsonNano/python/lib/waveshare_epd" "$SCRIPT_DIR/"
    rm -rf "$SCRIPT_DIR/temp_epaper"
    echo "  ✓ Waveshare drivers installed"
else
    echo "  ✓ Waveshare drivers already present"
fi

echo ""
echo "🔌 Enabling SPI interface..."
# Enable SPI using raspi-config (more reliable method)
sudo raspi-config nonint do_spi 0
if [ $? -eq 0 ]; then
    echo "  ✓ SPI enabled successfully"
    # Check if SPI was just enabled (requires reboot)
    if ! ls /dev/spidev* 2>/dev/null | grep -q spidev; then
        echo "  ⚠️  SPI enabled but reboot required to activate"
        REBOOT_REQUIRED=1
    fi
else
    echo "  ⚠️  Failed to enable SPI automatically"
    echo "     Please run: sudo raspi-config"
    echo "     Navigate to: Interface Options > SPI > Enable"
fi

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

# No need to update tracker script - it now dynamically determines its own path

echo ""
echo "🔐 Configuring Git safe directory..."
# Configure git to trust the repository directory (needed for auto-updates)
git config --global --add safe.directory "$SCRIPT_DIR"
sudo git config --global --add safe.directory "$SCRIPT_DIR"

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
echo "  • Check for updates from GitHub every 30 minutes"
echo "  • Apply updates and restart automatically"
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
echo "The display will update automatically within 30 minutes."
echo ""

if [ ! -z "$REBOOT_REQUIRED" ]; then
    echo "⚠️  IMPORTANT: A reboot is required for SPI to be enabled!"
    echo "   Run: sudo reboot"
    echo ""
fi