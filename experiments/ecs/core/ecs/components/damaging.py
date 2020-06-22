from .component import Component

class Damaging(Component):
	''' Entity containing this component is hurting 
	entities upon collision - for example projectile.
	'''

	__slots__ = ['damage']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Damaging component.
		'''
		super().__init__()

		self.damage = kwargs.get("damage", 10)
