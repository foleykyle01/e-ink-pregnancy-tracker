#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Main script with sequential GPIO initialization
Initializes display first, then buttons to avoid conflicts
"""
import json
import os
import time
import logging
import signal
import sys

# Set logging to only show warnings and errors, not info messages
logging.basicConfig(level=logging.WARNING)

# Load config first
config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

# Global variables
epd = None
button_handler = None
screen_ui = None
pregnancy = None

def cleanup_and_exit(signum=None, frame=None):
    """Clean up resources and exit"""
    global epd, button_handler
    
    if button_handler:
        try:
            button_handler.cleanup()
        except:
            pass
    
    if epd:
        try:
            epd.sleep()
        except:
            pass
    
    sys.exit(0)

def update_display(page_num):
    """Update display to specified page"""
    global epd, screen_ui
    
    try:
        screen_ui.set_page(page_num)
        himage = screen_ui.draw()
        epd.display(epd.getbuffer(himage))
    except Exception as e:
        logging.error(f"Display update error: {e}")

# Register signal handlers
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

try:
    # Step 1: Initialize display FIRST
    from waveshare_epd import epd2in7_V2
    epd = epd2in7_V2.EPD()
    epd.init()
    epd.Clear()
    
    # Step 2: Setup pregnancy tracker and UI
    from pregnancy_tracker import ScreenUI, Pregnancy
    pregnancy = Pregnancy(config['expected_birth_date'])
    screen_ui = ScreenUI(epd.height, epd.width, pregnancy, current_page=0)
    
    # Step 3: Show initial screen
    himage = screen_ui.draw()
    epd.display(epd.getbuffer(himage))
    
    # Step 4: Now try to initialize buttons AFTER display is set up
    try:
        # Import RPi.GPIO directly to avoid conflicts
        import RPi.GPIO as GPIO
        
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Button pins
        buttons = {1: 5, 2: 6, 3: 13, 4: 19}
        
        # Setup buttons
        for btn, pin in buttons.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Simple polling loop
        button_states = {btn: 1 for btn in buttons}
        last_press_time = 0
        
        while True:
            for btn, pin in buttons.items():
                current = GPIO.input(pin)
                # Button pressed (LOW)
                if current == 0 and button_states[btn] == 1:
                    current_time = time.time()
                    if current_time - last_press_time > 1:  # 1 second debounce
                        last_press_time = current_time
                        update_display(btn - 1)
                button_states[btn] = current
            time.sleep(0.05)
            
    except ImportError:
        # RPi.GPIO not available - running without buttons
        while True:
            time.sleep(1)
    except Exception as e:
        logging.error(f"Button initialization failed: {e}")
        while True:
            time.sleep(1)

except Exception as e:
    logging.error(f"Fatal error: {e}")
    import traceback
    traceback.print_exc()
    cleanup_and_exit()