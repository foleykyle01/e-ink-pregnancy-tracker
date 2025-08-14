#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Main tracker script that handles auto-updates
Simplified version that prioritizes reliability over features
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

def run_main_tracker():
    """Run the main tracker program directly"""
    try:
        logging.info("Starting main tracker...")
        
        # Change to repo directory
        os.chdir(REPO_DIR)
        
        # Import and run the main tracker
        sys.path.insert(0, REPO_DIR)
        import main  # This will run the main tracker
        
    except Exception as e:
        logging.error(f"Tracker error: {str(e)[:200]}")
        time.sleep(10)
        sys.exit(1)

def try_git_pull():
    """Try to pull updates, but don't let it block the tracker"""
    try:
        # Set environment to prevent git from hanging
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_ASKPASS"] = ""
        
        # Try a quick fetch with timeout
        result = subprocess.run(
            ["timeout", "5", "git", "fetch", "origin"],
            capture_output=True,
            text=True,
            cwd=REPO_DIR,
            env=env
        )
        
        if result.returncode != 0:
            return False
        
        # Check if there are updates
        result = subprocess.run(
            ["git", "rev-list", "HEAD..origin/master", "--count"],
            capture_output=True,
            text=True,
            cwd=REPO_DIR,
            timeout=2
        )
        
        if result.returncode == 0:
            update_count = int(result.stdout.strip())
            if update_count > 0:
                logging.info(f"Found {update_count} updates, pulling...")
                
                # Try to pull with timeout
                result = subprocess.run(
                    ["timeout", "10", "git", "pull", "origin", "master"],
                    capture_output=True,
                    text=True,
                    cwd=REPO_DIR,
                    env=env
                )
                
                if result.returncode == 0:
                    logging.info("Updates pulled successfully, restarting...")
                    return True
        
        return False
        
    except Exception as e:
        logging.debug(f"Update check failed: {e}")
        return False

def update_check_loop():
    """Background thread that checks for updates periodically"""
    while True:
        time.sleep(UPDATE_CHECK_INTERVAL)
        try:
            logging.info("Checking for updates...")
            if try_git_pull():
                # Exit so systemd can restart us with new code
                os._exit(0)
        except:
            pass  # Ignore all errors in update thread

if __name__ == "__main__":
    try:
        logging.info("Starting pregnancy tracker with auto-updates...")
        logging.info(f"Repository directory: {REPO_DIR}")
        
        # Start the update checker in background (non-blocking)
        update_thread = threading.Thread(target=update_check_loop)
        update_thread.daemon = True
        update_thread.start()
        
        # Run the main tracker immediately
        # This will block forever running the display
        run_main_tracker()
        
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)