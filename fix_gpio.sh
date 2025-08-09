#!/bin/bash
# Script to fix GPIO issues on Raspberry Pi

echo "Fixing GPIO issues..."

# Kill any existing Python processes
echo "Stopping Python processes..."
sudo pkill -f python3
sudo pkill -f python
sleep 1

# Reset GPIO using system commands
echo "Resetting GPIO..."
for gpio in 5 6 13 19 17 25 24 18; do
    echo $gpio > /sys/class/gpio/unexport 2>/dev/null || true
done

# Clear any lgpio locks
echo "Clearing lgpio locks..."
sudo rm -f /var/run/lgpio* 2>/dev/null || true

# Reset SPI
echo "Resetting SPI..."
sudo modprobe -r spi_bcm2835
sudo modprobe spi_bcm2835

echo "GPIO reset complete!"
echo ""
echo "Now try running: sudo python3 main.py"