from datetime import datetime, timedelta
from urllib.request import urlopen
from xml.dom import minidom
import json
import pzwglobals

logger = pzwglobals.logger

"""
map noaa icon names to names of our custom icons ( our set is much smaller :) )
"""
NOAA_ICON_MAP = {
	'bkn': 'cloudy-day',
	'blizzard': 'blizzard',
	'blowingsnow': 'blizzard',
	'br': 'cloudy-day',
	'cloudy': 'cloudy',
	'cloudynight': 'cloudy-night',
	'cold': 'cold',
	'drizzle': 'rain',
	'du': 'fog',
	'dust': 'fog',
	#'error',
	'fair': 'sun',
	'fdrizzle': 'rain',
	'few': 'cloudy-day',
	'fg': 'fog',
	'flurries': 'snow',
	'fog': 'fog',
	'fogn': 'fog',
	'freezingrain': 'rain',
	#'fu',
	'fzra': 'rain',
	'fzrara': 'rain',
	'hazy': 'fog',
	'hi_bkn': 'cloudy-day',
	'hi_clr': 'sun',
	'hi_few': 'cloudy-day',
	'hi_mocldy': 'cloudy-day',
	'hi_moclr': 'sun',
	'hi_nbkn': 'cloudy-night',
	'hi_nclr': 'moon',
	'hi_nfew': 'cloudy-night',
	'hi_nmocldy': 'cloudy-night',
	'hi_nmoclr': 'moon',
	'hi_nptcldy': 'cloudy-night',
	'hi_nsct': 'rain',
	'hi_nshwrs': 'rain',
	'hi_nskc': 'moon',
	'hi_ntsra': 'rain',
	'hi_ptcldy': 'cloudy-night',
	'hi_sct': 'cloudy-night',
	'hi_shwrs': 'rain',
	#'hi_skc',
	'hi_tsra': 'rain',
	'hiclouds': 'cloudy',
	'hot': 'hot',
	#'hurr-noh',
	#'hurr',
	'ip': 'sleet',
	'mcloudy': 'cloudy',
	'mcloudyn': 'cloudy-night',
	'mist': 'sleet',
	'mix': 'sleet',
	#'na',
	#'nbkn',
	#'nbknfg',
	'nfew': 'cloudy',
	#'nfg',
	'nhiclouds': 'cloudy',
	'nmix': 'sleet',
	#'novc',
	'nra': 'rain',
	#'nraip',
	#'nrasn',
	#'nsct',
	'nscttsra': 'rain',
	'nskc': 'rain',
	#'nsn',
	'nsvrtsra': 'rain',
	#'ntor',
	'ntsra': 'rain',
	'nwind': 'wind',
	'ovc': 'cloudy',
	'pcloudy': 'cloudy',
	'pcloudyn': 'cloudy-night',
	'ra': 'rain',
	'radandsat': 'rain',
	'rain': 'rain',
	'rainandsnow': 'sleet',
	'raip': 'sleet',
	'rasn': 'sleet',
	'sct': 'rain',
	'sctfg': 'fog',
	'scttsra': 'rain',
	'showers': 'rain',
	'shra': 'rain',
	#'shsn',
	#'skc',
	'sleet': 'sleet',
	'smoke': 'fog',
	'sn': 'snow',
	'snow': 'snow',
	'snowshowers': 'blizzard',
	'snowshwrs': 'blizzard',
	'sunny': 'sun',
	'sunnyn': 'sun',
	#'tcu',
	#'tor',
	#'tropstorm-noh',
	#'tropstorm',
	'tsra': 'rain',
	'tstorm': 'rain',
	'tstormn': 'rain',
	'wind': 'wind',
	'wswarning': 'blizzard',
	'wswatch': 'blizzard'
}
"""
these noaa icons map to unique icons we like, so they get priority
"""
NOAA_PRIORITY_ICONS = [
	'blizzard',
	'blowingsnow',
	'snowshowers',
	'snowshwrs',
	'cold',
	'hot'
]
NOAA_ENDPOINT = "http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php"
NOAA_FORMAT = "12+hourly"
NOAA_NUM_DAYS = "4"
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
	
		logger.debug('NOAA_URL: ' + NOAA_URL)
	
		self.icon_map = NOAA_ICON_MAP
		
		self.priority_icons = NOAA_PRIORITY_ICONS
		
		try:
			with open(pzwglobals.DATA_DIRECTORY + "noaa.json") as f:
				noaa_log = json.load(f)
		except:
			logger.warning("couldn't open noaa log")
			noaa_log = {}
	
		if "last_load" in noaa_log:
			last_load = datetime.strptime(noaa_log["last_load"], LOG_DATE_FORMAT)
			now = datetime.now()
			tdiff = now - last_load
		
			logger.debug("time difference: " + last_load.strftime(LOG_DATE_FORMAT) + " - " + now.strftime(LOG_DATE_FORMAT))
			logger.debug(tdiff)
		
			if (tdiff < timedelta(minutes=45) or pzwglobals.DEBUG is True):
				logger.info("using logged noaa data")
				self.forecast = {
					'date_names': noaa_log["date_names"],
					'dates_abbr': noaa_log["dates_abbr"],
					'temps': noaa_log["temps"],
					'icons': noaa_log["icons"],
					'summaries': noaa_log["summaries"],
					'last_load': noaa_log["last_load"]
				}
				return None
		
		today = datetime.today()
		
		forecast_dates = [
			today,
			today + timedelta(days=1),
			today + timedelta(days=2),
			today + timedelta(days=3),
		]
		
		self.dates = [fd.strftime("%Y-%m-%d") for fd in forecast_dates]
		
		logger.debug('noaa desired dates: {}'.format(self.dates))
		
		try:
			xmldom = self.getNoaaXmlDom()
			time_layouts = self.parseTimeLayouts(xmldom)
			temps = self.parseTemps(xmldom, time_layouts)
			icons = self.parseIcons(xmldom, time_layouts)
			summaries = self.parseSummaries(xmldom, time_layouts)
			
		except:
			logger.warning('error building forecast')
			
			if "last_load" in noaa_log:
				self.forecast = {
					'date_names': noaa_log["date_names"],
					'dates_abbr': noaa_log["dates_abbr"],
					'temps': noaa_log["temps"],
					'icons': noaa_log["icons"],
					'summaries': noaa_log["summaries"],
					'last_load': noaa_log["last_load"]
				}
			return None

		self.forecast = {
			'date_names': [fd.strftime("%A") for fd in forecast_dates],
			'dates_abbr': [fd.strftime("%m/%d") for fd in forecast_dates],
			'temps': temps,
			'icons': icons,
			'summaries': summaries,
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
	parse time layouts and store in list
	"""
	def parseTimeLayouts(self, dom):
		tl_dict = {}
		time_layouts = dom.getElementsByTagName('time-layout')
		
		for tl in time_layouts:
			
			lk = tl.getElementsByTagName('layout-key')[0]
			
			start_times = tl.getElementsByTagName('start-valid-time')
			
			st_list = []
			
			for i in range(len(start_times)):
				st = start_times[i]
				st_date = st.firstChild.nodeValue[0:10]
				st_list.append(st_date)
			
			tl_dict.update({lk.firstChild.nodeValue: st_list})
		
		return tl_dict
		
	"""
	get days max, min temps
	 we only want one of each for each of our days (today +3)
	"""
	def parseTemps(self, dom, times):
		temps = dom.getElementsByTagName('temperature')
		highs = [None] * 4
		lows = [None] * 4
		
		for item in temps:
			
			if item.getAttribute('type') == 'maximum':
				time_layout = item.getAttribute('time-layout')
				temp_dates = times[time_layout]
				values = item.getElementsByTagName('value')
				for i in range(len(self.dates)):
					date = self.dates[i]
					if date in temp_dates:
						date_index = temp_dates.index(date)
						highs[i] = values[date_index].firstChild.nodeValue
				
			if item.getAttribute('type') == 'minimum':
				time_layout = item.getAttribute('time-layout')
				temp_dates = times[time_layout]
				values = item.getElementsByTagName('value')
				for i in range(len(self.dates)):
					date = self.dates[i]
					if date in temp_dates:
						date_index = temp_dates.index(date)
						lows[i] = values[date_index].firstChild.nodeValue
		
		return [highs, lows]

	"""
	get days of icon names
	 we only want one value for each of our days (today +3)
	"""
	def parseIcons(self, dom, times):
		conditions_icon = dom.getElementsByTagName('conditions-icon')[0]
		time_layout = conditions_icon.getAttribute('time-layout')
		icon_dates = times[time_layout]
		icon_links = conditions_icon.getElementsByTagName('icon-link')
		
		icons = [None] * 4
		
		for i in range(len(self.dates)):
			date = self.dates[i]
			if date in icon_dates:
				date_index = icon_dates.index(date)
				if icon_links[date_index].firstChild is not None:
					icons[i] = icon_links[date_index].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')
		
		return icons

	"""
	get text summaries for our forecast days
	"""
	def parseSummaries(self, dom, times):
		weather = dom.getElementsByTagName('weather')[0]
		time_layout = weather.getAttribute('time-layout')
		weather_dates = times[time_layout]
		weather_values = weather.getElementsByTagName('weather-conditions')
		
		summaries = [""] * 4
		
		for i in range(len(self.dates)):
			date = self.dates[i]
			if date in weather_dates:
				date_index = weather_dates.index(date)
				if weather_values[date_index].getAttribute('weather-summary') is not None:
					summaries[i] = weather_values[date_index].getAttribute('weather-summary')
		
		return summaries
		
	"""
	get date of first forecast day
	"""
	def parseFirstDay(self, dom):
		day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
		return datetime.strptime(day_one, '%Y-%m-%d')














