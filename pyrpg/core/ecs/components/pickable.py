from .component import Component

class Pickable(Component):
	''' Entity is pickable by HasInventory entity.

	Used by:
		-	CollisionItemProcessor

	Tests:
		>>> c = Pickable()
	'''

	__slots__ = []

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Item component. Component has
		no arguments, it is just a tag, in fact.
		'''

		super().__init__()

