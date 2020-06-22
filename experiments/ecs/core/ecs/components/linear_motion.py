from .component import Component

class LinearMotion(Component):
	'''
	'''
	__slots__ = ['speed']

	def __init__(self, *args, **kwargs):
		'''
		'''
		super().__init__()
		
		# Change of position
		self.speed = kwargs.get('speed')

		# Assert that dx, dy are numbers
		try:
			assert isinstance(self.speed, int) or isinstance(self.dx, float), f'Movement speed is not a number for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError
