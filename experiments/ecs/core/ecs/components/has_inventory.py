from .component import Component
import core.engine as engine # For checking the engine._entity_map - if component has entity as a str as a parameter (HasInventory) + engine._maps

class HasInventory(Component):
	''' Entity has inventory - can pick items and add it to the inventory.

	Used by:
		-	RenderDebugProcessor
		-	CollisionTeleportProcessor
		-	CollisionItemProcessor

	Tests:
		>>> c = HasInventory()
	'''

	__slots__ = ['inventory']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new HasInventory component.

		Parameters:
			:param inventory: List of entities that are in the inventory
			:type inventory: List of string or list of integers
		'''

		super().__init__()

		# Check that inventory is a list
		try:
			assert isinstance(kwargs.get('inventory', []), list), f'Inventory must be a list of entities.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Substitute the inventory items that are specified by id (str) with entity ids (int)
		# based on mapping in engine class
		try:
			self.inventory = [engine._entity_map.get(item) if isinstance(item, str) else item for item in kwargs.get('inventory', [])]
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Item in the inventory is not initiated in global list of entities.')
			raise ValueError
