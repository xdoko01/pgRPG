from .component import Component

class Labeled(Component):
	''' Entity has some id and name that is used in configuration files (json) 
	to refer to the entity.

	Used by:
		-	RenderDebugProcessor

	Tests:
		>>> c = Labeled()
	'''

	__slots__ = ['id', 'name']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the  Labeled component.

		Parameters:
			:param id: Game ID of the entity. Can differ from ECS id
			:type id: str

			:param name: Game name of the entity
			:type name: str
		'''
		super().__init__()

		self.id = kwargs.get("id", None)
		self.name = kwargs.get("name", None)
