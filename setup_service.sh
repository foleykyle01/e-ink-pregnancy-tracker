#!/bin/bash
# Script to install the pregnancy tracker as a system service

echo "Installing Pregnancy Tracker as a system service..."

# Copy service file to systemd directory
sudo cp pregnancy-tracker.service /etc/systemd/system/

# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable pregnancy-tracker.service

# Start the service now
sudo systemctl start pregnancy-tracker.service

echo "Service installed and started!"
echo ""
echo "Useful commands:"
echo "  Check status:  sudo systemctl status pregnancy-tracker"
echo "  Stop service:  sudo systemctl stop pregnancy-tracker"
echo "  Start service: sudo systemctl start pregnancy-tracker"
echo "  View logs:     sudo journalctl -u pregnancy-tracker -f"
echo "  Restart:       sudo systemctl restart pregnancy-tracker"