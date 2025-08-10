#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Main tracker script that handles auto-updates
Checks for GitHub updates periodically and restarts if needed
"""
import subprocess
import time
import os
import sys
import threading
import hashlib
import logging

# Configuration
UPDATE_CHECK_INTERVAL = 1800  # Check for updates every 30 minutes (in seconds)
REPO_DIR = "/home/kylefoley/e-ink-pregnancy-tracker"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_file_hash(filepath):
    """Get hash of a file to detect changes"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def get_default_branch():
    """Get the default branch name (main or master)"""
    try:
        # Try to get the default branch from remote
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Extract branch name from refs/remotes/origin/main
            branch = result.stdout.strip().split('/')[-1]
            logging.info(f"Detected default branch: {branch}")
            return branch
    except:
        pass
    
    # Check if main branch exists
    result = subprocess.run(
        ["git", "branch", "-r"],
        capture_output=True,
        text=True
    )
    if "origin/main" in result.stdout:
        return "main"
    elif "origin/master" in result.stdout:
        return "master"
    
    # Default to main
    return "main"

def check_and_apply_updates():
    """Check GitHub for updates and apply them"""
    try:
        os.chdir(REPO_DIR)
        
        # Get the default branch
        branch = get_default_branch()
        logging.info(f"Checking for updates on branch: {branch}")
        
        # Get the hash of main files before update
        main_hash_before = get_file_hash("main.py")
        ui_hash_before = get_file_hash("pregnancy_tracker/screen_ui.py")
        
        # Fetch latest changes from GitHub
        logging.info("Fetching from GitHub...")
        result = subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"Git fetch failed: {result.stderr}")
            return False
        
        # Check if there are updates
        result = subprocess.run(
            ["git", "rev-list", "HEAD..origin/" + branch, "--count"],
            capture_output=True,
            text=True
        )
        
        update_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        
        if update_count > 0:
            logging.info(f"Found {update_count} updates, applying...")
            
            # Stash any local changes (like logs)
            subprocess.run(
                ["git", "stash"],
                capture_output=True,
                text=True
            )
            
            # Pull the updates
            result = subprocess.run(
                ["git", "pull", "origin", branch],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logging.error(f"Git pull failed: {result.stderr}")
                # Try to recover
                subprocess.run(["git", "stash", "pop"], capture_output=True)
                return False
            
            logging.info("Updates pulled successfully")
            
            # Check if critical files changed
            main_hash_after = get_file_hash("main.py")
            ui_hash_after = get_file_hash("pregnancy_tracker/screen_ui.py")
            
            if main_hash_before != main_hash_after or ui_hash_before != ui_hash_after:
                logging.info("Critical files updated, restart required")
                return True  # Need restart
            else:
                logging.info("Updates applied (data files only, no restart needed)")
                return False  # No restart needed
        else:
            logging.debug("No updates available")
            return False  # No updates
            
    except Exception as e:
        logging.error(f"Update check error: {e}")
        return False

def update_checker_thread():
    """Background thread that checks for updates"""
    while True:
        time.sleep(UPDATE_CHECK_INTERVAL)
        logging.info("Running scheduled update check...")
        if check_and_apply_updates():
            # Restart the entire script if critical files changed
            logging.info("Restarting tracker...")
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
        logging.error(f"Tracker error: {e}")
        time.sleep(10)
        # Restart on error
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    # Check for updates on startup
    logging.info("Starting pregnancy tracker with auto-updates...")
    os.chdir(REPO_DIR)
    
    # Initial update check
    if check_and_apply_updates():
        logging.info("Updates found on startup, restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    # Run the tracker
    run_main_tracker()