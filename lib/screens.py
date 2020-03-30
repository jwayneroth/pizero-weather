class Screen():
	def __init__(self, display=None, debug=False):
		self.display = display
		self.debug = debug
		self.image = None

	def render(self):
		if self.display:
			display.set_image(self.image)
			display.show()

class CurrentWeather(Screen):
	def __init__(self, icon=None, display=None, debug=False):
		Screen.__init__(self, display, debug)

class ForecastDays(Screen):
	def __init__(self, display=None, debug=False):
		Screen.__init__(self, display, debug)