from .component import Component
import pygame

class Debug(Component):
	''' Display debug information on entities that are tagged by this component.

	Used by:
		-	RenderDebugProcessor
	
	Tests:
		>>> c = Debug()
	'''

	__slots__ = 'font'

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new component
		'''

		super().__init__()

		# Font used for displaying debug information
		self.font = pygame.font.Font(None, 16)

	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.font = None

	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.font = pygame.font.Font(None, 16)
