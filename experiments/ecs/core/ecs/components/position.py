from .component import Component
import core.engine as engine # For checking the engine._entity_map - if component has entity as a str as a parameter (HasInventory) + engine._maps

# TODO - is self.direction necessary? is not enough dir_name?
class Position(Component):
	''' Entity has possition in the game world specified by x, y and map.
	
	Used by:
		-	UpdateCameraOffsetProcessor
		-	MovementProcessor
		-	RenderMapProcessor
		-	RenderWorldProcessor
		-	RenderDebugProcessor
		-	CollisionMapProcessor
		-	CollisionEntityGeneratorProcessor
		-	CollisionTeleportProcessor
		-	CollisionEntityProcessor
		-	CollisionCorrectorProcessor
		-	RenderMapProcessorFullScan (OBSOLETE)

	Tests:
		>>> c = Position()
	'''

	__slots__ = ['x', 'y', 'map', 'direction', 'dir_name']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Position component.

		Parameters:
			:param x: X-axis position in pixels on the map.
			:type x: int

			:param y: Y-axis position in pixels on the map.
			:type y: int

			:param map: Name of the map where entity is present.
			:type map: str

			:raise: ValueError - in case mandatory parameters are missing.
		'''

		super().__init__()
		
		# Coordinates in the world
		try:
			self.x = kwargs.get('x')
			self.y = kwargs.get('y')
			self.map = kwargs.get('map')
			self.dir_name = kwargs.get('dir', 'down')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that map exists in the global list of all initiated maps engine
		try:
			assert self.map in engine._maps.keys(), f'Map {self.map} is not initialized for {self.__class__} component.'
			assert isinstance(self.x, int), f'Position x is not an integer for {self.__class__} component.'
			assert isinstance(self.y, int), f'Position y is not an integer for {self.__class__} component.'
			assert self.dir_name in ('up', 'down', 'left', 'right'), f'Position direction is not defined for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Direction SOUTH (0,1) NORD (0,-1) WEST (-1,0) EAST (1,0)
		# Necessary for correct rendering of sprites and text boxes etc.
		
		if self.dir_name == 'down': self.direction = (0, 1)
		if self.dir_name == 'up': self.direction = (0, -1)
		if self.dir_name == 'left': self.direction = (-1, 0)
		if self.dir_name == 'right': self.direction = (1, 0)

		# Remember last possition, on collision return to the last known pos
		# Required for resolution of collisions with the map
		self.lastx = self.x
		self.lasty = self.y
		self.lastmap = self.map
	
	def set_direction(self, dir_name):
		'''
		'''
		try:
			assert dir_name in ('up', 'down', 'left', 'right'), f'Position direction is not defined for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError
		
		self.dir_name = dir_name 

		if self.dir_name == 'down': self.direction = (0, 1)
		if self.dir_name == 'up': self.direction = (0, -1)
		if self.dir_name == 'left': self.direction = (-1, 0)
		if self.dir_name == 'right': self.direction = (1, 0)
