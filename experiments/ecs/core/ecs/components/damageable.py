from .component import Component

class Damageable(Component):
	''' Entity has some health, i.e. is damageable 
	'''

	__slots__ = ['health']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the  Health component.
		'''
		super().__init__()

		self.health = kwargs.get("health", 100)
