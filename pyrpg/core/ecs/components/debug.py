from .component import Component

class Debug(Component):
	''' Display debug information on entities that are tagged by this component.

	Used by:
		-	RenderDebugProcessor
	
	Tests:
		>>> c = Debug()
	'''

	__slots__ = []

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new component
		'''

		super().__init__()


	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		pass

	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		pass