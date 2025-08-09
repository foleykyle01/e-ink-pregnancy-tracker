#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
import time
import logging
import signal
import sys
import argparse
import threading
from waveshare_epd import epd2in7_V2  # Use V2 driver for Rev 2.2 display
from pregnancy_tracker import ScreenUI, Pregnancy

# Parse command line arguments
parser = argparse.ArgumentParser(description='E-ink Pregnancy Tracker')
parser.add_argument('--no-buttons', action='store_true', help='Run without button support')
args = parser.parse_args()

if not args.no_buttons:
    try:
        from pregnancy_tracker.button_handler_simple import ButtonHandler
    except ImportError:
        from pregnancy_tracker.button_handler import ButtonHandler

logging.basicConfig(level=logging.INFO)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

# Global variables for cleanup
epd = None
button_handler = None
screen_ui = None
display_lock = threading.Lock()  # Thread lock for display updates
last_update_time = 0  # Track last display update

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
        except Exception as e:
            logging.error(f"Error putting display to sleep: {e}")
    
    sys.exit(0)

def handle_button_press(button_num):
    """Handle button press and update display"""
    global epd, screen_ui, last_update_time
    
    # Prevent multiple rapid updates
    current_time = time.time()
    if current_time - last_update_time < 2:  # Minimum 2 seconds between updates
        logging.info(f"Button {button_num} press ignored (too soon after last update)")
        return
    
    logging.info(f"Handling button {button_num} press")
    
    # Map button number to page (button 1 = page 0, etc.)
    page_num = button_num - 1
    
    if 0 <= page_num <= 3:
        # Use lock to ensure thread safety
        with display_lock:
            try:
                last_update_time = current_time
                
                # Update the page
                screen_ui.set_page(page_num)
                
                # Redraw the screen
                himage = screen_ui.draw()
                
                # Display the new image (no sleep/wake cycle needed)
                epd.display(epd.getbuffer(himage))
                
                logging.info(f"Display updated to page {page_num + 1}")
                
            except Exception as e:
                logging.error(f"Error updating display: {e}")

# Register signal handlers for clean exit
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

try:
    # Initialize e-ink display
    epd = epd2in7_V2.EPD()
    epd.init()  # Regular black and white mode
    epd.Clear()
    
    # Initialize pregnancy tracker
    pregnancy = Pregnancy(config['expected_birth_date'])
    
    # Initialize screen UI (start with page 0)
    screen_ui = ScreenUI(epd.height, epd.width, pregnancy, current_page=0)
    
    # Draw initial screen
    himage = screen_ui.draw()
    epd.display(epd.getbuffer(himage))
    logging.info("Initial display complete")
    
    # Don't sleep the display when using buttons - keep it ready
    
    if not args.no_buttons:
        # Initialize button handler with callback
        button_handler = ButtonHandler(callback=handle_button_press)
        
        logging.info("Pregnancy tracker started. Press buttons to switch pages.")
        logging.info("Button 1: Progress | Button 2: Size | Button 3: Appointments | Button 4: Baby Info")
        
        # Keep the program running to handle button presses
        while True:
            time.sleep(0.1)
    else:
        logging.info("Pregnancy tracker displayed (no button support). Press Ctrl+C to exit.")
        # Just display and exit after a delay
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

except IOError as e:
    logging.error(f"IO Error: {e}")
    cleanup_and_exit()

except KeyboardInterrupt:
    logging.info("Keyboard interrupt received")
    cleanup_and_exit()

except Exception as e:
    logging.error(f"Unexpected error: {e}")
    cleanup_and_exit()