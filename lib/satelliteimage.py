import os
import time
import re
from urllib.request import urlretrieve
import requests
from xml.dom import minidom
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import pzwglobals

DEFAULT_BG = pzwglobals.IMG_DIRECTORY + 'default-bg.png'

NOAA_IMG_URL = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/ne/GEOCOLOR/"

CROP_LEFT = 593
CROP_TOP = 508
BG_WIDTH = 212
BG_HEIGHT = 104

logger = pzwglobals.logger

"""
SatelliteImage

	attempt to download latest NOAA satellite image
	crop and dither it for Inky display
	store new image or local default on public prop image
"""
class SatelliteImage():
	def __init__(self):
		url = self.getLatestImageUrl()
		
		if not url:
			self.image = self.getDefault()
			return None
		
		img = self.downloadLatest(url)
		
		if not img:
			self.image = self.getDefault()
			return None
		
		self.image = self.doCropAndIndex(img)
		
		return None

	"""
	 find latest 1200 x 1200 satellite image on server
	"""
	def getLatestImageUrl(self):
		res = requests.get(NOAA_IMG_URL)
		if res.status_code == 200:
			soup = BeautifulSoup(res.content, 'html.parser')
			img_urls = soup.find_all('a', string=re.compile("1200x1200"))
			if not img_urls:
				logger.warning('Error: no image urls found')
				return None
			logger.debug('latest image anchor: ')
			logger.debug(img_urls[-1])
			return NOAA_IMG_URL + img_urls[-1]['href']
		return None
	
	"""
	 download latest satellite image
	"""
	def downloadLatest(self, url):
		sat_img_localname = "noaa-download" + time.strftime("%Y%m%d%H%M") + ".jpg"
		try:
			sat_img_local, headers = urlretrieve(url, sat_img_localname)
			img = Image.open(sat_img_local)
			os.remove(sat_img_local)
			return img
		except:
			return None

	"""
	 crop nyc area from satellite image
	 convert rgb image to 3 color indexed image 
	"""
	def doCropAndIndex(self, img):
		img = img.crop((CROP_LEFT, CROP_TOP, CROP_LEFT + BG_WIDTH, CROP_TOP + BG_HEIGHT))
		idx_img = Image.new("P", (1, 1))
		idx_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)
		img2 = img.quantize(palette=idx_img)
		return img2

	"""
	 use default satellite background
	"""
	def getDefault(self):
		return Image.open(DEFAULT_BG)