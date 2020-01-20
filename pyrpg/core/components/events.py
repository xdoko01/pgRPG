class Event:
	""" Class encapsulating event sent by event dispatcher
	"""
	def __init__(self, generator_obj, other_obj, params={}):
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params


class EventHandler:
	""" Implementation of the Observer pattern. 
	Class implementing the listener functionality.
	"""

	def event_handler(self, event):
		pass

