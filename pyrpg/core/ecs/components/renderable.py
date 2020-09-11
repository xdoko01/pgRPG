from .component import Component
import pygame
from pyrpg.core.config.paths import IMAGE_PATH

class Renderable(Component):
	''' Entity is displayable on the game screen.

	Used by:
		-	RenderWorldProcessor
		-	RenderDebugProcessor

	Tests:
		>>> c = Renderable()
	'''

	__slots__ = ['image', 'w', 'h', 'd_h', 'd_w']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Renderable component.

		Parameters:
			:param image_file: Name of the image stored in IMAGE_PATH directory, including suffix
			:type image_file: str

			:raise: ValueError - in case image file is not found
		'''

		super().__init__()

		# Image and its parameters
		try:
			self.image_file = kwargs.get("image", "")
			assert isinstance(self.image_file, str), f'Image file name {self.image_file} is not valid.'

			#self.image = pygame.image.load(str(IMAGE_PATH / self.image_file)).convert()
			self.image = pygame.image.load(str(IMAGE_PATH / self.image_file)).convert()

		except FileNotFoundError:
			print(f'Image file {IMAGE_PATH / self.image_file} not found')
			# Notify component factory that initiation has failed
			raise ValueError
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		self.w = self.image.get_width()
		self.h = self.image.get_height()

		# Diff vector from centre of the sprite to the topleft corner
		# it is used by Render processor to get the right point where
		# to render the sprite. i.e. position of the character can be 
		# 100, 100 but in order to be centered on this position, render 
		# processor must blit the sprite on 75,75 (example w,h=50)
		self.d_w = self.w / 2
		self.d_h = self.h / 2

	def topleft(self, pos):
		''' Returns correction of coordinates to display the sprite correctly

		Parameters:
			:param pos: Position on the map in pixels.
			:type pos: tuple, list
			
			:return: Position of the topleft corner of the image as a tuple.
		'''
		return (pos[0] - self.d_w, pos[1] - self.d_h)

	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.image = None
		self.w = self.h = self.d_h = self.d_w = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.image = pygame.image.load(str(IMAGE_PATH / self.image_file)).convert()
		
		self.w = self.image.get_width()
		self.h = self.image.get_height()
		
		self.d_w = self.w / 2
		self.d_h = self.h / 2		
