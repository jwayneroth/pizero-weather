from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json
import pzwglobals

logger = pzwglobals.logger

"""
map darksky icon names to names of our custom icons
"""
DARK_SKY_ICON_MAP = {
	'clear-day': 'sun',
	'clear-night': 'moon',
	'partly-cloudy-day': 'cloudy-day',
	'partly-cloudy-night': 'cloudy-night',
	'cloudy': 'cloudy',
	'rain': 'rain',
	'sleet': 'sleet',
	'snow': 'snow',
	'wind': 'wind',
	'fog': 'fog',
	'hail': 'hail'
	#'thunderstorm',
	#'tornado'
}

DARK_SKY_URL = "https://darksky.net/forecast/{}/us12/en".format(",".join([pzwglobals.LATITUDE, pzwglobals.LONGITUDE]))

LOG_DATE_FORMAT = '%Y%m%d%H%M%S'

"""
DarkSkyWeather

	lightly adapted from InkyPhat example script
	scrape darksky for temp, summary-icon, pressure and humidity
	store data on public prop weather
"""
class DarkSkyWeather():
	def __init__(self, debug=False):
		self.icon_map = DARK_SKY_ICON_MAP
		
		try:
			with open(pzwglobals.DATA_DIRECTORY + "darksky.json") as f:
				drksky_log = json.load(f)
		except:
			logger.warning("couldn't open darksky log")
			drksky_log = {}
	
		if drksky_log is not None and "last_load" in drksky_log:
			last_load = datetime.strptime(drksky_log["last_load"], LOG_DATE_FORMAT)
			now = datetime.now()
			tdiff = now - last_load
		
			logger.debug("time difference: " + last_load.strftime(LOG_DATE_FORMAT) + " - " + now.strftime(LOG_DATE_FORMAT))
			logger.debug(tdiff)
			
			if (tdiff < timedelta(minutes=10) or debug is True):
				logger.info("using logged darksky data")
				self.weather = {
					'summary': drksky_log["summary"],
					'temperature': drksky_log["temperature"],
					'pressure': drksky_log["pressure"],
					'humidity': drksky_log["humidity"],
					'last_load': drksky_log["last_load"]
				}
				return None
				
		self.weather = self.get_weather()
		
		self.weather['last_load'] = datetime.now().strftime(LOG_DATE_FORMAT)

		with open(pzwglobals.DATA_DIRECTORY + "darksky.json", 'w') as f:
			json.dump(self.weather, f)
			
		return None
	"""
	Query Dark Sky (https://darksky.net/) to scrape current weather data
	"""
	def get_weather(self):
		weather = {}
		res = requests.get(DARK_SKY_URL)
		if res.status_code == 200:
			soup = BeautifulSoup(res.content, "lxml")
			curr = soup.find_all("span", "currently")
			weather["summary"] = curr[0].img["alt"].split()[0]
			weather["temperature"] = int(curr[0].find("span", "summary").text.split()[0][:-1])
			press = soup.find_all("div", "pressure")
			weather["pressure"] = int(press[0].find("span", "num").text)
			hum = soup.find_all("div", "humidity")
			weather["humidity"] = int(hum[0].find("span", "num").text)
			return weather
		return None
