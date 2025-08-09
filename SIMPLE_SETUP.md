# 🍼 Easy Setup Guide for Family Members

This guide is for non-technical family members who want to set up the pregnancy tracker.

## What You Need
- Raspberry Pi with the e-ink display attached
- Power cable for the Raspberry Pi
- Internet connection (WiFi or Ethernet)

## One-Time Setup (Only do this once!)

### Step 1: Connect to Your Raspberry Pi
1. Plug in your Raspberry Pi and wait 1 minute for it to start
2. On your computer, open Terminal (Mac) or Command Prompt (Windows)
3. Type this and press Enter:
   ```
   ssh kylefoley@raspberrypi.local
   ```
4. Enter the password when asked

### Step 2: Get the Tracker Code
Copy and paste this command, then press Enter:
```bash
cd ~ && git clone https://github.com/[YOUR-GITHUB-USERNAME]/e-ink-pregnancy-tracker.git
```

### Step 3: Install Everything
Copy and paste these commands one at a time:
```bash
cd ~/e-ink-pregnancy-tracker
chmod +x INSTALL.sh
./INSTALL.sh
```

**That's it! The tracker is now running!**

## How It Works (No Action Needed!)

Once installed, the tracker:
- ✅ Starts automatically when you plug in the Pi
- ✅ Updates itself from the internet every hour
- ✅ Shows pregnancy progress on the screen
- ✅ Works with the 4 buttons to show different information

## Using the Buttons

Press any button on the display:
- **Button 1**: Shows pregnancy progress (percentage)
- **Button 2**: Shows baby size (compared to fruits/objects)
- **Button 3**: Shows next doctor appointment
- **Button 4**: Shows weeks and days information

## If Something Goes Wrong

Just unplug the Raspberry Pi, wait 10 seconds, and plug it back in. It will start working again automatically!

## Checking If It's Working

Want to make sure it's running? After connecting to the Pi (Step 1 above), type:
```bash
sudo systemctl status pregnancy-tracker-auto
```

You should see green text saying "active (running)".

---

**Remember**: Once you run the INSTALL.sh script, you never need to do anything again! The tracker will keep itself updated and running.