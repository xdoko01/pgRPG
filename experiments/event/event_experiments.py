# Scenario - our object - character - calls its function send_event. Sent event re-calls  EventDispatcher (Engine)
# function Send_event and by doing so, the Event dispatcher distributes the event to all registered objects by running their
# even_handler method
class Event:
	
	type = [e_increment_score, e_game_over]

	self.type
	self.arguments

class EventHandler:
	""" Somebody who wants to listen - QUEST wants to listen
	"""
	def event_handler(self, event):

		if event.type == ....:
			...

class EventDispatcher:
	""" Somebody who is sending the messages. ENGINE (it is singleton) can be good for this
	"""
	list_of_listeners

	def register_handler(self, event_handler):
		pass

	def send_event(self, event_type, arguments):
		pass
