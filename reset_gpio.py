#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Utility script to reset GPIO pins when they get stuck
Run this if you encounter GPIO errors
"""

import RPi.GPIO as GPIO
import sys

print("Resetting GPIO pins...")

try:
    # Set mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # List of all pins used by the application
    pins_to_reset = [
        5,   # KEY1
        6,   # KEY2
        13,  # KEY3
        19,  # KEY4
        17,  # RST
        25,  # DC
        24,  # BUSY
        18,  # CS
    ]
    
    # Clean up each pin
    for pin in pins_to_reset:
        try:
            GPIO.setup(pin, GPIO.IN)
            GPIO.remove_event_detect(pin)
        except:
            pass
    
    # Final cleanup
    GPIO.cleanup()
    print("GPIO reset complete!")
    
except Exception as e:
    print(f"Error during reset: {e}")
    sys.exit(1)