# E-ink Pregnancy Tracker

A Raspberry Pi-powered e-ink display that tracks pregnancy progress, baby development milestones, and appointment reminders.

![Waveshare 2.7inch e-Paper Display](https://img.shields.io/badge/Display-Waveshare%202.7inch-blue)
![Raspberry Pi](https://img.shields.io/badge/Platform-Raspberry%20Pi-red)
![Python](https://img.shields.io/badge/Language-Python%203-green)

## Overview

This project turns a Raspberry Pi with an e-ink display into a dedicated pregnancy tracker that shows:
- Real-time pregnancy progress with visual timeline
- Weekly baby size comparisons
- Upcoming appointment reminders
- Developmental milestones for each week

The tracker runs 24/7, automatically updates from GitHub, and is controlled by physical buttons - no technical knowledge required for daily use.

## Features

### 4 Display Screens
1. **Progress Screen** - Shows percentage complete with visual progress bar
2. **Size Comparison** - Current week and baby size reference
3. **Appointments** - Next upcoming appointment details
4. **Milestones** - Weekly developmental updates and baby weight

### Auto-Update System
- Checks GitHub for updates every hour
- Automatically applies changes without intervention
- Perfect for remote management by tech-savvy family members

### Family-Friendly Design
- Physical button controls
- No app or phone required
- Starts automatically on power-up
- E-ink display is easy on the eyes and always visible

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- [Waveshare 2.7inch e-Paper HAT](https://www.waveshare.com/2.7inch-e-paper-hat.htm) with 4 buttons
- MicroSD card (8GB+) with Raspberry Pi OS
- Power supply

## Quick Start

1. **Clone the repository**
   ```bash
   cd ~
   git clone https://github.com/[YOUR-USERNAME]/e-ink-pregnancy-tracker.git
   cd e-ink-pregnancy-tracker
   ```

2. **Set your due date**
   Edit `config.json`:
   ```json
   {
       "expected_birth_date": "2025-05-15"
   }
   ```

3. **Run the installer**
   ```bash
   chmod +x INSTALL.sh
   ./INSTALL.sh
   ```

That's it! The display will start showing pregnancy information immediately.

## Managing Appointments

Edit `appointments.json` to add appointments:
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

Push changes to GitHub and the display updates automatically within an hour.

## Button Controls

- **Button 1** - Progress screen
- **Button 2** - Baby size comparison
- **Button 3** - Next appointment
- **Button 4** - Development milestones

## Project Structure

```
e-ink-pregnancy-tracker/
├── main.py                      # Main display controller
├── tracker_with_updates.py      # Auto-update wrapper
├── config.json                  # Due date configuration
├── appointments.json            # Appointment tracking
├── pregnancy_tracker/           # Core display logic
│   ├── screen_ui.py            # Screen layouts
│   ├── pregnancy.py            # Progress calculations
│   ├── size_data.py            # Weekly size comparisons
│   └── developmental_milestones.py  # Weekly development info
└── waveshare_epd/              # Display drivers
```

## For Developers

The display uses the Waveshare EPD library for e-ink control. Each screen is rendered as a PIL image with careful consideration for the 264x176 pixel resolution and 4-color grayscale capability.

Key files:
- `screen_ui.py` - Defines all screen layouts
- `pregnancy.py` - Handles date calculations and progress tracking
- `developmental_milestones.py` - Weekly milestone data

## Troubleshooting

**Display not updating?**
```bash
sudo systemctl status pregnancy-tracker-auto
sudo journalctl -u pregnancy-tracker-auto -f
```

**Manual restart:**
```bash
sudo systemctl restart pregnancy-tracker-auto
```

## Credits

Created by Kyle Foley

Built with love for expecting parents who want a simple, always-on way to track their pregnancy journey.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the tracker.

---

*For detailed setup instructions, see [SETUP.md](SETUP.md)*