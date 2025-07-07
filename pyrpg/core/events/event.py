from pyrpg.core.config import MESSAGES # for the format of event messages

class Event:
	''' Class encapsulating event sent by event dispatcher
	'''

	EVENT_TYPES = ['COLLISION', 'TELEPORTATION', 'ITEM_PICKUP',\
		 'WEARABLE_WEARED', 'WEAPON_ARMED', 'AMMO_PACK_ARMED', 'AMMO_PACK_DISARMED',\
		 'DAMAGE', 'KILL', 'SCORE',\
		 'SCENE_START', 'PHASE_START']


	def __init__(self, event_type, generator_obj, other_obj, params={}):

		#assert(event_type in Event.EVENT_TYPES)

		self.event_type = event_type
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params

	def __str__(self):
		return f'*Event type: "{self.event_type}", Source entity: "{self.generator_obj}", Other entity: "{self.other_obj}", Params: "{self.params}"'

	def to_string(self):
		''' If format of the event message is not present in json config file
		or config module, empty string is returned and no message is displayed.
		'''

		# Get the event msg format - from config files - it is ok not to fill any parameter
		event_msg_format = MESSAGES["ON_EVENT"].get(self.event_type, ['', []])
		
		# Decode the message
		return event_msg_format[0].format(*[engine.entity_to_alias.get(getattr(self, var_name)) for var_name in event_msg_format[1]])