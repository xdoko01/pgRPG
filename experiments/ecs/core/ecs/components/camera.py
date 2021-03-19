from .component import Component
import pygame 			# for Camera component

class Camera(Component):
	''' Entity is in focus of a camera that is displayed in form of a screen
	in the game window.

	Used by:
		-	UpdateCameraOffsetProcessor
		-	CollisionItemProcessor
		-	RenderMapProcessor
		-	RenderWorldProcessor
		-	RenderDebugProcessor
		-	RenderMapProcessorFullScan (OBSOLETE)

	Tests:
		>>> c = Camera()
	'''

	__slots__ = ['always_centre', 'map_screen_rect', 'offset_x', 'offset_y', 'screen_pos_x', 'screen_pos_y' \
				'screen_width', 'screen_height', 'screen_width_half', 'screen_height_half','screen']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Camera component.

		Parameters:
			:param screen_pos_x: X-axis position of the topleft screen corner in the game window.
			:type screen_pos_x: int

			:param screen_pos_y: Y-axis position of the topleft screen corner in the game window.
			:type screen_pos_y: int

			:param screen_width: Width of the screen window.
			:type screen_height: Height of the screen window.

			:raise: ValueError - in case of incorrect screen window parameters.
		'''
		
		super().__init__()
		
		# Rectancle (top-left and bottom-right positions in pixels) of the map that is displayed on
		# camera.screen surface. It is used for rendering of map on the screen. Rectancle is calculated
		# by the UpdateCameraOffsetProcessor.
		self.map_screen_rect = (0,0,0,0)

		# Offset variables necessary for camera functionality - Offset is calculated by the 
		# UpdateCameraOffsetProcessor
		self.offset_x = 0
		self.offset_y = 0

		# Should the camera be always centered on the entity - default is False 
		# If False then camera stops centering when entity is close to map edges
		self.always_center = kwargs.get('always_center', False)

		# Topleft position of the Camera screen
		self.screen_pos_x = kwargs.get('screen_pos_x', 0)
		self.screen_pos_y = kwargs.get('screen_pos_y', 0)

		# Width and height of the Camera screen
		self.screen_width = kwargs.get('screen_width', 100)
		self.screen_height = kwargs.get('screen_height', 100)

		# Check the parameters for correctness
		try:
			assert isinstance(self.always_center, bool), f'Incorrect camera mode parameter - {self.always_center}.'

			assert isinstance(self.screen_pos_x, int) and self.screen_pos_x >= 0, f'Incorrect position of the camera screen window - {self.screen_pos_x}.'
			assert isinstance(self.screen_pos_y, int) and self.screen_pos_y >= 0, f'Incorrect position of the camera screen window - {self.screen_pos_y}.'

			assert isinstance(self.screen_width, int) and self.screen_width > 0, f'Incorrect width of the camera screen window - {self.screen_width}.'
			assert isinstance(self.screen_height, int) and self.screen_height > 0, f'Incorrect height of the camera screen window - {self.screen_height}.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Half of width and height is precalculated to avoid repetitive calculations /2
		self.screen_width_half = int(round(self.screen_width / 2))
		self.screen_height_half = int(round(self.screen_height / 2))

		# Camera screen surface on which map is blitted
		self.screen = pygame.Surface((self.screen_width, self.screen_height))
	
	def apply(self, pos=(0,0)):
		''' Applying camera offset to some position. Returns new position
		of the object and hence enables scrolling effect.

		Parameters:
			:param pos: Position on which camera offset will be applied
			:type pos: tuple
		'''
		# Move the sprite of the entity - returns new shifted coordinates
		return (pos[0] + self.offset_x, pos[1] + self.offset_y)
	
	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.screen = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.screen = pygame.Surface((self.screen_width, self.screen_height))
