from .component import Component

class Collidable(Component):
	''' Entity collides with other collidable entities.

	Used by:
		-	RenderDebugProcessor
		-	CollisionMapProcessor
		-	CollisionEntityGeneratorProcessor
		-	CollisionTeleportProcessor
		-	CollisionItemProcessor
		-	CollisionEntityProcessor
		-	CollisionCorrectorProcessor	

	Tests:
		>>> c = Collidable()
	'''

	__slots__ = ['x', 'y', 'collision_events']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Collidable component.

		Parameters:
			:param x: X-axis collision zone +- from the x-centre of the entity in pixel coordinates
			:type x: int

			:param y: Y-axis collision zone +- from the y-centre of the entity in pixel coordinates
			:type y: int

			:raise: ValueError - in case of incorrect collision borders
		'''

		super().__init__()
		
		# With and height of the collision zone - from the center +/-x and +/-y
		self.x = kwargs.get('x', 0)
		self.y = kwargs.get('y', 0)

		try:
			assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as positive int.'
			assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as positive int.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError		

		# Keep track with whom the entity collided
		self.collision_events = set()
