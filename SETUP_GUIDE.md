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

### 5. Install Waveshare Display Library
```bash
# Clone the official Waveshare repository
cd ~
git clone https://github.com/waveshare/e-Paper.git

# Copy the library to your project
cd e-Paper/RaspberryPi_JetsonNano/python
cp -r lib/waveshare_epd ~/e-ink-pregnancy-tracker/

# Go back to project directory
cd ~/e-ink-pregnancy-tracker

# Install Python PIL dependency
sudo apt-get install python3-pil -y
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
# Run the main script to test (requires sudo for GPIO access)
sudo python3 main.py
```

You should see the pregnancy tracker display on your e-ink screen!

**Note:** The display alternates between two screens:
- **Progress screen**: Shows percentage complete with week/day
- **Size screen**: Shows current week number and baby size comparison
- Screens automatically switch every 20 minutes

### 8. Setup Automatic Updates with Cron
```bash
# Use root's crontab for GPIO access
sudo crontab -e

# If prompted, select option 1 for nano editor
```

Add this line for updates every 10 minutes (recommended):
```bash
# Update every 10 minutes - balanced for display lifespan and screen rotation
*/10 * * * * cd /home/kylefoley/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/kylefoley/tracker.log 2>&1
```

**Why every 10 minutes?**
- Screens switch every 20 minutes
- Updates twice per screen cycle ensures both screens are shown
- Preserves e-ink display lifespan

**Alternative update frequencies:**
```bash
# Update every 5 minutes (more frequent updates, shorter display life)
*/5 * * * * cd /home/kylefoley/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/kylefoley/tracker.log 2>&1

# Update every 20 minutes (shows alternating screens each update)
*/20 * * * * cd /home/kylefoley/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/kylefoley/tracker.log 2>&1
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

Verify the cron job was added:
```bash
sudo crontab -l
```

Save and exit. The cron job will now run automatically.

### 9. (Optional) Setup Automatic GitHub Updates
To automatically pull updates from GitHub (useful for multiple Pis), create an update script:

```bash
# Create the update script
nano ~/e-ink-pregnancy-tracker/auto_update.sh
```

Add this content:
```bash
#!/bin/bash
# Auto-update script for pregnancy tracker

cd /home/kylefoley/e-ink-pregnancy-tracker

# Pull latest changes from GitHub
git pull origin master

# Copy waveshare library back if it was removed
if [ ! -d "waveshare_epd" ]; then
    echo "Restoring waveshare_epd library..."
    cp -r ~/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./
fi

echo "Update completed at $(date)"
```

Make it executable:
```bash
chmod +x ~/e-ink-pregnancy-tracker/auto_update.sh
```

Add to cron to run daily at 3 AM:
```bash
sudo crontab -e
```

Add this line (in addition to your display update line):
```bash
# Auto-update from GitHub daily at 3 AM
0 3 * * * /home/kylefoley/e-ink-pregnancy-tracker/auto_update.sh >> /home/kylefoley/update.log 2>&1
```

Now your Pi will automatically pull any updates you push to GitHub!

Test the update script manually:
```bash
~/e-ink-pregnancy-tracker/auto_update.sh
```

Check update logs:
```bash
tail -f /home/kylefoley/update.log
```

### 10. (Optional) Setup as System Service
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
User=root
WorkingDirectory=/home/kylefoley/e-ink-pregnancy-tracker
ExecStart=/usr/bin/python3 /home/kylefoley/e-ink-pregnancy-tracker/main.py
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
# Make sure you've copied the library from Waveshare repo
cd ~/e-Paper/RaspberryPi_JetsonNano/python
cp -r lib/waveshare_epd ~/e-ink-pregnancy-tracker/
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

## Important Notes
- **Display Version**: This setup is for the 2.7" Rev 2.2 display (264x176 pixels)
- **Driver**: Uses the `epd2in7_V2` driver from waveshare_epd library
- **GPIO Access**: Requires sudo to access GPIO pins
- **Screen Switching**: Alternates between Progress and Size screens every 20 minutes
- The display updates slowly (2-3 seconds) - this is normal for e-ink
- Recommended update frequency is every 10 minutes for optimal display lifespan
- The display retains the image even when powered off
- In cold temperatures, the display may update more slowly

## Monitoring
Check if updates are working:
```bash
# View the log file
tail -f /home/kylefoley/tracker.log

# Check cron execution
sudo grep CRON /var/log/syslog | tail -10
```