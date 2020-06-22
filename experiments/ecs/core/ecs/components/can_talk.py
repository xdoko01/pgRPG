from .component import Component
import core.config.config as config
import pygame 
import pygame.freetype 	# for CanTalk component



class CanTalk(Component):
	''' Entity can generate the text bubble that is displayed on the screen.

	Used by:
		-	RenderWorldProcessor

	Tests:
		>>> c = CanTalk()
	'''

	__slots__ = ['font_object', 'text', 'text_surf', 'text_rect']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new CanTalk component.

		Parameters:
			:param text_color: Color of the text
			:type text_color: tuple

			:param font: Path to the used font
			:type font: str

			:param font_size: Size of the font
			:type font: int
		'''

		super().__init__()

		# Font parameters
		self.text_color = kwargs.get('text_color', (255, 255, 255))
		self.font = kwargs.get('font', str(config.FONT_PATH / 'FiraCode-Regular.ttf'))
		self.font_size = kwargs.get('font_size', 12)

		# Check that parameters have correct type
		try:
			assert isinstance(self.font, str), f'Font must be passed in the form of string.'
			assert isinstance(self.font_size, int), f'Font size must be passed as int.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Necessary for generating graphical text representation
		self.font_object = pygame.freetype.Font(self.font, self.font_size)

		# Text to display
		self.text = '...'

		# Surface and rectangle describing the text in graphics
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects.
		'''
		self.font_object = None
		self.text_surf = None
		self.text_rect = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component.
		'''
		self.font_object = pygame.freetype.Font(self.font, self.font_size)
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)
