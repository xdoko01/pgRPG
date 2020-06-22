from .component import Component

class Controllable(Component):
	''' Entity can be controlled by the keyboard commands.

	Used by:
		-	InputProcessor

	Tests:
		>>> c = Controllable()
	'''

	__slots__ = ['control_keys', 'enabled', 'control_cmds']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Controllable component.

		Parameters:
			:param control_keys: Dictionary containing mapping 
				of movement and action keys to keyboard keys
			:type control_keys: dict

			:param control_cmds: Dictionary containing mapping
				of movement and action keys to commands
			:type control_cmds: dict

			:raise: ValueError - in case of incorrect keys/commands definition

		'''
		super().__init__()

		# Possibility to disable input for the global processor
		self.enabled = True

		# Control keys definition - keyboard arrows + 'z' key for attack
		default_keys = {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122}
		control_keys = kwargs.get("control_keys", default_keys)

		# Control commands definition
		default_cmds = { 'left' : 'move', 'right': 'move', 'up' : 'move', 'down' : 'move', 'attack' : 'attack'}
		control_cmds = kwargs.get("control_cmds", default_cmds)

		try:
			assert isinstance(control_keys, dict), f'Control keys must be passed in a form of dictionary.'
			assert isinstance(control_cmds, dict), f'Control cmds must be passed in a form of dictionary.'

			# Does control_keys dictionary contain at least one valid key key?
			assert bool(set(default_keys.keys()).intersection(set(control_keys.keys()))), f'Control keys are not properly defined'

			# Does control_cmds dictionary contain at least one valid command key?
			assert bool(set(default_cmds.keys()).intersection(set(control_cmds.keys()))), f'Control commands are not properly defined'

		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Merge defaults with defined
		self.control_keys = {**default_keys, **control_keys}

		# Merge defaults with defined
		self.control_cmds = {**default_cmds, **control_cmds}
