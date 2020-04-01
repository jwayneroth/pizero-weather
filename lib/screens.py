from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap
import pzwglobals

logger = pzwglobals.logger

BLACK = 1
WHITE = 0
RED = 2

LR_PADDING = 20
TB_PADDING = 12

FONT_SIZE = 26
FONT_SIZE_SMALL = 18
FONT_Y_OFFSET = 6

ICON_SIZE_SMALL = 50

class Screen():
	def __init__(self, name='screen', display=None, debug=False):
		self.name = name
		self.display = display
		self.debug = debug
		
		self.font = ImageFont.truetype(pzwglobals.FONT_DIRECTORY + "Impact.ttf", FONT_SIZE)
		self.font_small = ImageFont.truetype(pzwglobals.FONT_DIRECTORY + "Impact.ttf", FONT_SIZE_SMALL)

	def render(self):
		pass

	"""
	Create a transparency mask.

		Takes a paletized source image and converts it into a mask
		permitting all the colours supported by Inky pHAT (0, 1, 2)
		or an optional list of allowed colours.

		:param mask: Optional list of Inky pHAT colours to allow.
	"""
	def create_mask(self, source, mask=(WHITE, BLACK, RED)):
		mask_image = Image.new("1", source.size)
		w, h = source.size
		for x in range(w):
			for y in range(h):
				p = source.getpixel((x, y))
				if p in mask:
					mask_image.putpixel((x, y), 255)
		return mask_image

	"""
	render a string onto our surface with a white border
	
		measure width to figure x point if right aligned
		render in white first for ersatz dropshadow, then black

		:param string: text to render
		:param xy: tuple with top and right or left corner
		:param align: optional align left or right
	"""
	def text_with_border(self, draw, string, xy, align="left", font=None):
		if font is None:
			font = self.font 
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
confirm shutdown screen
"""
class ConfirmScreen(Screen):
	def __init__(self, name, icon=None, display=None, debug=False):
		Screen.__init__(self, name, display, debug)
	
	def render(self):
		bg = Image.new("1", (pzwglobals.DISPLAY_WIDTH, pzwglobals.DISPLAY_HEIGHT), 0)
		msg = 'Shutdown?'
		draw = ImageDraw.Draw(bg)
		mid_y = int(pzwglobals.DISPLAY_HEIGHT / 2) - int(draw.textsize(msg, font=self.font)[1] / 2) - int(FONT_Y_OFFSET / 2)
		self.text_with_border(draw, msg, (LR_PADDING, mid_y))
		
		if self.display is not None:
			self.display.set_image(bg)
			self.display.show()
		else:
			bg.save(pzwglobals.IMG_DIRECTORY + 'pz-weather-confirm.png')

"""
screen class for current weather
"""
class CurrentWeather(Screen):
	def __init__(self, name, icon=None, display=None, debug=False):
		Screen.__init__(self, name, display, debug)

	def render(self, bg, darksky, noaa, icon=None):
		now = datetime.now()
		draw = ImageDraw.Draw(bg)

		date = now.strftime("%m/%d")
		if date[0] is "0":
			date = date[1:]

		time = now.strftime("%I:%M %p")
		if time[0] is "0":
			time = time[1:]

		self.text_with_border(draw, date, (LR_PADDING, TB_PADDING - FONT_Y_OFFSET))
		self.text_with_border(draw, time, (pzwglobals.DISPLAY_WIDTH - LR_PADDING - 2, TB_PADDING - FONT_Y_OFFSET), align="right")

		if darksky is not None:
			if "temperature" in darksky:
				temp_str = u"{}°".format(darksky["temperature"])
				mid_y = int(pzwglobals.DISPLAY_HEIGHT / 2) - int(draw.textsize(temp_str, font=self.font)[1] / 2) - int(FONT_Y_OFFSET / 2)
				self.text_with_border(draw, temp_str, (pzwglobals.DISPLAY_WIDTH - LR_PADDING - 12, mid_y), align="right")

			if "humidity" in darksky:
				bottom_y = pzwglobals.DISPLAY_HEIGHT - TB_PADDING -  draw.textsize(temp_str, font=self.font)[1]
				self.text_with_border(draw, "{} %".format(darksky["humidity"]), (pzwglobals.DISPLAY_WIDTH - LR_PADDING, bottom_y), align="right")

		# current icon
		# we have some noaa icons that take precedence for display
		# otherwise we use our map of darksky icon summaries to our icon images
		# with a fallback noaa icon map

		icon_name = None

		#check if user forced an icon via command line arg
		if icon is not None:
			icon_name = icon

		#else determine icon based on our data
		else:

			#if we have noaa icons, we check them first for priority images
			noaa_icon = noaa["icons"][0]
	
			if noaa_icon is not None:
				if noaa_icon in pzwglobals.NOAA_PRIORITY_ICONS:
					icon_name = pzwglobals.NOAA_ICON_MAP[noaa_icon]
			
			#no priority icon, use the darksky summary icon
			if icon_name is None:
				if "summary" in darksky:
					if darksky["summary"] in pzwglobals.DARKSKY_ICON_MAP:
						icon_name = pzwglobals.DARKSKY_ICON_MAP[darksky["summary"]]

			#something went wrong with darksky, use any noaa icon
			if icon_name is None and noaa_icon is not None:
				if noaa_icon in pzwglobals.NOAA_ICON_MAP:
					icon_name = pzwglobals.NOAA_ICON_MAP[noaa_icon]

		#if we determined an icon, try to load it
		if icon_name is not None:
			try:
				icon = pzwglobals.IMG_DIRECTORY + "icons/" + icon_name + ".png"
				icon_img = Image.open(icon)
				mask = self.create_mask(icon_img)
				bg.paste(icon_img, (LR_PADDING, 40), mask)
			except:
				pass

		if self.display is not None:
			self.display.set_image(bg)
			self.display.show()
		else:
			bg.save(pzwglobals.IMG_DIRECTORY + 'pz-weather-current.png')

"""
screen class for three day forecast
"""
class ForecastDays(Screen):
	def __init__(self, name, display=None, debug=False):
		Screen.__init__(self, name, display, debug)
	
	# print day, high and low, and icon for our forecast days
	def render(self, bg, darksky, noaa, icon=None):
		
		draw = ImageDraw.Draw(bg)
		
		rx = 8 #LR_PADDING
		ry = TB_PADDING - 4 - FONT_Y_OFFSET
		col_width = int((pzwglobals.DISPLAY_WIDTH - 16) / 3)
		line_height = FONT_SIZE + 3
		line_height_small = FONT_SIZE_SMALL + 4
		
		for i in range(1,4):
			self.text_with_border(draw, noaa["date_names"][i][:3], (rx, ry), align="left")
			self.text_with_border(draw, "{}-{}°".format(noaa["temps"][1][i], noaa["temps"][0][i]), (rx, ry + line_height), align="left", font=self.font_small)
			
			if noaa["icons"][i] is not None and noaa["icons"][i] in pzwglobals.NOAA_ICON_MAP:
				icon = pzwglobals.IMG_DIRECTORY + "icons/" + pzwglobals.NOAA_ICON_MAP[noaa["icons"][i]] + ".png"
				icon_img = Image.open(icon)
				mask = self.create_mask(icon_img)
				icon_img.thumbnail((ICON_SIZE_SMALL, ICON_SIZE_SMALL))
				mask.thumbnail((ICON_SIZE_SMALL, ICON_SIZE_SMALL))
				bg.paste(icon_img, (rx, ry + line_height + line_height_small), mask)
			elif noaa["summaries"][i] is not None:
				summary_text = noaa["summaries"][i]
				summary_lines = textwrap.wrap(summary_text, width=9)
				summary_y = ry + line_height + line_height_small
				for s_line in summary_lines:
					s_lineh = draw.textsize(s_line, font=self.font_small)[1]
					self.text_with_border(draw, s_line, (rx, summary_y), align="left", font=self.font_small)
					summary_y = summary_y + s_lineh
		
			rx = rx + col_width
		
		if self.display is not None:
			self.display.set_image(bg)
			self.display.show()
		else:
			bg.save(pzwglobals.IMG_DIRECTORY + 'pz-weather-forecast.png')
