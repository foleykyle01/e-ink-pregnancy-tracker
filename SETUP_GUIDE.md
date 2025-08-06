# Raspberry Pi E-ink Pregnancy Tracker Setup Guide

## Prerequisites
- Raspberry Pi with fresh OS installed (headless)
- SPI enabled (via `sudo raspi-config`)
- SSH access to your Pi
- 2.7 inch Waveshare e-Paper HAT connected

## Step-by-Step Setup

### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Python and System Dependencies
```bash
# Install Python 3 and pip
sudo apt-get install python3-pip python3-dev -y

# Install required system libraries for display
sudo apt-get install python3-pil python3-numpy -y

# Install libopenjp2 for Pillow image processing
sudo apt-get install libopenjp2-7 -y

# Install Git if not already installed
sudo apt-get install git -y
```

### 3. Enable SPI and GPIO (if not already done)
```bash
# Enable SPI interface
sudo raspi-config nonint do_spi 0

# Install GPIO libraries
sudo apt-get install python3-rpi.gpio python3-spidev -y
```

### 4. Clone the Project
```bash
cd ~
git clone https://github.com/grappeq/e-ink-pregnancy-tracker.git
cd e-ink-pregnancy-tracker
```

### 5. Install Python Dependencies
```bash
# Install the Waveshare e-Paper library and other requirements
pip3 install -r requirements.txt

# If you encounter permission issues, use:
sudo pip3 install -r requirements.txt --break-system-packages
```

### 6. Configure the Application
```bash
# Copy the example config and edit it
cp config.json.example config.json
nano config.json
```

Edit the file to set your expected birth date:
```json
{
    "expected_birth_date": "2025-05-15"
}
```
Save with Ctrl+X, Y, Enter

### 7. Test the Display
```bash
# Run the main script to test
python3 main.py
```

You should see the pregnancy tracker display on your e-ink screen!

### 8. Setup Automatic Updates with Cron
```bash
# Open crontab editor
crontab -e
```

Add one of these lines (choose your update frequency):
```bash
# Update every 30 minutes
*/30 * * * * cd /home/pi/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1

# Update every hour
0 * * * * cd /home/pi/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1

# Update twice daily (8am and 8pm)
0 8,20 * * * cd /home/pi/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1
```

Save and exit. The cron job will now run automatically.

### 9. (Optional) Setup as System Service
For more reliable operation, create a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/pregnancy-tracker.service
```

Add this content:
```ini
[Unit]
Description=E-ink Pregnancy Tracker
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/e-ink-pregnancy-tracker
ExecStart=/usr/bin/python3 /home/pi/e-ink-pregnancy-tracker/main.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable pregnancy-tracker.service

# Create a timer for periodic updates
sudo nano /etc/systemd/system/pregnancy-tracker.timer
```

Add timer configuration:
```ini
[Unit]
Description=Run pregnancy tracker every 30 minutes
Requires=pregnancy-tracker.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min

[Install]
WantedBy=timers.target
```

Enable and start the timer:
```bash
sudo systemctl enable pregnancy-tracker.timer
sudo systemctl start pregnancy-tracker.timer

# Check status
sudo systemctl status pregnancy-tracker.timer
```

## Troubleshooting

### Display Not Working
1. Check SPI is enabled:
   ```bash
   ls /dev/spi*
   # Should show /dev/spidev0.0 and /dev/spidev0.1
   ```

2. Check GPIO permissions:
   ```bash
   # Add user to gpio group
   sudo usermod -a -G gpio,spi $USER
   # Logout and login again
   ```

3. Test with Waveshare examples:
   ```bash
   cd ~
   git clone https://github.com/waveshare/e-Paper.git
   cd e-Paper/RaspberryPi_JetsonNano/python/examples
   python3 epd_2in7_test.py
   ```

### Python Module Errors
If you get "No module named 'waveshare_epd'":
```bash
# Reinstall the package
sudo pip3 install --upgrade --force-reinstall waveshare-epaper==1.2.0
```

### Permission Errors
If you get permission errors accessing GPIO:
```bash
# Run with sudo (temporary fix)
sudo python3 main.py

# Or fix permissions (permanent)
sudo chmod 666 /dev/spidev0.0
sudo chmod 666 /dev/spidev0.1
```

### Logs and Debugging
Check logs if using cron:
```bash
tail -f ~/tracker.log
```

Check system logs if using systemd:
```bash
sudo journalctl -u pregnancy-tracker.service -f
```

## Hardware Connections

Ensure your 2.7" e-Paper HAT is properly connected to the GPIO pins:
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 6)
- DIN → MOSI (Pin 19)
- CLK → SCLK (Pin 23)
- CS → CE0 (Pin 24)
- DC → GPIO 25 (Pin 22)
- RST → GPIO 17 (Pin 11)
- BUSY → GPIO 24 (Pin 18)

## Notes
- The display updates slowly (2-3 seconds) - this is normal for e-ink
- Frequent updates (more than once per minute) may reduce display lifespan
- The display retains the image even when powered off
- In cold temperatures, the display may update more slowly