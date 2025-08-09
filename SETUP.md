# 🍼 E-ink Pregnancy Tracker Setup Guide

A Raspberry Pi-powered e-ink display that shows pregnancy progress, baby size comparisons, and appointment reminders.

## Features

- **4 Display Screens** controlled by physical buttons:
  - Progress screen with percentage and visual timeline
  - Baby size comparison (fruit/object references)
  - Next appointment reminder
  - Baby info (weeks, days remaining, trimester)
- **Auto-Updates** from GitHub every hour
- **Runs Automatically** on boot - no interaction needed
- **Family-Friendly** - designed for non-technical users

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- Waveshare 2.7inch e-Paper HAT (with 4 buttons)
- Power supply for Raspberry Pi
- SD card with Raspberry Pi OS

## Initial Setup (One-Time Only)

### Step 1: Prepare Your Raspberry Pi

1. Install Raspberry Pi OS on your SD card
2. Enable SSH and connect to WiFi
3. Attach the Waveshare e-ink display to the GPIO pins

### Step 2: Clone the Repository

SSH into your Raspberry Pi and run:

```bash
cd ~
git clone https://github.com/[YOUR-USERNAME]/e-ink-pregnancy-tracker.git
cd e-ink-pregnancy-tracker
```

### Step 3: Configure Your Due Date

Edit `config.json` with your expected birth date:

```json
{
    "expected_birth_date": "2025-05-15"
}
```

### Step 4: Run the Installer

```bash
chmod +x INSTALL.sh
./INSTALL.sh
```

This installer will:
- Install all required packages
- Set up the auto-start service
- Configure automatic GitHub updates
- Start the tracker immediately

**That's it!** The tracker is now running and will:
- Start automatically when the Pi boots
- Check for updates every hour
- Apply changes automatically
- Keep running 24/7

## Using the Tracker

### Button Controls

- **Button 1**: Progress screen (percentage complete)
- **Button 2**: Baby size comparison 
- **Button 3**: Next appointment
- **Button 4**: Development milestones

### Updating Appointments

Edit `appointments.json` with your next appointment:

```json
{
    "appointments": [
        {
            "date": "2025-01-20",
            "time": "2:30 PM",
            "type": "20 Week Ultrasound"
        }
    ]
}
```

Commit and push to GitHub - the display will update within an hour.

## Management Commands

Check if running:
```bash
sudo systemctl status pregnancy-tracker-auto
```

View logs:
```bash
sudo journalctl -u pregnancy-tracker-auto -f
```

Restart service:
```bash
sudo systemctl restart pregnancy-tracker-auto
```

Manual update from GitHub:
```bash
cd ~/e-ink-pregnancy-tracker && git pull
sudo systemctl restart pregnancy-tracker-auto
```

## Troubleshooting

**Display not updating?**
- Check WiFi connection
- Verify service is running: `sudo systemctl status pregnancy-tracker-auto`
- Check logs for errors: `sudo journalctl -u pregnancy-tracker-auto -n 50`

**Buttons not working?**
- Restart the service: `sudo systemctl restart pregnancy-tracker-auto`
- Check GPIO connections on the display

**Wrong information displayed?**
- Verify `config.json` has correct due date
- Check `appointments.json` has current appointment
- Pull latest updates: `cd ~/e-ink-pregnancy-tracker && git pull`

## For Family Members

Once set up, family members just need to:
1. Plug in the Raspberry Pi
2. Wait 30 seconds for it to start
3. Press buttons to see different information

No technical knowledge required!

## Project Structure

```
e-ink-pregnancy-tracker/
├── main.py                    # Main display control script
├── tracker_with_updates.py    # Auto-update wrapper
├── config.json               # Due date configuration
├── appointments.json         # Appointment data
├── pregnancy_tracker/        # Core display logic
│   ├── screen_ui.py         # Screen layouts
│   ├── pregnancy.py         # Progress calculations
│   └── size_data.py         # Baby size data
├── waveshare_epd/           # Display drivers
└── INSTALL.sh              # One-time installer
```

## Support

For issues or questions, please open an issue on GitHub.

---

*Built with ❤️ for expecting parents*