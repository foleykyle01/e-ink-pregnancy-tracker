#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time
import logging

class ButtonHandler:
    # GPIO pin mappings for the 4 buttons on Waveshare 2.7inch e-Paper HAT
    KEY1_PIN = 5
    KEY2_PIN = 6
    KEY3_PIN = 13
    KEY4_PIN = 19
    
    def __init__(self, callback=None):
        """
        Initialize button handler
        callback: function to call when button is pressed, receives button number (1-4)
        """
        self.callback = callback
        self.last_press_time = {1: 0, 2: 0, 3: 0, 4: 0}
        self.debounce_time = 0.3  # 300ms debounce
        
        try:
            # Clean up any existing GPIO state
            GPIO.cleanup([self.KEY1_PIN, self.KEY2_PIN, self.KEY3_PIN, self.KEY4_PIN])
        except:
            pass  # Ignore if pins weren't previously set up
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # Disable warnings about pins already in use
        
        # Setup pins
        GPIO.setup(self.KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY4_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Remove any existing event detection first
        try:
            GPIO.remove_event_detect(self.KEY1_PIN)
            GPIO.remove_event_detect(self.KEY2_PIN)
            GPIO.remove_event_detect(self.KEY3_PIN)
            GPIO.remove_event_detect(self.KEY4_PIN)
        except:
            pass
        
        # Setup interrupts
        GPIO.add_event_detect(self.KEY1_PIN, GPIO.FALLING, callback=lambda x: self._button_pressed(1), bouncetime=300)
        GPIO.add_event_detect(self.KEY2_PIN, GPIO.FALLING, callback=lambda x: self._button_pressed(2), bouncetime=300)
        GPIO.add_event_detect(self.KEY3_PIN, GPIO.FALLING, callback=lambda x: self._button_pressed(3), bouncetime=300)
        GPIO.add_event_detect(self.KEY4_PIN, GPIO.FALLING, callback=lambda x: self._button_pressed(4), bouncetime=300)
        
        logging.info("Button handler initialized")
    
    def _button_pressed(self, button_num):
        """Handle button press with debouncing"""
        current_time = time.time()
        if current_time - self.last_press_time[button_num] > self.debounce_time:
            self.last_press_time[button_num] = current_time
            logging.info(f"Button {button_num} pressed")
            if self.callback:
                self.callback(button_num)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()