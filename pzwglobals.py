import os
import logging

LATITUDE = "40.74307"
LONGITUDE = "-73.9182"

RUN_ON_RASPBERRY_PI = os.uname()[4][:3] == 'arm'

HOME_DIR = os.path.expanduser("~")

IMG_DIRECTORY = os.path.dirname(__file__) + '/images/'
FONT_DIRECTORY = os.path.dirname(__file__) + '/fonts/'
DATA_DIRECTORY = os.path.dirname(__file__) + '/data/'

DISPLAY_WIDTH = 212
DISPLAY_HEIGHT = 104

formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

fh = logging.FileHandler(DATA_DIRECTORY + 'pz_weather.log', 'a')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger = logging.getLogger('pz_weather_logger')
if RUN_ON_RASPBERRY_PI:
	logger.setLevel(logging.INFO)
else:
	logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(fh)

"""
map darksky icon names to names of our custom icons
"""
DARKSKY_ICON_MAP = {
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