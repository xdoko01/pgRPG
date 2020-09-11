from .component import Component
import pyrpg.core.config.config as config
import pygame 


class CanTalk(Component):
	''' Entity can generate the text bubble that is displayed on the screen.

	Unlike CanTalk(previous version) this one is not having new font instance
	per every component.
	
	Used by:
		-	RenderTalkProcessor

	Tests:
		>>> c = CanTalk()
	'''

	__slots__ = ['text', 'text_color', 'text_surf', 'text_dim', 'text_speed', 'frame_surf', 'frame_dim', 'frame_text_offset']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new CanTalk component.

		Parameters:
			:param text_color: Color of the text
			:type text_color: tuple

			:param text_speed: Speed of displaying the speach in ms
			:type font: int
		'''

		super().__init__()

		# Text and frame parameters
		self.text_color = kwargs.get('text_color', None)
		self.text_color = kwargs.get('frame_color', None)

		self.text_speed = kwargs.get('text_speed', 100)

		# Check that parameters have correct type
		try:
			assert isinstance(self.text_color, str) if self.text_color != None else True, f"Incorrect value: 'text_color = {self.text_color}'. Text color be passed in the form of string (e.g. #FF00FF)."
			assert isinstance(self.text_speed, int) and self.text_speed > 0, f"Incorrect value: 'text_speed = {self.text_speed}'. Must be integer greater than 0."
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Text to display
		self.text = ''

		# Surface representing the text in graphics
		self.text_surf = pygame.Surface((0, 0))
		self.text_dim = (self.text_surf.get_width(), self.text_surf.get_height())

		# Surface representing the frame in graphics
		self.frame_surf = pygame.Surface((0, 0))
		self.frame_dim = (self.frame_surf.get_width(), self.frame_surf.get_height())
		self.frame_text_offset = (0, 0)

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects.
		'''
		self.text_surf = None
		self.frame_surf = None

	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component.
		'''
		self.text_surf = pygame.Surface((0, 0))
		self.frame_surf = pygame.Surface((0, 0))



class CanTalkObsolete(Component):
	''' Entity can generate the text bubble that is displayed on the screen.

	This one is using pygame.freetype.Font for every entity

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
		self.font = kwargs.get('font', str(config.FONT_PATH / 'game_font.ttf'))
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
