#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
import time
import logging
import signal
import sys
from waveshare_epd import epd2in7_V2  # Use V2 driver for Rev 2.2 display
from pregnancy_tracker import ScreenUI, Pregnancy
from pregnancy_tracker.button_handler import ButtonHandler

logging.basicConfig(level=logging.WARN)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

# Global variables for cleanup
epd = None
button_handler = None
screen_ui = None

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
    global epd, screen_ui
    
    logging.info(f"Handling button {button_num} press")
    
    # Map button number to page (button 1 = page 0, etc.)
    page_num = button_num - 1
    
    if 0 <= page_num <= 3:
        screen_ui.set_page(page_num)
        
        # Redraw the screen
        himage = screen_ui.draw()
        
        # Wake up the display if it's sleeping
        epd.init()
        
        # Display the new image
        epd.display(epd.getbuffer(himage))
        
        # Put display back to sleep to save power
        time.sleep(2)
        epd.sleep()

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
    time.sleep(2)
    
    # Put display to sleep to save power
    epd.sleep()
    
    # Initialize button handler with callback
    button_handler = ButtonHandler(callback=handle_button_press)
    
    logging.info("Pregnancy tracker started. Press buttons to switch pages.")
    logging.info("Button 1: Progress | Button 2: Size | Button 3: Appointments | Button 4: Baby Info")
    
    # Keep the program running to handle button presses
    while True:
        time.sleep(0.1)

except IOError as e:
    logging.error(f"IO Error: {e}")
    cleanup_and_exit()

except KeyboardInterrupt:
    logging.info("Keyboard interrupt received")
    cleanup_and_exit()

except Exception as e:
    logging.error(f"Unexpected error: {e}")
    cleanup_and_exit()