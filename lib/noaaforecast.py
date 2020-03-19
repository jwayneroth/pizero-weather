from datetime import datetime, timedelta
from urllib.request import urlopen
from xml.dom import minidom
import json
import pzwglobals

logger = pzwglobals.logger

NOAA_ENDPOINT = "http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php"
NOAA_FORMAT = "12+hourly"
NOAA_NUM_DAYS = "1"
NOAA_QUERY = "whichClient=NDFDgenByDay&lat=" + pzwglobals.LATITUDE + "&lon=" + pzwglobals.LONGITUDE + "&format=" + NOAA_FORMAT + "&numDays=" + NOAA_NUM_DAYS + "&Unit=e"
NOAA_URL = NOAA_ENDPOINT + "?" + NOAA_QUERY

LOG_DATE_FORMAT = '%Y%m%d%H%M%S'

"""
NoaaForecast

	parse NOAA location based xml for min, max temps and forecast icon
	store data on public prop forecast
"""
class NoaaForecast():
	def __init__(self):
		
		print('NOAA_URL: ' + NOAA_URL)
		
		try:
			with open(pzwglobals.DATA_DIRECTORY + "noaa.json") as f:
				noaa_log = json.load(f)
		except:
			noaa_log = {}
		
		if "last_load" in noaa_log:
			last_load = datetime.strptime(noaa_log["last_load"], LOG_DATE_FORMAT)
			now = datetime.now()
			tdiff = now - last_load
			
			#print("time difference: " + last_load.strftime(LOG_DATE_FORMAT) + " - " + now.strftime(LOG_DATE_FORMAT))
			#print(tdiff)
			
			if (tdiff < timedelta(minutes=45)):
				logger.debug("using logged noaa data")
				self.forecast = {
					'temps': noaa_log["temps"],
					'icons': noaa_log["icons"],
					'date': datetime.strptime(noaa_log["date"], '%Y-%m-%d')
				}
				return None
		
		xmldom = self.getNoaaXmlDom()
		temps = self.parseTemps(xmldom)
		icons = self.parseIcons(xmldom)
		date = self.parseFirstDay(xmldom)
		
		self.forecast = {
			'temps': temps,
			'icons': icons,
			'date':  datetime.strftime(date, '%Y-%m-%d'),
			'last_load': datetime.now().strftime(LOG_DATE_FORMAT)
		}
		
		with open(pzwglobals.DATA_DIRECTORY + "noaa.json", 'w') as f:
			json.dump(self.forecast, f)
			
		return None

	"""
	load xml and parse with minidom
	"""
	def getNoaaXmlDom(self):
		xml = urlopen(NOAA_URL).read()
		dom = minidom.parseString(xml)
		return dom

	"""
	get days max, min temps
	"""
	def parseTemps(self, dom):
		temps = dom.getElementsByTagName('temperature')
		highs = [] #[None] * 4
		lows = [] #[None] * 4
		for item in temps:
				if item.getAttribute('type') == 'maximum':
					values = item.getElementsByTagName('value')
					for i in range(len(values)):
						highs.append(int(values[i].firstChild.nodeValue))
				if item.getAttribute('type') == 'minimum':
					values = item.getElementsByTagName('value')
					for i in range(len(values)):
						lows.append(int(values[i].firstChild.nodeValue))
		return [highs, lows]

	"""
	get days of icon names
	"""
	def parseIcons(self, dom):
		icon_links = dom.getElementsByTagName('icon-link')
		icons = [] #[None] * 4
		for i in range(len(icon_links)):
			print(icon_links[i])
			if icon_links[i].firstChild is not None:
				icons.append(icon_links[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789'))
		return icons

	"""
	get date of first forecast day
	"""
	def parseFirstDay(self, dom):
		day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
		return datetime.strptime(day_one, '%Y-%m-%d')














