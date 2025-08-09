#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Main tracker script that handles auto-updates
Checks for GitHub updates every hour and restarts if needed
"""
import subprocess
import time
import os
import sys
import threading
import hashlib

# Configuration
UPDATE_CHECK_INTERVAL = 3600  # Check for updates every hour (in seconds)
REPO_DIR = "/home/kylefoley/e-ink-pregnancy-tracker"

def get_file_hash(filepath):
    """Get hash of a file to detect changes"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def check_and_apply_updates():
    """Check GitHub for updates and apply them"""
    try:
        os.chdir(REPO_DIR)
        
        # Get the hash of main files before update
        main_hash_before = get_file_hash("main.py")
        ui_hash_before = get_file_hash("pregnancy_tracker/screen_ui.py")
        
        # Fetch latest changes from GitHub
        result = subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True
        )
        
        # Check if there are updates
        result = subprocess.run(
            ["git", "status", "-uno"],
            capture_output=True,
            text=True
        )
        
        if "Your branch is behind" in result.stdout:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Updates found, applying...")
            
            # Pull the updates
            subprocess.run(
                ["git", "pull", "origin", "master"],
                capture_output=True,
                text=True
            )
            
            # Check if critical files changed
            main_hash_after = get_file_hash("main.py")
            ui_hash_after = get_file_hash("pregnancy_tracker/screen_ui.py")
            
            if main_hash_before != main_hash_after or ui_hash_before != ui_hash_after:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Critical files updated, restarting...")
                return True  # Need restart
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Updates applied (data only)")
                return False  # No restart needed
        else:
            return False  # No updates
            
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Update check error: {e}")
        return False

def update_checker_thread():
    """Background thread that checks for updates"""
    while True:
        time.sleep(UPDATE_CHECK_INTERVAL)
        if check_and_apply_updates():
            # Restart the entire script if critical files changed
            os.execv(sys.executable, [sys.executable] + sys.argv)

def run_main_tracker():
    """Run the main tracker script"""
    try:
        # Start the update checker in background
        update_thread = threading.Thread(target=update_checker_thread)
        update_thread.daemon = True
        update_thread.start()
        
        # Import and run the main tracker
        sys.path.insert(0, REPO_DIR)
        import main  # This will run the main tracker
        
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Tracker error: {e}")
        time.sleep(10)
        # Restart on error
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    # Check for updates on startup
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting pregnancy tracker with auto-updates...")
    os.chdir(REPO_DIR)
    check_and_apply_updates()
    
    # Run the tracker
    run_main_tracker()