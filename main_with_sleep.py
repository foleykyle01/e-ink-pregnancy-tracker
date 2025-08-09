#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Alternative main script with power-saving sleep mode
Display sleeps after 5 minutes of inactivity and wakes on button press
"""
import json
import os
import time
import logging
import signal
import sys
import argparse
import threading
from waveshare_epd import epd2in7_V2
from pregnancy_tracker import ScreenUI, Pregnancy

# Parse command line arguments
parser = argparse.ArgumentParser(description='E-ink Pregnancy Tracker with Sleep Mode')
parser.add_argument('--no-buttons', action='store_true', help='Run without button support')
parser.add_argument('--sleep-timeout', type=int, default=300, help='Seconds before display sleeps (default: 300)')
args = parser.parse_args()

if not args.no_buttons:
    try:
        from pregnancy_tracker.button_handler_simple import ButtonHandler
    except ImportError:
        from pregnancy_tracker.button_handler import ButtonHandler

logging.basicConfig(level=logging.INFO)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

# Global variables
epd = None
button_handler = None
screen_ui = None
display_lock = threading.Lock()
last_activity_time = time.time()
display_sleeping = False
current_page = 0

def cleanup_and_exit(signum=None, frame=None):
    """Clean up resources and exit"""
    global epd, button_handler
    logging.info("Cleaning up...")
    
    if button_handler:
        try:
            button_handler.cleanup()
        except Exception as e:
            logging.error(f"Error cleaning up buttons: {e}")
    
    if epd:
        try:
            epd.sleep()
            epd.module_exit()
        except Exception as e:
            logging.error(f"Error cleaning up display: {e}")
    
    sys.exit(0)

def wake_display():
    """Wake the display from sleep"""
    global epd, display_sleeping
    if display_sleeping:
        logging.info("Waking display...")
        epd.init()
        display_sleeping = False

def sleep_display():
    """Put display to sleep"""
    global epd, display_sleeping
    if not display_sleeping:
        logging.info("Display going to sleep...")
        epd.sleep()
        display_sleeping = True

def handle_button_press(button_num):
    """Handle button press and update display"""
    global epd, screen_ui, last_activity_time, current_page, display_sleeping
    
    last_activity_time = time.time()
    
    logging.info(f"Button {button_num} pressed")
    
    # Map button number to page
    page_num = button_num - 1
    
    if 0 <= page_num <= 3:
        with display_lock:
            try:
                # Wake display if sleeping
                if display_sleeping:
                    wake_display()
                    time.sleep(0.1)  # Small delay after wake
                
                # Only update if page changed
                if page_num != current_page:
                    current_page = page_num
                    screen_ui.set_page(page_num)
                    himage = screen_ui.draw()
                    epd.display(epd.getbuffer(himage))
                    logging.info(f"Display updated to page {page_num + 1}")
                
            except Exception as e:
                logging.error(f"Error updating display: {e}")

def sleep_monitor():
    """Monitor activity and sleep display after timeout"""
    global last_activity_time, display_sleeping
    
    while True:
        time.sleep(10)  # Check every 10 seconds
        
        if not display_sleeping:
            idle_time = time.time() - last_activity_time
            if idle_time > args.sleep_timeout:
                with display_lock:
                    sleep_display()

# Register signal handlers
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

try:
    # Initialize display
    epd = epd2in7_V2.EPD()
    epd.init()
    epd.Clear()
    
    # Initialize pregnancy tracker
    pregnancy = Pregnancy(config['expected_birth_date'])
    
    # Initialize screen UI
    screen_ui = ScreenUI(epd.height, epd.width, pregnancy, current_page=0)
    
    # Draw initial screen
    himage = screen_ui.draw()
    epd.display(epd.getbuffer(himage))
    logging.info("Initial display complete")
    
    if not args.no_buttons:
        # Initialize button handler
        button_handler = ButtonHandler(callback=handle_button_press)
        
        # Start sleep monitor thread
        sleep_thread = threading.Thread(target=sleep_monitor)
        sleep_thread.daemon = True
        sleep_thread.start()
        
        logging.info(f"Tracker started. Display sleeps after {args.sleep_timeout}s of inactivity.")
        logging.info("Buttons: 1=Progress | 2=Size | 3=Appointments | 4=Baby Info")
        
        # Keep running
        while True:
            time.sleep(0.1)
    else:
        logging.info("Display shown (no button support). Press Ctrl+C to exit.")
        epd.sleep()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

except Exception as e:
    logging.error(f"Unexpected error: {e}")
    cleanup_and_exit()