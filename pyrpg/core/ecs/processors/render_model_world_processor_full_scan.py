__all__ = ['RenderModelWorldProcessorFullScan']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class RenderModelWorldProcessorFullScan(esper.Processor):
	''' Draws the entities in the world. Unlike RenderWorldProcessor
	this one supports animated models. 
	
	Unlike  RenderModelWorldProcessor this one blits even entities that
	are not visible on the screen. Hence, it is not optimized.
	
	Input parameters:
		-	window - reference to main game screen
		-	debug

	Involved components:
		-	Position
		-	Camera
		-	RenderableModel
		-	CanTalk
	
	Related processors:
		-	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

	What if this processor is disabled?
		-	entities will be not shown on the game window
	
	Where the processor should be planned?
		-	before RenderDebugProcessor - in order not to overwrite the debug info
		-	after UpdateCameraOffsetProcessor - in order to display scrolling
		-	after RenderMapProcessor - in order to display map
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

			# Blit all the Entities that have Renderable and Position components - all, i.e. not only visible components
			for _, (position, renderable, state) in self.world.get_components(components.Position, components.RenderableModel, components.State):
				camera.screen.blit(renderable.get_frame(state.state, position.dir_name), camera.apply(renderable.topleft((position.x, position.y))))

			# Blit all Texts that are entities saying (CanSpeak + Position component)
			for _, (can_talk, renderable, position) in self.world.get_components(components.CanTalk, components.Renderable, components.Position):

				# If there is something to say
				if can_talk.text:
					
					# Blit the text bubble on the position offset specified by CanTalk component
					
					if position.direction == (1,0): # RIGHT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - renderable.d_w - can_talk.text_rect[2], position.y - can_talk.text_rect[3])))
					
					elif position.direction == (-1,0): # if direction is (-1, 0) LEFT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x + renderable.d_w, position.y - can_talk.text_rect[3])))

					elif position.direction == (0,-1): # if direction is (0,-1) UP
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y + renderable.d_h )))

					else: # if direction is (0,1) DOWN
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y - renderable.d_h - can_talk.text_rect[3])))


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
