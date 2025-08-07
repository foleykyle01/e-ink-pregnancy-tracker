# Raspberry Pi E-ink Pregnancy Tracker Setup Guide

## Prerequisites
- Raspberry Pi with fresh OS installed (headless)
- SPI enabled (via `sudo raspi-config`)
- SSH access to your Pi
- 2.7 inch Waveshare e-Paper HAT connected

## Step-by-Step Setup

## If there is an existing connection to the PI
ssh-keygen -R 192.168.1.240

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
git clone https://github.com/foleykyle01/e-ink-pregnancy-tracker.git
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

### 8. Automated Setup (Recommended)

Use the automated setup script for complete configuration:

```bash
bash setup_auto_update.sh
```

The script will:
1. Ask for your preferred GitHub update frequency (recommended: every 12 hours)
2. Configure display update cron jobs based on `settings/display_config.json`
3. Optionally set up boot startup
4. Create all necessary logging

This is the recommended approach as it enables:
- Automatic GitHub updates
- Remote configuration management
- Proper logging and monitoring
- Display timing control via settings files

### 8a. Manual Setup (Alternative)
```bash
# Use root's crontab for GPIO access
sudo crontab -e

# If prompted, select option 1 for nano editor
```

Add this line for updates every 10 minutes (recommended):
```bash
# Update every 10 minutes - balanced for display lifespan and screen rotation
*/10 * * * * cd /home/pi/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1
```

**Why every 10 minutes?**
- Screens switch every 20 minutes
- Updates twice per screen cycle ensures both screens are shown
- Preserves e-ink display lifespan

**Alternative update frequencies:**
```bash
# Update every 5 minutes (more frequent updates, shorter display life)
*/5 * * * * cd /home/pi/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1

# Update every 20 minutes (shows alternating screens each update)
*/20 * * * * cd /home/pi/e-ink-pregnancy-tracker && /usr/bin/python3 main.py >> /home/pi/tracker.log 2>&1
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

Verify the cron job was added:
```bash
sudo crontab -l
```

Save and exit. The cron job will now run automatically.

### 9. Remote Management and Monitoring

The automated setup includes remote management capabilities:

#### Monitoring System Status
```bash
# Check system health, configuration, and cron jobs
bash monitor_updates.sh
```

#### Remote Configuration
Modify files in the `settings/` directory and push to GitHub:
- `settings/display_config.json` - Control display timing
- `config.json` - Set birth date (per device)

Changes are automatically applied on next update cycle.

#### Manual Operations
```bash
# Force immediate update from GitHub
bash auto_update.sh

# View update logs
tail -f /home/pi/pregnancy-tracker-update.log

# View display logs
tail -f /home/pi/tracker.log
```

See [REMOTE_SETTINGS.md](../REMOTE_SETTINGS.md) for detailed configuration options.

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

## Deployment for End Users

Once setup is complete, the Raspberry Pi becomes a plug-and-play device:

### What Recipients Need:
- Power outlet (USB-C or micro USB depending on Pi model)
- Internet connection (Ethernet or pre-configured WiFi)
- **Nothing else!** No configuration, no technical knowledge required

### What Happens When They Plug It In:
1. Pi boots automatically (30-60 seconds)
2. Display starts showing pregnancy information
3. Updates continue based on your configured schedule
4. GitHub updates pull automatically
5. Remote configuration changes apply without user intervention

### Pre-Deployment Checklist:
```bash
# Verify all systems are working
bash monitor_updates.sh

# Confirm cron jobs are set up
sudo crontab -l
crontab -l

# Test display manually one more time
sudo python3 main.py
```

## Important Notes
- **Display Version**: This setup is for the 2.7" Rev 2.2 display (264x176 pixels)
- **Driver**: Uses the `epd2in7_V2` driver from waveshare_epd library
- **GPIO Access**: Requires sudo to access GPIO pins
- **Screen Switching**: Alternates between Progress and Size screens every 20 minutes (configurable)
- The display updates slowly (2-3 seconds) - this is normal for e-ink
- Recommended update frequency is every 10 minutes for optimal display lifespan
- The display retains the image even when powered off
- In cold temperatures, the display may update more slowly
- **Plug & Play**: Once configured, works autonomously with no user interaction

## Monitoring
Check if updates are working:
```bash
# View the log file
tail -f /home/kylefoley/tracker.log

# Check cron execution
sudo grep CRON /var/log/syslog | tail -10
```