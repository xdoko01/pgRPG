import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

from .functions import filter_only_visible_on_camera # for filtering only entities with position on the cameras

class RenderTalkProcessor2(esper.Processor):
	''' Draws the text bubbles for the entites usning Bitmap font

	It draws only those bubbles that are displayable on the screen
	by using filter function.
	
	Input parameters:
		-	window - reference to main game screen
		-	debug

	Involved components:
		-	Position
		-	Camera
		-	CanTalk
	
	Related processors:
		-	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

	What if this processor is disabled?
		-	text bubbles will be not shown on the game window
	
	Where the processor should be planned?
		-	before RenderDebugProcessor - in order not to overwrite the debug info
		-	after UpdateCameraOffsetProcessor - in order to display scrolling
		-	after RenderMapProcessor - in order to display map
		-	after RenderModelWorldProcessor - in order to be displayed over other entities
	'''

	__slots__ = ['window', 'debug', 'font']

	def __init__(self, window, debug=False):
		''' Initiation of RenderProcessor processor.
		
		Parameters:
			:param window: Reference to the main game surface
			:type window: pygame.Surface

			:param debug: Tag if processor should run in debug mode
			:type debug: bool
		'''

		super().__init__()

		self.window = window
		self.debug = debug

	def process(self, *args, **kwargs):
		''' Draws screen for every camera. Every screen draws entities
		and dialog texts. Check the following video for more details about camera
		implementation of scrolling https://youtu.be/3zV2ewk-IGU.
		'''

		# For all camera screens in the game window
		for _, (camera) in self.world.get_component(components.Camera):

			# Blit all Texts that are entities saying (CanTalk + Position component)
			for _, (position, can_talk) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(components.Position, components.CanTalk)):

				# If there is something to say
				if can_talk.text:

					# Blit the text frame bubble and the text itself on the position offset specified by CanTalk component

					if position.direction == (1, 0): # RIGHT
						camera.screen.blit(can_talk.frame_surf, camera.apply((position.x - can_talk.frame_dim[0], position.y - can_talk.frame_dim[1])))
						camera.screen.blit(can_talk.text_surf, camera.apply((can_talk.frame_text_offset[0] + position.x - can_talk.frame_dim[0], can_talk.frame_text_offset[1] + position.y - can_talk.frame_dim[1])))

					elif position.direction == (-1, 0): # if direction is (-1, 0) LEFT
						camera.screen.blit(can_talk.frame_surf, camera.apply((position.x, position.y - can_talk.frame_dim[1])))
						camera.screen.blit(can_talk.text_surf, camera.apply((can_talk.frame_text_offset[0] + position.x, can_talk.frame_text_offset[1] + position.y - can_talk.frame_dim[1])))

					elif position.direction == (0, -1): # if direction is (0,-1) UP
						camera.screen.blit(can_talk.frame_surf, camera.apply((position.x - can_talk.frame_dim[0] / 2, position.y)))
						camera.screen.blit(can_talk.text_surf, camera.apply((can_talk.frame_text_offset[0] + position.x - can_talk.frame_dim[0] / 2, can_talk.frame_text_offset[1] + position.y)))

					else: # if direction is (0,1) DOWN
						camera.screen.blit(can_talk.frame_surf, camera.apply((position.x - can_talk.frame_dim[0] / 2, position.y - can_talk.frame_dim[1])))
						camera.screen.blit(can_talk.text_surf, camera.apply((can_talk.frame_text_offset[0] + position.x - can_talk.frame_dim[0] / 2, can_talk.frame_text_offset[1] + position.y - can_talk.frame_dim[1])))

			# Blit the camera screen on the main game window
			self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to
		non-serializable components (window).
		'''
		self.window = None

	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window


class RenderTalkProcessor(esper.Processor):
	''' Draws the text bubbles for the entites

	It draws only those bubbles that are displayable on the screen
	by using filter function.
	
	Input parameters:
		-	window - reference to main game screen
		-	debug

	Involved components:
		-	Position
		-	Camera
		-	CanTalk
	
	Related processors:
		-	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

	What if this processor is disabled?
		-	text bubbles will be not shown on the game window
	
	Where the processor should be planned?
		-	before RenderDebugProcessor - in order not to overwrite the debug info
		-	after UpdateCameraOffsetProcessor - in order to display scrolling
		-	after RenderMapProcessor - in order to display map
		-	after RenderModelWorldProcessor - in order to be displayed over other entities
	'''

	__slots__ = ['window', 'debug']

	def __init__(self, window, debug=False):
		''' Initiation of RenderProcessor processor.
		
		Parameters:
			:param window: Reference to the main game surface
			:type window: pygame.Surface

			:param debug: Tag if processor should run in debug mode
			:type debug: bool
		'''

		super().__init__()

		self.window = window
		self.debug = debug


	def process(self, *args, **kwargs):
		''' Draws screen for every camera. Every screen draws entities
		and dialog texts. Check the following video for more details about camera 
		implementation of scrolling https://youtu.be/3zV2ewk-IGU.
		'''
		# For all camera screens in the game window
		for _, (camera) in self.world.get_component(components.Camera):

			#####
			# Blit text bubbles
			#####

			# Blit all Texts that are entities saying (CanTalk + Position component)
			for _, (position, can_talk, renderable) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(components.Position, components.CanTalk, components.RenderableModel)):

				# If there is something to say
				if can_talk.text:
					
					# Blit the text bubble on the position offset specified by CanTalk component
					
					if position.direction == (1, 0): # RIGHT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - renderable.model.dim_2.x - can_talk.text_rect[2], position.y - can_talk.text_rect[3])))
					
					elif position.direction == (-1, 0): # if direction is (-1, 0) LEFT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x + renderable.model.dim_2.x, position.y - can_talk.text_rect[3])))

					elif position.direction == (0, -1): # if direction is (0,-1) UP
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y + renderable.model.dim_2.y )))

					else: # if direction is (0,1) DOWN
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y - renderable.model.dim_2.y - can_talk.text_rect[3])))


			# Blit the camera screen on the main game window
			self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window).
		'''
		self.window = None

	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window
