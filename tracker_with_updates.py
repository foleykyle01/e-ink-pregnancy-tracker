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
import logging

# Configuration
UPDATE_CHECK_INTERVAL = 1800  # Check for updates every 30 minutes (in seconds)
# Dynamically determine the repository directory
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

def wait_for_network(max_attempts=30, delay=2):
    """Wait for network connectivity before proceeding"""
    import socket
    for attempt in range(max_attempts):
        try:
            # Try to resolve GitHub's domain
            socket.gethostbyname("github.com")
            logging.info("Network is ready")
            return True
        except socket.gaierror:
            if attempt < max_attempts - 1:
                logging.info(f"Waiting for network... attempt {attempt + 1}/{max_attempts}")
                time.sleep(delay)
    logging.error("Network not available after waiting")
    return False

def check_and_apply_updates():
    """Check GitHub for updates and apply them"""
    try:
        os.chdir(REPO_DIR)
        
        # Get the default branch
        branch = get_default_branch()
        logging.info(f"Checking for updates on branch: {branch}")
        
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
            
            # Always restart when ANY updates are pulled
            logging.info("Updates applied, restarting to ensure all changes take effect")
            return True  # Always restart after updates
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
            # Exit with code 0 to trigger systemd restart
            logging.info("Updates applied, exiting for restart...")
            os._exit(0)  # Immediate exit, systemd will restart us

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
        # Exit cleanly, systemd will restart us
        sys.exit(1)

if __name__ == "__main__":
    # Check for updates on startup
    logging.info("Starting pregnancy tracker with auto-updates...")
    
    # Wait for network to be ready (important after reboot)
    if not wait_for_network():
        logging.error("Network not available, running in offline mode")
        # Continue anyway - the display should still work offline
    
    os.chdir(REPO_DIR)
    
    # Initial update check (only if network is available)
    if wait_for_network(max_attempts=1, delay=0):  # Quick check
        if check_and_apply_updates():
            logging.info("Updates found on startup, exiting for restart...")
            os._exit(0)  # Immediate exit, systemd will restart us
    
    # Run the tracker
    run_main_tracker()