class Event:
	''' Class encapsulating event sent by event dispatcher
	'''

	EVENT_TYPES = ['COLLISION', 'TELEPORTATION', 'ITEM_PICKUP', 'WEARABLE_WEARED']

	def __init__(self, event_type, generator_obj, other_obj, params={}):

		assert(event_type in Event.EVENT_TYPES)

		self.event_type = event_type
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params
	
	def __str__(self):
		return f'*Event type:\t{self.event_type}\nSource entity:\t{self.generator_obj}\nDestination entity:\t{self.other_obj}\nParams:\t{self.params}\n'
