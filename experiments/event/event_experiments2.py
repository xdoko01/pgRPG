"""
Phylosophy
 	Engine class is serving as a EventDispatcher, i.e. it distributes events to all relevant
 	objects - quests, maps, screens using send_event method. Engine.send_event method is invoked
 	by other entities in the game (players, characters). Those entities have also send_event method 
 	implemented and this method is just recalling Engine.send_event.
 	Quests have implemented event_handler method that is invoked by Engine.send_event. This method
 	decides what should happen (if anything) upon receival of the event.
Aim
	Example of processing among Engine, Map, NPC - only logging to console
"""

class Event:
	""" Class encapsulating event sent by event dispatcher
	"""
	def __init__(self, generator_obj, other_obj, params={}):
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params


class EventHandler:
	""" Somebody who wants to listen - Entity wants to listen to hits from other objects
	Map wants to know if entity moves... 
	"""
	def event_handler(self, event):

		if event.type == ....:
			...

class EventDispatcher:
	""" Somebody who is sending the messages. ENGINE (it is singleton) can be good for this
	"""
	list_of_listeners - list of maps, list of entities

	def register_handler(self, event_handler):
		pass

	def send_event(self, event_type, arguments):
		pass

class Engine:
	def __init__(self):
		pass

	def send_event(self, event):
		""" Engine is EventDispatcher implementation. This function sends
		event to every registered Quest instance in Engine.quests dictionary
		by invoking event_handler method on the quest.
		"""

		# TODO - here we can inspect event object and decide to which event handler
		# to send it to (to all/some quests, to all/some maps, to all/some screens)

		# Send the event to all quests 
		for q_key, q_value in quests.items():
			q_value.event_handler(event)

class Map:
	
		def send_event(self, event):
		""" Method generates event and invokes EventDispatcher (Engine class)
		for distributoi of this event to relevant event handlers (quests, maps,
		screens, ...)
		"""
		Engine.send_event(event)

class Entity:
	
	def send_event(self, event):
	""" Method generates event and invokes EventDispatcher (Engine class)
	for distributoi of this event to relevant event handlers (quests, maps,
	screens, ...)
	"""
	Engine.send_event(event)


