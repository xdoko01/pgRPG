"""Game event data object used by the event manager and processors."""

from pgrpg.core.config import MESSAGES
from pgrpg.core.managers import ecs_manager


class Event:
	"""Encapsulate a game event dispatched through the event queue.

	Attributes:
		event_type: String identifying the event kind (e.g. ``'COLLISION'``).
		generator_obj: Entity ID (or None) that generated the event.
		other_obj: Entity ID (or None) of the other participant.
		params: Dict of additional event parameters.
	"""

	# Every type any processor actually emits, verified by grepping Event(...)
	# constructions across pgrpg/ and example_game/ (#98). Documentation only:
	# the assert below is disabled, and a scene may legitimately invent its own
	# type (e.g. 'CUST_UI_CONFIRM', raised by the show_confirm_dlg script), so
	# this list is not a closed set to validate against.
	EVENT_TYPES = ['SCENE_START', 'COLLISION', 'TELEPORTATION',
		 'ITEM_PICKUP', 'ITEM_DROP',
		 'WEAPON_ARMED', 'WEAPON_DISARMED', 'WEAPON_SET_INTO_USE',
		 'AMMO_PACK_ARMED', 'AMMO_PACK_DISARMED',
		 'DAMAGE', 'KILLED', 'DESTROYED', 'SCORE',
		 'ON_POS_TARGET', 'ON_BUTTON_PRESSED',
		 'CAN_SEE', 'CAN_HEAR']

	def __init__(self, event_type, generator_obj, other_obj, params={}):

		#assert(event_type in Event.EVENT_TYPES)

		self.event_type = event_type
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params

	def __str__(self):
		return f'*Event type: "{self.event_type}", Source entity: "{self.generator_obj}", Other entity: "{self.other_obj}", Params: "{self.params}"'

	def to_string(self):
		"""Format the event as a human-readable message using config templates.

		Returns:
			Formatted string, or empty string if no template is defined.
		"""

		# Get the event msg format - from config files - it is ok not to fill any parameter
		event_msg_format = MESSAGES["ON_EVENT"].get(self.event_type, ['', []])
		
		# Decode the message
		return event_msg_format[0].format(*[ecs_manager.get_entity_alias(entity_id=getattr(self, var_name)) for var_name in event_msg_format[1]])