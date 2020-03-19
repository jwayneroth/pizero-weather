#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from PIL import Image, ImageDraw, ImageFont
import pzwglobals

if pzwglobals.RUN_ON_RASPBERRY_PI:
	from inky import InkyPHAT

from lib.satelliteimage import SatelliteImage
from lib.noaaforecast import NoaaForecast
from lib.darkskyweather import DarkSkyWeather

logger = pzwglobals.logger

BLACK = 1
WHITE = 0
RED = 2

LR_PADDING = 20
TB_PADDING = 12

FONT_SIZE = 26
FONT_Y_OFFSET = 6

"""
helper to exit program in case we need special rpi consideration in future
"""
def kill():
	if pzwglobals.RUN_ON_RASPBERRY_PI:
		sys.exit(0)
	else:
		sys.exit(0)

"""
Create a transparency mask.

	Takes a paletized source image and converts it into a mask
	permitting all the colours supported by Inky pHAT (0, 1, 2)
	or an optional list of allowed colours.

	:param mask: Optional list of Inky pHAT colours to allow.
"""
def create_mask(source, mask=(WHITE, BLACK, RED)):
	mask_image = Image.new("1", source.size)
	w, h = source.size
	for x in range(w):
		for y in range(h):
			p = source.getpixel((x, y))
			if p in mask:
				mask_image.putpixel((x, y), 255)
	return mask_image

"""
render a string onto our surface
	measure width to figure x point if right aligned
	render in white first for ersatz dropshadow, then black

	:param string: text to render
	:param xy: tuple with top and right or left corner
	:param align: optional align left or right
"""
def draw_text(string, xy, align="left"):
	over = 2
	x,y = xy
	if align is "right":
		w,h = draw.textsize(string, font=font)
		x = x - w
	cx = x
	for c in string:
		draw.text((cx-over,y-over), c, WHITE, font=font)
		draw.text((cx,y-over), c, WHITE, font=font)
		draw.text((cx+over,y-over), c, WHITE, font=font)
		draw.text((cx-over,y), c, WHITE, font=font)
		draw.text((cx+over,y), c, WHITE, font=font)
		draw.text((cx-over,y+over), c, WHITE, font=font)
		draw.text((cx,y+over), c, WHITE, font=font)
		draw.text((cx+over,y+over), c, WHITE, font=font)
		cw = draw.textsize(c, font=font)[0]
		cx = cx + cw
	cx = x
	for c in string:
		draw.text((cx,y), c, BLACK, font=font)
		cw = draw.textsize(c, font=font)[0]
		cx = cx + cw

"""
main
"""
if __name__ == '__main__':
	logger.info('pizero weather started at ' + time.strftime("%m/%d/%Y %I:%M %p"))

	bg = SatelliteImage().image

	forecast = NoaaForecast().forecast
	current = DarkSkyWeather().weather
	
	logger.debug(forecast)
	logger.debug(current)
	
	draw = ImageDraw.Draw(bg)

	font = ImageFont.truetype(pzwglobals.FONT_DIRECTORY + "Impact.ttf", FONT_SIZE)
	
	date = time.strftime("%m/%d")
	if date[0] is "0":
		date = date[1:]
	
	time = time.strftime("%I:%M %p")
	if time[0] is "0":
		time = time[1:]
	
	draw_text(date, (LR_PADDING, TB_PADDING - FONT_Y_OFFSET))
	draw_text(time, (pzwglobals.DISPLAY_WIDTH - LR_PADDING - 2, TB_PADDING - FONT_Y_OFFSET), align="right")

	if current is not None:
		if "temperature" in current:
			temp_str = u"{}°".format(current["temperature"])
			mid_y = int(pzwglobals.DISPLAY_HEIGHT / 2) - int(draw.textsize(temp_str, font=font)[1] / 2) - int(FONT_Y_OFFSET / 2)
			draw_text(temp_str, (pzwglobals.DISPLAY_WIDTH - LR_PADDING - 12, mid_y), align="right")

		if "humidity" in current:
			bottom_y = pzwglobals.DISPLAY_HEIGHT - TB_PADDING -  draw.textsize(temp_str, font=font)[1]
			draw_text("{} %".format(current["humidity"]), (pzwglobals.DISPLAY_WIDTH - LR_PADDING, bottom_y), align="right")

	if "icons" in forecast and len(forecast["icons"]) > 0:
		try:
			icon = pzwglobals.IMG_DIRECTORY + "icons/" + forecast["icons"][0] + ".png"
			icon_img = Image.open(icon)
			mask = create_mask(icon_img)
			bg.paste(icon_img, (LR_PADDING + 2, 44), mask)
		except:
			pass

	if not pzwglobals.RUN_ON_RASPBERRY_PI:
		bg.save(pzwglobals.IMG_DIRECTORY + 'pz-weather.png')
		kill()

	inky_display = InkyPHAT("yellow")
	inky_display.set_border(WHITE)

	inky_display.set_image(bg)
	inky_display.show()

	kill()






