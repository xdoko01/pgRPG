from .component import Component
import core.engine as engine # For checking the engine._entity_map - if component has entity as a str as a parameter (HasInventory) + engine._maps

class Teleport(Component):
	''' Entity is a teleport - i.e. on collision it changes position of
	the object that collided with the entity.

	Used by:
		-	CollisionTeleportProcessor

	Tests:
		>>> c = Teleport()
	'''

	__slots__ = ['dest_x', 'dest_y', 'dest_map']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Teleport component.

		Parameters:
			:param dest_x: X-axis position in pixels on the target map.
			:type dest_x: int

			:param dest_y: Y-axis position in pixels on the target map.
			:type dest_y: int

			:param dest_map: Name of the target map where entity is teleported.
			:type dest_map: str

			:param key: Entity representing key that is necessary to be in the inventory in order to teleport.
			:type key: str or int

			:raise: ValueError - in case mandatory parameters are missing.
		'''
	
		super().__init__()
		
		# Teleport destination - mandatory
		try:
			self.dest_map = kwargs.get('dest_map')
			self.dest_x = kwargs.get('dest_x')
			self.dest_y = kwargs.get('dest_y')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing')
			raise ValueError

		# Assert that targetmap exists in the global list of all initiated maps engine and position is integer
		try:
			assert self.dest_map in engine._maps.keys(), f'Destination map {self.dest_map} is not initialized for {self.__class__} component.'
			assert isinstance(self.dest_x, int), f'Position x is not an integer for {self.__class__} component.'
			assert isinstance(self.dest_y, int), f'Position y is not an integer for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError


		# Key for the teleport - no teleportation without key in inventory (entity) - optional
		teleport_key = kwargs.get('key', None)
		
		# Check that the key entity exists in global list of entities
		try:
			self.key = engine._entity_map.get(teleport_key) if isinstance(teleport_key, str) else teleport_key
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Key {teleport_key} is not present in list of entities.')
			raise ValueError
