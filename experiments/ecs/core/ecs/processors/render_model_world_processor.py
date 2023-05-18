__all__ = ['RenderModelWorldProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

from .functions import filter_only_visible_on_camera # for filtering only entities with position on the cameras

class RenderModelWorldProcessor(esper.Processor):
	''' Draws the entities in the world. Unlike RenderWorldProcessor
	this one supports animated models.

	It draws only those entities that are displayable on the screen
	by using filter function.
	
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

			#####
			# Blit body
			#####

			# Blit all the Entities that have Renderable and Position components - only visible entities
			for ent, (position, renderable) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(components.Position, components.RenderableModel)):
				#camera.screen.blit(renderable.get_frame(position.dir_name, renderable.action), camera.apply(renderable.topleft((position.x, position.y))))
				camera.screen.blit(renderable.get_current_frame(position.dir_name), camera.apply(renderable.topleft((position.x, position.y))))

				#####
				# Blit wearables for those displayable- using body information in order to sync the animations
				#####

				# Blit all wearables for the above Entity - if possible
				if self.world.has_component(ent, components.CanWear):

					# Get the CanWear component of the entity that picked up Wearable
					can_wear = self.world.component_for_entity(ent, components.CanWear)

					# Iterate the wearables dictionary and blit them
					for w_part, w_entity in can_wear.wearables.items():

						# Get the wearable entity - RenderableModel
						if w_entity: 
							w_renderable = self.world.component_for_entity(w_entity, components.RenderableModel)

							# Blit it on the screen the wearable - using state / position and frame id from the character's RenderableModel
							#camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))
							camera.screen.blit(w_renderable.get_current_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))

				#####
				# Blit weapons for those displayable- using body information in order to sync the animations
				#####

				# Blit all weapons for the above Entity - if possible
				if self.world.has_component(ent, components.HasWeapon):

					# Get the HasWeapon component of the entity that picked up Weapon
					has_weapon = self.world.component_for_entity(ent, components.HasWeapon)

					# Get the weapon entity - RenderableModel
					if has_weapon.get_weapon_in_use():

						# Skip if weapon does not have any model to be rendered
						try:
							w_renderable = self.world.component_for_entity(has_weapon.get_weapon_in_use(), components.RenderableModel)
							#print(f'has_weapon.get_weapon_in_use() - {has_weapon.get_weapon_in_use()}, renderable.action {renderable.action}')

							# Blit it on the screen the weapon - using state / position and frame id from the character's RenderableModel
							# camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))
							camera.screen.blit(w_renderable.get_current_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))
						except KeyError:
							pass

						# Skip if generator does not have any model to be rendered
						try:
							gen_renderable = self.world.component_for_entity(has_weapon.get_generator_in_use(), components.RenderableModel)
							#print(f'has_weapon.get_weapon_in_use() - {has_weapon.get_weapon_in_use()}, renderable.action {renderable.action}')

							# Blit it on the screen the weapon - using state / position and frame id from the character's RenderableModel
							# camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))
							camera.screen.blit(gen_renderable.get_current_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))
						except KeyError:
							pass

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
