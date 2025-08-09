#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time
import logging
import threading

class ButtonHandler:
    # GPIO pin mappings for the 4 buttons on Waveshare 2.7inch e-Paper HAT
    KEY1_PIN = 5
    KEY2_PIN = 6
    KEY3_PIN = 13
    KEY4_PIN = 19
    
    def __init__(self, callback=None):
        """
        Initialize button handler with polling instead of interrupts
        callback: function to call when button is pressed, receives button number (1-4)
        """
        self.callback = callback
        self.last_press_time = {1: 0, 2: 0, 3: 0, 4: 0}
        self.debounce_time = 0.5  # 500ms debounce
        self.running = True
        
        # Setup GPIO without interrupts
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup pins as inputs with pull-up resistors
        self.pins = {
            1: self.KEY1_PIN,
            2: self.KEY2_PIN,
            3: self.KEY3_PIN,
            4: self.KEY4_PIN
        }
        
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Start polling thread
        self.poll_thread = threading.Thread(target=self._poll_buttons)
        self.poll_thread.daemon = True
        self.poll_thread.start()
        
        logging.info("Button handler initialized (polling mode)")
    
    def _poll_buttons(self):
        """Poll buttons for state changes"""
        button_states = {1: 1, 2: 1, 3: 1, 4: 1}  # Initialize as not pressed (HIGH)
        
        while self.running:
            for button_num, pin in self.pins.items():
                current_state = GPIO.input(pin)
                
                # Check if button was just pressed (transition from HIGH to LOW)
                if button_states[button_num] == 1 and current_state == 0:
                    current_time = time.time()
                    # Check debounce
                    if current_time - self.last_press_time[button_num] > self.debounce_time:
                        self.last_press_time[button_num] = current_time
                        logging.info(f"Button {button_num} pressed")
                        if self.callback:
                            # Call callback in a separate thread to avoid blocking
                            threading.Thread(target=self.callback, args=(button_num,)).start()
                
                button_states[button_num] = current_state
            
            time.sleep(0.05)  # Poll every 50ms
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.running = False
        time.sleep(0.1)  # Give polling thread time to stop
        # Don't call GPIO.cleanup() here as it might interfere with display