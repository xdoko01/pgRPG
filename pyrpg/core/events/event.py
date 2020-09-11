import pyrpg.core.engine as engine

from pyrpg.core.config.config import MSG_EVENT_FORMAT # for the format of event messages

class Event:
	''' Class encapsulating event sent by event dispatcher
	'''

	EVENT_TYPES = ['COLLISION', 'TELEPORTATION', 'ITEM_PICKUP',\
		 'WEARABLE_WEARED', 'WEAPON_ARMED', 'DAMAGE', 'KILL',\
		 'QUEST_START', 'PHASE_START']
	

	def __init__(self, event_type, generator_obj, other_obj, params={}):

		assert(event_type in Event.EVENT_TYPES)

		self.event_type = event_type
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params
	
	def __str__(self):
		return f'*Event type:\t{self.event_type}\nSource entity:\t{self.generator_obj}\nDestination entity:\t{self.other_obj}\nParams:\t{self.params}\n'

	def to_string(self):
		''' If format of the event message is not present in json config file 
		or config module, empty string is returned and no message is displayed.
		'''

		# Get the event msg format - from config files - it is ok not to fill any parameter
		event_msg_format = MSG_EVENT_FORMAT.get(self.event_type, ['',[]])
		
		# Decode the message
		return event_msg_format[0].format(*[engine.entity_to_alias.get(getattr(self, var_name)) for var_name in event_msg_format[1]])