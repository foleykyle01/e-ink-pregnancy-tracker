# E-ink Pregnancy Tracker

A Raspberry Pi-powered pregnancy tracker that displays pregnancy progress on a 2.7 inch e-Paper HAT. The display alternates between showing percentage completion and baby size comparisons.

![Sample screen image](docs/sample-screen.png)
![Completed project photo](docs/completed-project.jpg)

## Features
- **Dual Display Modes**: Automatically alternates between progress percentage and baby size comparison screens
- **Low Power**: E-ink display retains image even when powered off
- **Automatic Updates**: Self-updating from GitHub with remote configuration
- **Remote Management**: Update display settings and timing without physical access
- **Plug & Play**: Once configured, works autonomously with no user intervention
- **Clean Design**: Minimalist display with clear, readable information

## Hardware Requirements
- Raspberry Pi (Zero/Zero W recommended for compact build)
- [2.7 inch e-Paper HAT by Waveshare](https://www.waveshare.com/2.7inch-e-paper-hat.htm) (264x176 pixels, Rev 2.2)
- MicroSD card (8GB+)
- Power supply for Raspberry Pi

### GPIO Connections
If not using the HAT directly, connect as follows:
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 6)
- DIN → MOSI (Pin 19)
- CLK → SCLK (Pin 23)
- CS → CE0 (Pin 24)
- DC → GPIO 25 (Pin 22)
- RST → GPIO 17 (Pin 11)
- BUSY → GPIO 24 (Pin 18)

## Installation

### Prerequisites
- Raspberry Pi with Raspberry Pi OS installed
- SSH access enabled
- SPI interface enabled (via `sudo raspi-config`)

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install System Dependencies
```bash
# Python and development tools
sudo apt-get install python3-pip python3-dev git -y

# Display libraries
sudo apt-get install python3-pil python3-numpy -y
sudo apt-get install libopenjp2-7 -y

# GPIO and SPI libraries
sudo apt-get install python3-rpi.gpio python3-spidev -y
```

### Step 3: Enable SPI Interface
```bash
sudo raspi-config nonint do_spi 0
```

### Step 4: Clone the Project
```bash
cd ~
git clone https://github.com/foleykyle01/e-ink-pregnancy-tracker.git
cd e-ink-pregnancy-tracker
```

### Step 5: Install Waveshare Display Library
```bash
# Clone official Waveshare repository
cd ~
git clone https://github.com/waveshare/e-Paper.git

# Copy library to project
cd e-Paper/RaspberryPi_JetsonNano/python
cp -r lib/waveshare_epd ~/e-ink-pregnancy-tracker/

# Return to project directory
cd ~/e-ink-pregnancy-tracker
```

### Step 6: Configure the Application
```bash
cp config.json.example config.json
nano config.json
```

Edit to set your expected birth date:
```json
{
    "expected_birth_date": "2025-05-15"
}
```

### Step 7: Test the Display
```bash
sudo python3 main.py
```

You should see the pregnancy tracker display on your e-ink screen!

## Automated Setup (Recommended)

For a fully automated setup with GitHub updates and remote management:

```bash
# Run the automated setup script
bash setup_auto_update.sh
```

This script will:
- Configure automatic GitHub updates (every 12 hours)
- Set up display update schedule (from settings/display_config.json)
- Enable boot startup
- Create all necessary cron jobs

The display timing is controlled by `settings/display_config.json` and can be updated remotely by pushing changes to GitHub.

## Remote Management

### Configurable Settings
All settings in the `settings/` directory can be modified and pushed to GitHub for automatic updates:

- **`settings/display_config.json`** - Control display update frequency and screen switching
- **`config.json`** - Set expected birth date (configure per device)

See [REMOTE_SETTINGS.md](REMOTE_SETTINGS.md) for detailed configuration options.

### Monitoring
Check system status and logs:

```bash
# Monitor system health and configuration
bash monitor_updates.sh

# View update logs
tail -f /home/pi/pregnancy-tracker-update.log

# Manually trigger update
bash auto_update.sh
```

## Troubleshooting

### Display Not Working
1. **Check SPI is enabled:**
   ```bash
   ls /dev/spi*
   # Should show /dev/spidev0.0 and /dev/spidev0.1
   ```

2. **Check GPIO permissions:**
   ```bash
   sudo usermod -a -G gpio,spi $USER
   # Then logout and login again
   ```

3. **Test with Waveshare examples:**
   ```bash
   cd ~/e-Paper/RaspberryPi_JetsonNano/python/examples
   sudo python3 epd_2in7_test.py
   ```

### Python Module Errors
If "No module named 'waveshare_epd'":
```bash
cd ~/e-Paper/RaspberryPi_JetsonNano/python
cp -r lib/waveshare_epd ~/e-ink-pregnancy-tracker/
```

### Permission Errors
```bash
# Quick fix - run with sudo
sudo python3 main.py

# Permanent fix - adjust permissions
sudo chmod 666 /dev/spidev0.0
sudo chmod 666 /dev/spidev0.1
```

### Checking Logs
```bash
# Cron logs
tail -f ~/tracker.log

# Check cron execution
sudo grep CRON /var/log/syslog | tail -10
```

## Local Testing
To test the display output on your development machine without a Raspberry Pi:
```bash
python3 local_test.py
```
This generates and displays the image locally without requiring Raspberry Pi-specific packages.

## Important Notes
- **Display updates slowly (2-3 seconds)** - this is normal for e-ink technology
- **GPIO access requires sudo** - all display updates need root permissions
- **Display retains image when powered off** - e-ink technology benefit
- **Cold temperatures may slow updates** - e-ink limitation
- Uses the `epd2in7_V2` driver for Waveshare 2.7" Rev 2.2 displays

## Useful Resources
- [2.7 inch e-Paper HAT Documentation](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT)
- [3D Printable Case for Display and Raspberry Pi Zero](https://www.printables.com/model/538237-27-inch-e-ink-display-raspberry-pi-zero-case)
- [Waveshare e-Paper GitHub Repository](https://github.com/waveshare/e-Paper)

## License
This project is open source and available under the MIT License.