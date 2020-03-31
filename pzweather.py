#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime, timedelta
import time
import threading
import queue
import argparse
from PIL import Image, ImageDraw, ImageFont
import pzwglobals

if pzwglobals.RUN_ON_RASPBERRY_PI:
	from inky import InkyPHAT
	import RPi.GPIO as GPIO
	BTN_PIN = 21
	btn_down = False

from lib.satelliteimage import SatelliteImage
from lib.noaaforecast import NoaaForecast
from lib.darkskyweather import DarkSkyWeather
from lib.screens import *

logger = pzwglobals.logger

EXIT_COMMAND = 'exit'

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', type=str, required=False, choices=['true', 'True', 'false', 'False'], help="run in debug mode") 
parser.add_argument('--icon', '-i', type=str, required=False, choices=['wind', 'sun', 'snowflake', 'sleet', 'rain', 'moon', 'hot', 'hail', 'fog', 'cold', 'cloudy', 'cloudy-night', 'cloudy-day', 'cloud', 'blizzard'], help="force a specific weather icon to display")
parser.add_argument('--dither', '-a', type=str, required=False, choices=['bayer', 'cluster', 'yliluoma'], help="set a dither algorithm for the background")
parser.add_argument('--threshold', '-t', type=int, required=False, choices=[128, 64, 32], help="set the dither algorithm threshold for dithering")
args = parser.parse_args()

"""
small thread to handle keyboard input on desktop
 as seen here: https://stackoverflow.com/questions/5404068/how-to-read-keyboard-input/53344690#53344690
"""
def read_kbd_input(input_queue):
	logger.debug('starting keyboard thread')
	print('Type exit to quit or anything else to toggle screens.')
	while (True):
		input_str = input()
		input_queue.put(input_str)

def handle_gpio_press(btn):
	btn_down = True

"""
main app class
 maintains screen instances. handles switching screens
"""
class PzWeather():
	def __init__(self):
		self.debug = False
		self.display = None
		self.current = None
		self.last = None
		self.last_load = None
		self.bg = None
		self.noaa = None
		self.darksky = None
		
		if args.debug is 'true' or args.debug is 'True':
			self.debug = True
		
		if pzwglobals.RUN_ON_RASPBERRY_PI:
			self.display = InkyPHAT("yellow")
			self.display.set_border(WHITE)
		
		self.screens = {
			'current_weather': CurrentWeather('current_weather', debug=self.debug, display=self.display),
			'forecast_days': ForecastDays('forecast_days', debug=self.debug, display=self.display) 
		}

	def change_screen(self, screen_name):
		logger.debug('PzWeather::change_screen \t' + screen_name)
		self.make_current_scene(self.screens[screen_name])

	def make_current_scene(self, screen):
		logger.debug('PzWeather::make_current_scene \t' + screen.name)
		if self.current:
			self.last = self.current
		self.current = screen
		self.render_current_screen()

	def render_current_screen(self):
		if self.current is not None:
			if self.current.name == 'confirm':
				self.current.render(bg=self.bg.copy())
			else:
				self.current.render(bg=self.bg.copy(), darksky=self.darksky, noaa=self.noaa, icon=args.icon)
	
	# do time check to update data
	def check_time(self):
		now = datetime.now()
		tdiff = now - self.last_load
		if (tdiff >= timedelta(minutes=10)):
			self.load_data()
			self.render_current_screen()
	
	def load_data(self):
		logger.debug('PzWeather::load_data')
		self.bg = SatelliteImage(args.dither, args.threshold, debug=self.debug).image
		self.noaa = NoaaForecast(debug=self.debug).forecast
		self.darksky = DarkSkyWeather(debug=self.debug).weather
		
		logger.debug(self.noaa)
		logger.debug(self.darksky)
		
		self.last_load = datetime.now()
		
	def toggle_screens(self):
		logger.debug('PzWeather::toggle_screens')
		if self.current and self.current.name == 'current_weather':
			self.change_screen('forecast_days')
			return
		self.change_screen('current_weather')
	
	# helper to exit program in case we need special rpi consideration in future
	def kill():
		if pzwglobals.RUN_ON_RASPBERRY_PI:
			sys.exit(0)
		else:
			sys.exit(0)

"""
main
"""
if __name__ == '__main__':
	logger.info('pizero weather started at ' + datetime.now().strftime("%m/%d/%Y %I:%M %p"))
	
	# init ui for pi and desktop for switching screens, exit / shutdown
	if pzwglobals.RUN_ON_RASPBERRY_PI:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup( BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(BTN_PIN, GPIO.FALLING, handle_gpio_press, bouncetime=20)
	else:
		input_queue = queue.Queue()
		input_thread = threading.Thread(target=read_kbd_input, args=(input_queue,), daemon=True)
		input_thread.start()
	
	# init app and render current weather screen
	pzweather = PzWeather()
	pzweather.load_data()
	pzweather.change_screen('current_weather')
	
	# main loop
	while (True):
		
		# check ui
		if pzwglobals.RUN_ON_RASPBERRY_PI:
			if btn_down is True:
				logger.info('gpio button down')
		else:
			if (input_queue.qsize() > 0):
				input_str = input_queue.get()
				logger.debug("input_str = {}".format(input_str))
				if (input_str == EXIT_COMMAND):
					pzweather.kill()
				else:
					print('switching screens...')
					pzweather.toggle_screens()
				
		pzweather.check_time()
		
		time.sleep(0.2) 
	
	pzweather.kill()






