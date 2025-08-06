#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
import time
import logging
from waveshare_epd import epd2in7_V2  # Use V2 driver for Rev 2.2 display
from pregnancy_tracker import ScreenUI, Pregnancy

logging.basicConfig(level=logging.WARN)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

try:
    epd = epd2in7_V2.EPD()
    epd.init()  # Regular black and white mode
    epd.Clear()

    pregnancy = Pregnancy(config['expected_birth_date'])

    screen_ui = ScreenUI(epd.height, epd.width, pregnancy)
    himage = screen_ui.draw()
    
    # Display in regular mode
    epd.display(epd.getbuffer(himage))
    time.sleep(2)

    epd.sleep()

except IOError as e:
    logging.info(e)

