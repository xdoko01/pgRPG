from .component import Component

class DeleteOnCollision(Component):
	''' Entity is deleted after collision with other entity

	Used by:
		-	CollisionDeletionProcessor	

	Tests:
		>>> c = DeleteOnCollision()
	'''

	__slots__ = []

	def __init__(self, *args, **kwargs):
		''' Initiate the new DeleteOnCollision component.

		Parameters:
			none
		'''

		super().__init__()