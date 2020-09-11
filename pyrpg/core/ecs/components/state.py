from .component import Component

class State(Component):
	''' Represent state of the entity
	idle, walk, attack, ...
	'''

	__slots__ = ['state']

	STATES = ['idle', 'walk', 'idle_stab', 'idle_swing']

	def __init__(self, *args, **kwargs):
		''' Initiate State component

		Parameters:
			:param state: State of the entity (default = idle)
			:type state: str

			:raise: ValueError - in case state is not defined/allowed
		'''
		
		try:
			self.state = kwargs.get('state', 'idle') 
			assert isinstance(self.state, str) and self.state in State.STATES, f'State {self.state} is not allowed state'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError
