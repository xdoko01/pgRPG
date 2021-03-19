''' Module containing all components

	TODO
		- debug processors?
		- log time of processors?
'''

import pygame	# for pygame.time, pygame.font and pygame.Color

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.config.config as config # for MOVE_SPEED
import pyrpg.core.events.event as event # for creation of events

########################################################
### Package init commands
########################################################

#if not pygame.get_init(): pygame.init()

########################################################
### Module globals
########################################################


########################################################
### Module functions
########################################################

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

def filter_only_visible(camera, comp_tuple, corr=32):
	''' Filter that is used for selection of only those entities
	that are within visible scope of the camera screen.

	Correction corr is by default 32 pixels

	!! Position component must be the first component in the tuple in order to work !!
	'''
	# Displayable part of the map in pixel coordinates
	rect = camera.map_screen_rect

	# Correction corr - part of sprite must be visible even if
	# position is beneath borders

	# Select position component from the return tuple. Must be the first
	_, (position, *_) = comp_tuple

	# True, if position is within rectancle of camera screen
	return rect[0] - corr < position.x < rect [2] + corr and rect[1] - corr < position.y < rect[3] + corr


########################################################
### Processors Classes
########################################################

class GenerateProjectileProcessor(esper.Processor):
	''' Generate projectiles
		
		- planned before all collision processors
		- planned after command processor - Attack command
	'''

	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		''' TODO - is there any variable from the global world that we want to use here?
		'''
		print(f'Running GenerateProjectileProcessor')
		# Get entities capable of producing projectiles - HasWeapon, on the last attack frame RenderableModel
		for ent, (has_weapon, renderable_model, position) in self.world.get_components(components.HasWeapon, components.RenderableModel, components.Position):
			
			print(f'RenderableModel {renderable_model}, Action: {renderable_model.action} Current frame: {renderable_model.last_frame} Is last frame: {renderable_model.is_last_frame}')

			# Check if Model is in the action status and last frame of the action is happening
			if renderable_model.action == has_weapon.get_weapon_action_anim() and renderable_model.is_last_frame:
				
				# Collidable is optional component - entities who are not collidable can generate projectiles
				collidable = self.world.try_component(ent, (components.Collidable))

				# Create an projectile
				has_weapon.create_projectile(ent, position, collidable)


class ClearTemporaryEntityProcessor(esper.Processor):
	''' Delete for example projectiles
	'''
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		
		# Get all temporary components
		for ent, temporary in self.world.get_component(components.Temporary):

			# Compare if the entity lived long enough
			if pygame.time.get_ticks() - temporary.creation_time > temporary.ttl:
				
				# Delete from container TODO - must be done generic
				container = self.world.try_component(ent, components.Container)
				
				if container:
					# Remove from the set of projectiles
					print(f'container.contained_in {container.contained_in}, container.contained_in.projectiles {container.contained_in.projectiles}')
					container.contained_in.remove_projectile(ent) #HasWeapon component
					
				
				# Remove from the world
				self.world.delete_entity(ent)


class RenderableModelAnimationActionProcessor(esper.Processor):
	''' Change the action of renderable model in order to display
	correct action animation.

	co takhle prepsat to jako erastotenovo sito
		- a potom porovnat performance
		- novej procesor
			- for RenderableModel -> IDLE
			- for RenderableModel, HasWeapon -> ACTION ANIM, IDLE ANIM
			- for RenderableModel, Motion -> WALK
		- potom aktualizovat frame
			- for RenderableModel, Position - pouze ty na kamerach novy filter filter_only_visible(all_cameras, x)
				- update_frame() ... bez argumentu
	'''
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		
		# Get all states
		for ent, renderable_model in self.world.get_component(components.RenderableModel):
			
			# try to get motion, has_weapon - returns None if not present
			motion = self.world.try_component(ent, components.Motion)
			has_weapon = self.world.try_component(ent, components.HasWeapon)

			if motion and motion.has_moved:
				
				# If entity has moved, action is set to 'walk'
				renderable_model.set_action('walk')
			
			elif has_weapon and has_weapon.weapon and has_weapon.has_attacked:
				
				# If entity has weapon and the weapon has attacked, set action to proper value
				renderable_model.set_action(has_weapon.get_weapon_action_anim())
				
				# Reset the attack - in case attack key is released animation of attack is no longer displayed
				has_weapon.has_attacked = False

			elif has_weapon and has_weapon.weapon:
				
				# If entity has weapon but is not attacking, display idle weapon animation
				renderable_model.set_action(has_weapon.get_weapon_idle_anim())

			
			else:
				# Has no weapon, is not moving,
				renderable_model.set_action('idle')


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
			for ent, (position, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel)):
				camera.screen.blit(renderable.get_frame(position.dir_name, renderable.action), camera.apply(renderable.topleft((position.x, position.y))))

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
							camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))

				#####
				# Blit weapons for those displayable- using body information in order to sync the animations
				#####

				# Blit all weapons for the above Entity - if possible
				if self.world.has_component(ent, components.HasWeapon):

					# Get the HasWeapon component of the entity that picked up Weapon
					has_weapon = self.world.component_for_entity(ent, components.HasWeapon)

					# Get the weapon entity - RenderableModel
					if has_weapon.weapon:
						w_renderable = self.world.component_for_entity(has_weapon.weapon, components.RenderableModel)

						# Blit it on the screen the weapon - using state / position and frame id from the character's RenderableModel
						camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))


			#####
			# Blit text bubbles
			#####

			# Blit all Texts that are entities saying (CanSpeak + Position component)
			for _, (position, can_talk, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.CanTalk, components.RenderableModel)):

				# If there is something to say
				if can_talk.text:
					
					# Blit the text bubble on the position offset specified by CanTalk component
					
					if position.direction == (1,0): # RIGHT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - renderable.model.d_w - can_talk.text_rect[2], position.y - can_talk.text_rect[3])))
					
					elif position.direction == (-1,0): # if direction is (-1, 0) LEFT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x + renderable.model.d_w, position.y - can_talk.text_rect[3])))

					elif position.direction == (0,-1): # if direction is (0,-1) UP
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y + renderable.model.d_h )))

					else: # if direction is (0,1) DOWN
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y - renderable.model.d_h - can_talk.text_rect[3])))


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


class UpdateCameraOffsetProcessor(esper.Processor):
	'''Updates Camera offset based on position (Position) of the entity. Updated
	camera offset is necessary later for RenderProcessor component to correctly display
	the screen.

	Input parameters:
		-	debug

	Involved components:
		-	Position
		-	Camera

	Related processors:
		-	RenderMapProcessor
		-	RenderWorldProcessor
		-	RenderDebugProcessor

	What if this processor is disabled?
		-	scrolling will not work

	Where the processor should be planned?
		-	before RenderXXXProcessor - camera must be updated before graphics is drawn
		-	after MovementProcessor - the position of the object in camera focus must be final
	'''

	__slots__ = ['maps', 'debug']

	def __init__(self, maps, debug=False):
		''' Initiation of UpdateCameraOffsetProcessor processor.
		
		Parameters:
			:param maps: Reference to the global dict with maps
			:type maps: reference

			:param debug: Tag if processor should run in debug mode
			:type debug: bool
		'''

		super().__init__()

		self.debug = debug
		self.maps = maps

	def process(self, *args, **kwargs):
		''' Process entities having Camera and Position components. Check
		the following video for more details about camera implementation
		https://youtu.be/3zV2ewk-IGU.
		'''

		for _, (position, camera) in self.world.get_components(components.Position, components.Camera):

			# Updates camera offset based on position of the Position (component that the camera follows).

			# Offset moves opposite direction than the object + we need to keep it in the centre of the screen
			x = -position.x + camera.screen_width_half
			y = -position.y + camera.screen_height_half

			# Correction - do not centre while entity is at the edge of the map

			# In case centred camera is required then skip all corrections
			if not camera.always_center:
				# Get the reference to the map from the global dict of maps
				try:
					pos_map_ref = self.maps.get(position.map)
				except KeyError:
					raise

				# Do the corrections
				x = min(0, x)
				y = min(0, y)
				x = max(-(pos_map_ref.width - camera.screen_width), x)
				y = max(-(pos_map_ref.height - camera.screen_height), y)

			# Update the Camera offset
			camera.offset_x, camera.offset_y = x, y

			# Update camera.map_screen_rect - rectancle that specifies in pixel coordinates what part of
			# map area is displayed on the camera.screen - area should not exceed map edges, that is
			# why the correction is applied

			# tl means top-left, br means bottom-right. These are supportive variables that are added to
			# corners of the area in case that camera is at the border of the map. In those cases there
			# was a problem that the area was incorrectly calculated because the position
			# was not in the centre of the camera. Those variables are correcting this.

			# Top-left corner - initial values (camera in the centre of the screen)
			x1 = position.x - camera.screen_width_half
			y1 = position.y - camera.screen_height_half

			# Bottom-right corner - initial values (camera in the centre of the screen)
			x2 = position.x + camera.screen_width_half
			y2 = position.y + camera.screen_height_half

			# In case centred camera is required then skip all corrections
			if not camera.always_center:

				# If the camera is freezed on top or left map edge, calculate correction
				# that is later added to bottom-right corner.
				tl_dx = -x1 if x1 < 0 else 0
				tl_dy = -y1 if y1 < 0 else 0

				# If the camera is freezed on bottom or right map edge, calculate correction
				# that is later added to top-left corner.
				br_dx = -(x2 - pos_map_ref.width) if x2 > pos_map_ref.width else 0
				br_dy = -(y2 - pos_map_ref.height) if y2 > pos_map_ref.height else 0

				# Top-left corner is never negative
				x1 = max(0, x1 + br_dx)
				y1 = max(0, y1 + br_dy)

				# Bottom-right corner cannot exceed map borders
				x2 = min(pos_map_ref.width, x2 + tl_dx)
				y2 = min(pos_map_ref.height, y2 + tl_dy)

			# Update the part of map that is displayed on camera.screen
			camera.map_screen_rect = (x1, y1, x2, y2)

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (maps)
		'''
		self.maps = None

	def post_load(self, maps):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to maps again
		'''
		self.maps = maps


class MovementProcessor(esper.Processor):
	''' Updates Position component (position of an entity on the map) based on Motion
	component (movement).

	Input parameters:
		-	debug
		-	stand_delay_ms

	Involved components:
		-	Position
		-	Motion

	Related processors:
		-	CommandProcessor - movement commands generate movement

	What if this processor is disabled?
		-	movements on the map will not work

	Where the processor should be planned?
		-	before CollisionXXXProcessors - collisions are processed based on final movements
		-	before RenderXXXProcessor - camera must be updated before graphics is drawn
		-	after CommandProcessor - commands generate changes in positions
	'''

	__slots__ = ['stand_delay_ms', 'debug']

	def __init__(self, stand_delay_ms=1500, debug=False):
		''' Initiation of MovementProcessor processor.

		Parameters:
			:param stand_delay_ms: How long (ms) there must be no movement until direction is reset
			:type stand_delay_ms: int

			:param debug: Tag if processor should run in debug mode
			:type debug: bool
		'''

		super().__init__()

		self.debug = debug

		# How long entity stays without movement before reseting its direction to SOUTH
		self.stand_delay_ms = stand_delay_ms

	def process(self, *args, **kwargs):
		''' Process entities having Motion and Position components. Basically,
		add motion diffs to the position represented by Position component.
		'''

		# Get the time of processing of the frame from the game main loop in seconds
		dt = kwargs.get('dt') / 1000

		for _, (position, motion) in self.world.get_components(components.Position, components.Motion):

			# Motion can be disabled/enabled from script or brain by command
			if motion.enabled:

				# If the position of the entity needs to be updated
				if (motion.dx !=0 or motion.dy !=0):

					motion.has_moved = True

					# Save last position - used for collision resolution on Map
					position.lastx = position.x
					position.lasty = position.y
					position.lastmap = position.map
					#position.lastdir = position.direction
					motion.last_move = pygame.time.get_ticks()

					# Compensate the speed of the diagonal movement - division by sqrt(2)
					if motion.dx != 0 and motion.dy != 0:
						motion.dx *= 0.7071
						motion.dy *= 0.7071

					# Update the position by the velocity. Compensate by dt
					position.x += motion.dx * dt
					position.y += motion.dy * dt

					####
					## Update the direction
					####

					# Update the direction based on motion attributes
					position.direction = (sign(motion.dx), sign(motion.dy))

					# If movement is in both axises then use NORD-SOUTH direction
					if motion.dx != 0 and motion.dy != 0:
						position.direction = (0, position.direction[1])

					# Update dir_name
					if position.direction == (1,0): position.dir_name = 'right'
					if position.direction == (-1,0): position.dir_name = 'left'
					if position.direction == (0,1): position.dir_name = 'down'
					if position.direction == (0,-1): position.dir_name = 'up'

					# Return the velocity to 0 - movement has been processed
					motion.dx = 0
					motion.dy = 0

				# No update of velocity in this cycle
				else:
					motion.has_moved = False
					# if the time from the last movement is longer than given duration, change the direction to SOUTH
					if pygame.time.get_ticks() - motion.last_move > self.stand_delay_ms:
						position.direction = (0, 1)
						position.dir_name = 'down'


class RenderMapProcessor(esper.Processor):
	''' For rendering maps on camera screen surfaces.

	Input parameters:
		-	debug
		-	window
		-	maps

	Involved components:
		-	Position
		-	Camera

	Related processors:
		-	UpdateCameraOffsetProcessor - for enabling of scrolling

	What if this processor is disabled?
		-	no map will be rendered on the camera screens

	Where the processor should be planned?
		-	before RenderWorldProcessor - so that entities are not overdrawn by map
		-	after UpdateCameraOffsetProcessor - so that map is properly scrolled
		-	after RenderBackgroundProcessor - so that the camera screen is cleared
	'''

	__slots__ = ['window', 'maps', 'debug']

	def __init__(self, window, maps, debug=False):
		''' Initiation of RenderMapProcessor processor.

		Parameters:
			:param window: Reference to the main game surface
			:type window: pygame.Surface

			:param maps: Reference to dict of all maps
			:type maps: reference

			:param debug: Tag if processor should run in debug mode
			:type debug: bool
		'''

		super().__init__()

		self.window = window
		self.maps = maps
		self.debug = debug

	def process(self, *args, **kwargs):
		''' Process entities having Position and Camera components. Basically,
		blit the relevant part of the map on camera screen surface.
		'''

		# Find the entity with Camera and use its position
		# position - position and map of the object that is in camera's focus
		# camera - camera component itself
		for _, (position, camera) in self.world.get_components(components.Position, components.Camera):

			# Get map that is on the object in camera's focus
			map = self.maps.get(position.map)

			# Cycle through visible layers and display tiles
			for layer in map.tmxdata.visible_tile_layers:

				for x, y, tile in map.get_tile_images_by_rect(layer, camera.map_screen_rect):
					camera.screen.blit(tile, camera.apply((x * config.TILE_RES, y * config.TILE_RES)))

			# Blit the camera screen on the main game window
			self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window, maps)
		'''
		self.window = None
		self.maps = None

	def post_load(self, window, maps):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window and maps again
		'''
		self.window = window
		self.maps = maps


# TODO - Continue Here
class RenderDebugProcessor(esper.Processor):
	''' Information displayed only on visible entities
	using the filter_only_visible function.

	'''

	def __init__(self, window):

		super().__init__()
		self.window = window
		self.font = pygame.font.Font(None, 14)

	def process(self, *args, **kwargs):

		# Get information about required debug information
		debug = kwargs.get('debug', {})

		# Show debug information on all cameras
		for _, (cam_cam) in self.world.get_component(components.Camera):

			for debug_entity, (pos_comp, deb_comp, coll_debug) in filter(lambda x: filter_only_visible(cam_cam, x), self.world.get_components(components.Position, components.Debug, components.Collidable)):
				# Print collision area
				if debug.get('show_collision', False):
					try:
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((pos_comp.x - coll_debug.x,pos_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

			# Show debug information only for displayable entities with Debug flag - only for visible entities
			for debug_entity, (pos_comp, deb_comp, render_comp) in filter(lambda x: filter_only_visible(cam_cam, x), self.world.get_components(components.Position, components.Debug, components.RenderableModel)):

				# Print health
				if debug.get('show_health', False):
					try:
						damageable_debug = self.world.component_for_entity(debug_entity, components.Damageable)
						text = f'Health: {damageable_debug.health}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 60))))
					except KeyError:
						pass

				# Print status
				if debug.get('show_state', False):
					try:
						state_debug = self.world.component_for_entity(debug_entity, components.RenderableModel)
						text = f'State: {state_debug.action}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 50))))
					except KeyError:
						pass

				# Print weapons
				if debug.get('show_weapons', False):
					try:
						weapons_debug = self.world.component_for_entity(debug_entity, components.HasWeapon)
						text = f'Weapon: {weapons_debug.weapon}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 40))))
					except KeyError:
						pass

				# Print wearables
				if debug.get('show_wearables', False):
					try:
						wearables_debug = self.world.component_for_entity(debug_entity, components.CanWear)
						text = f'Wearables: {wearables_debug.wearables}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 30))))
					except KeyError:
						pass

				# Print inventory
				if debug.get('show_inventory', False):
					try:
						inventory_debug = self.world.component_for_entity(debug_entity, components.HasInventory)
						text = f'Inventory: {inventory_debug.inventory}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 20))))
					except KeyError:
						pass

				# Print labels
				if debug.get('show_labels', False):
					try:
						label_debug = self.world.component_for_entity(debug_entity, components.Labeled)
						text = str(debug_entity) + ', ' + str(label_debug.id) + ', ' + str(label_debug.name)
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 10))))
					except KeyError:
						pass

				
				# Print position
				if debug.get('show_position', False):
					try:
						pos_debug = self.world.component_for_entity(debug_entity, components.Position)
						text = 'Pos: (' + str(int(pos_debug.x)) + ', ' + str(int(pos_debug.y)) + ')' + str(pos_comp.dir_name)
						pos = deb_comp.font.render(text, True, pygame.Color('white'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y))))
					except KeyError:
						pass

				# Print brain
				if debug.get('show_brain', False):
					try:
						brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
						for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
							color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
							cmd = deb_comp.font.render(str(cmd_idx) + ' -> ' + str(cmd_txt), True, color)
							cam_cam.screen.blit(cmd, cam_cam.apply(render_comp.topleft((pos_comp.x, 10 + pos_comp.y + (cmd_idx * 10)))))
					except KeyError:
						pass

				# Print collision area
				if debug.get('show_collision', False):
					try:
						coll_debug = self.world.component_for_entity(debug_entity, components.Collidable)
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((pos_comp.x - coll_debug.x,pos_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

				# Print direction of entity
				if debug.get('show_direction', False):
					try:
						pygame.draw.line(cam_cam.screen, pygame.Color('red'), 
							cam_cam.apply((pos_comp.x, pos_comp.y)),
							cam_cam.apply((pos_comp.x + pos_comp.direction[0] * 20, pos_comp.y + pos_comp.direction[1] * 20)),
							2)
					except KeyError:
						pass

			if debug.get('show_map_screen_area', False):
				map_display_area = self.font.render(str(cam_cam.map_screen_rect), True, pygame.Color('white'))
				cam_cam.screen.blit(map_display_area, (0,0))

			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window).
		'''
		self.window = None
		self.font = None


	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window
		self.font = pygame.font.Font(None, 14)


class RenderBackgroundProcessor(esper.Processor):
	def __init__(self, window, clear_color=(0, 0, 0), debug=False):

		super().__init__()
		self.window = window
		self.clear_color = clear_color
		self.debug = debug

	def process(self, *args, **kwargs):
		# Clear the main game window surface
		self.window.fill(self.clear_color)
	
	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window)
		'''
		self.window = None

	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again
		'''
		self.window = window


# TODO - implement debug
class InputProcessor(esper.Processor):
	''' Based on user input generates commands to controll the entity.
	
	Input parameters:
		-	events - list of pressed keys passed from the main game loop
		-	input_command_queue - queue for storing commands for later processing
		-	debug

	Involved components:
		-	Controllable
	
	Related processors:
		-	CommandProcessor - for processing of commands generated by this processor

	What if this processor is disabled?
		-	game cannot be controlled by keyboard
	
	Where the processor should be planned?
		-	before CommandProcessor - before processing the commands from this processor
		-	as first of the processors - user input should have priority over AI (Brain)
	'''

	def __init__(self, input_command_queue, debug=False):
		''' Initiation of InputProcessor processor.
		'''
		super().__init__()
		self.input_command_queue = input_command_queue
		self.debug = debug

	def process(self, *args, **kwargs):
		''' Process entities having Controllable and Motion components. Read user
		input and generate corresponding commands and add them to the command queue.
		'''
		
		# Extract events and keys from parameter kwargs
		# currently only keys are used but events might be usefull as well for mouse later
		#events = kwargs.get('events', [])
		
		keys = kwargs.get('keys', [])

		# Get all entities that are controllable - not necesserilly moveable as the input can be for static entity theoretically
		for ent, (inp) in self.world.get_component(components.Controllable):

			# For each entity check if control keys were pressed and move them accordingly
			# only process if keys are enabled.
			if inp.enabled:

				# Move up
				if keys[inp.control_keys.get('up')]:
					self.input_command_queue.append((inp.control_cmds.get('up'), {"entity" : ent, "dy" : -config.MOVE_SPEED}))

				# Move down
				if keys[inp.control_keys.get('down')]:
					self.input_command_queue.append((inp.control_cmds.get('down'), {"entity" : ent, "dy" : config.MOVE_SPEED}))

				# Move left
				if keys[inp.control_keys.get('left')]:
					self.input_command_queue.append((inp.control_cmds.get('left'), {"entity" : ent, "dx" : -config.MOVE_SPEED}))

				# Move right
				if keys[inp.control_keys.get('right')]:
					self.input_command_queue.append((inp.control_cmds.get('right'), {"entity" : ent, "dx" : config.MOVE_SPEED}))

				# Attack
				if keys[inp.control_keys.get('attack')]:
					self.input_command_queue.append((inp.control_cmds.get('attack'), {"entity" : ent}))
				
				# If none above buttons are presed
				#if not (keys[inp.control_keys.get('up')]
				#	or keys[inp.control_keys.get('up')]
				#	or keys[inp.control_keys.get('up')]
				#	or keys[inp.control_keys.get('up')]):


	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (none)
		'''
		pass

	def post_load(self, input_command_queue):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again
		'''
		self.input_command_queue = input_command_queue

#continue here
class CollisionMapProcessor(esper.Processor):
	''' Checks for collisions with the titles on the map.
	'''

	def __init__(self, maps):
		''' maps is link to global dict of maps
		'''
		super().__init__()

		self.maps = maps
	
	def process(self, *args, **kwargs):

		# Do collision against the map 
		for ent_moved, (coll_moved, pos_moved) in self.world.get_components(components.Collidable, components.Position):
			
			# Get collision map using the global dict of maps
			#collision_map = self.maps.get(pos_moved.map).collision_map
			collision_map = self.maps.get(pos_moved.map)

			# Get the map position where the entity is situated
			
			# Topleft corner is situated
			#if (collision_map[int(pos_moved.y - coll_moved.y) // 64][int(pos_moved.x - coll_moved.x) // 64] != 0 or
			#	# Topright corner is situated
			#	collision_map[int(pos_moved.y - coll_moved.y) // 64][int(pos_moved.x + coll_moved.x) // 64] != 0 or
			#	# Bottomleft corner
			#	collision_map[int(pos_moved.y + coll_moved.y) // 64][int(pos_moved.x - coll_moved.x) // 64] != 0 or
			#	# Bottom right corner
			#	collision_map[int(pos_moved.y + coll_moved.y) // 64][int(pos_moved.x + coll_moved.x) // 64] != 0):

			# NEW check collisions by function collision_map.check_collision(((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)))
			if (collision_map.check_collision((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)) or 
				collision_map.check_collision((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y + coll_moved.y) // 64)) or
				collision_map.check_collision((int(pos_moved.x + coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)) or
				collision_map.check_collision((int(pos_moved.x + coll_moved.x) // 64),(int(pos_moved.y + coll_moved.y) // 64))):

				# Fix position for the entity that has moved
				pos_moved.x = pos_moved.lastx
				pos_moved.y = pos_moved.lasty

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components
		'''
		self.maps = None

	def post_load(self, maps):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to maps again
		'''
		self.maps = maps


class CollisionEntityGeneratorProcessor(esper.Processor):
	''' Unlike CollisionEntityGeneratorProcessorFullScan, this processor
	checks only entities that are visible on one of the camera screens.

	
	-	COLLISION SYSTEM
			Checks for collisions and resolves them
			-	COLLISION + MOTION - Only entities that has moved are checked for collision
			-	COLLISION + POSITION - Above entities are checked against Collision and Position.
	'''

	def __init__(self):
		super().__init__()
		

	def process(self, *args, **kwargs):

		# For all camera screens in the game window
		for _, (camera) in self.world.get_component(components.Camera):

			# Get all entities that have Motion and Collidable (only those can activelly hit something) - i.e. that could have moved and iterate those
			for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.Collidable)):
				# Compare that all collision + position entities - DUMMY WAY
				for ent_other, (pos_other, coll_other) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.Collidable)):
					
					# Heuristic no.-1 - Test only those that have Motion component
					#if not self.world.has_component(ent_moved, Motion): continue

					# Heuristic no.0 - Test only those that have moved component
					#if not self.world.component_for_entity(ent_moved, Motion).has_moved: continue

					# Heuristic no.1 - Skip if testing itself
					if ent_moved == ent_other: continue

					# Heuristic no 1.5 - Test only entities on the same map
					if pos_moved.map != pos_other.map: continue

					# Heuristic no.2 - Test only those in close distance
					#if abs(pos_moved.x - pos_other.y) > 200 or abs(pos_moved.y - pos_other.y) > 200: continue 

					# Heuristic no.3 - Do not test twice the same double of entities, i.e. 1,3 and 3,1
					
					# AABB comaprison - Collision
					if(pos_moved.x - coll_moved.x < pos_other.x + coll_other.x and
						pos_moved.x + coll_moved.x > pos_other.x - coll_other.x and
						pos_moved.y - coll_moved.y < pos_other.y + coll_other.y and
						pos_moved.y + coll_moved.y > pos_other.y - coll_other.y):
						
						# Add collision to the collision component 
						coll_other.collision_events.add(ent_moved)
						#coll_moved.collision_events.add(ent_other)


class CollisionTeleportProcessor(esper.Processor):
	def __init__(self, teleport_event_queue):
		super().__init__()

		self.teleport_event_queue = teleport_event_queue

	def process(self, *args, **kwargs):
		for ent, (teleport, collision) in self.world.get_components(components.Teleport, components.Collidable):

			# Process everything that collided with teleport
			for col_event_entity in collision.collision_events.copy():
					
					# If entity is Teleportable and has position
					if self.world.has_components(col_event_entity, components.Teleportable, components.Position, components.Collidable):
						
						# Get the Position, Collidable and HasInventory component of the teleportee entity
						col_event_entity_pos = self.world.component_for_entity(col_event_entity, components.Position) 
						col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)
						try:
							col_event_entity_inventory = self.world.component_for_entity(col_event_entity, components.HasInventory)
							
							# Does the teleportee have the key in the inventory?
							# Either no key is required by the teleport or key is in teleportees inventory
							teleportee_has_key = teleport.key is None or teleport.key in col_event_entity_inventory.inventory

						except KeyError:
							teleportee_has_key = teleport.key is None

						# Do the teleportation of the teleportee - only if it has the key (by default no key necessary)
						if teleportee_has_key:
							col_event_entity_pos.x = teleport.dest_x
							col_event_entity_pos.y = teleport.dest_y
							col_event_entity_pos.map = teleport.dest_map 

							# Report that teleportation occured - generate event
							teleport_event = event.Event('TELEPORTATION', ent, col_event_entity, params={'teleport' : ent, 'teleportee' : col_event_entity})
							self.teleport_event_queue.append(teleport_event)

						# Remove the col_event_entity from Teleport
						collision.collision_events.remove(col_event_entity)

						# Remove the col event related to teleport from the Entity
						col_event_entity_coll.collision_events.remove(ent)


class CollisionDamageProcessor(esper.Processor):
	def __init__(self, damage_event_queue):
		super().__init__()
		self.damage_event_queue = damage_event_queue

	def process(self, *args, **kwargs):

		for ent, (damaging, collision) in self.world.get_components(components.Damaging, components.Collidable):

			# Process everything that collided with Damaging entity
			for col_event_entity in collision.collision_events.copy():

				# If hitted component has Damageble component then proceed
				if self.world.has_component(col_event_entity, components.Damageable):

					# Get the Damageble component of the entity that was hit by the Projectile
					col_event_entity_damageable = self.world.component_for_entity(col_event_entity, components.Damageable) 
					
					# Get the Collidable component of the entity that was hitted - in order to remove the collision
					col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

					# Decrease the health
					col_event_entity_damageable.health -= damaging.damage

					#try:
					#	# Remove Position component from the weapon so that it is not displayable on the map - weapon is picked
					#	self.world.remove_component(ent, components.Position) 
					#	# Remove Camera component from the weapon so that the screen disappears - weapon is picked
					#	self.world.remove_component(ent, components.Camera) 
					#except KeyError:
					#	pass

					# Remove the col_event_entity from Damagable entity
					collision.collision_events.remove(col_event_entity)

					# Remove the col event related to item from the Damaging
					col_event_entity_coll.collision_events.remove(ent)

					# Report that item was hit - generate event
					damage_event = event.Event('DAMAGE', ent, col_event_entity, params={'damaging' : ent, 'damaged' : col_event_entity})
					self.damage_event_queue.append(damage_event)


class CollisionWeaponProcessor(esper.Processor):
	def __init__(self, weapon_event_queue):
		super().__init__()
		self.weapon_event_queue = weapon_event_queue

	def process(self, *args, **kwargs):
		for ent, (item, collision) in self.world.get_components(components.Weapon, components.Collidable):

			# Process everything that collided with weapon entity
			for col_event_entity in collision.collision_events.copy():
					
					# If entity (that have collided with weapon) can wear weapons items (HasWeapon)
					if self.world.has_component(col_event_entity, components.HasWeapon):
						
						# Get the HasWeapon component of the entity that picked up Weapon
						col_event_entity_has_weapon = self.world.component_for_entity(col_event_entity, components.HasWeapon) 
						
						# Get the Collidable component of the entity that picked up Weapon - in order to remove the collision
						col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

						# Add weapon to the HasWeapon - only in case that the slot for Weapon is available
						if not col_event_entity_has_weapon.weapon:
							col_event_entity_has_weapon.weapon = ent

							# Store the action connected to the weapon in the hasWeapon component
							col_event_entity_has_weapon.action = self.world.component_for_entity(ent, components.Weapon).action

							try:
								# Remove Position component from the weapon so that it is not displayable on the map - weapon is picked
								self.world.remove_component(ent, components.Position) 
								# Remove Camera component from the weapon so that the screen disappears - weapon is picked
								self.world.remove_component(ent, components.Camera) 
							except KeyError:
								pass

							# Remove the col_event_entity from HasWeapon entity
							collision.collision_events.remove(col_event_entity)

							# Remove the col event related to item from the Weapon
							col_event_entity_coll.collision_events.remove(ent)

							# Report that item was weared - generate event
							weapon_event = event.Event('WEAPON_ARMED', ent, col_event_entity, params={'weapon' : ent, 'picker' : col_event_entity})
							self.weapon_event_queue.append(weapon_event)


class CollisionWearableProcessor(esper.Processor):
	def __init__(self, wearable_event_queue):
		super().__init__()
		self.wearable_event_queue = wearable_event_queue

	def process(self, *args, **kwargs):
		for ent, (item, collision) in self.world.get_components(components.Wearable, components.Collidable):

			# Process everything that collided with wearable entity
			for col_event_entity in collision.collision_events.copy():
					
					# If entity (that have collided with wearable) can wear items (CanWear)
					if self.world.has_component(col_event_entity, components.CanWear):
						
						# Get the CanWear component of the entity that picked up Wearable
						col_event_entity_can_wear = self.world.component_for_entity(col_event_entity, components.CanWear) 
						
						# Get the Collidable component of the entity that picked up Wearable - in order to remove the collision
						col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

						# Add wearable to the CanWear wearables - only in case that the slot for Wearable is available
						if not col_event_entity_can_wear.wearables.get(item.bodypart, None):
							col_event_entity_can_wear.wearables.update({item.bodypart : ent})

							try:
								# Remove Position component from the wearable so that it is not displayable on the map - wearable is picked
								self.world.remove_component(ent, components.Position) 
								# Remove Camera component from the wearable so that the screen disappears - wearable is picked
								self.world.remove_component(ent, components.Camera) 
							except KeyError:
								pass

							# Remove the col_event_entity from CanWear entity
							collision.collision_events.remove(col_event_entity)

							# Remove the col event related to item from the Wearable
							col_event_entity_coll.collision_events.remove(ent)

							# Report that item was weared - generate event
							wear_event = event.Event('WEARABLE_WEARED', ent, col_event_entity, params={'wearable' : ent, 'picker' : col_event_entity})
							self.wearable_event_queue.append(wear_event)


class CollisionItemProcessor(esper.Processor):
	def __init__(self, item_pickup_event_queue):
		super().__init__()
		self.item_pickup_event_queue = item_pickup_event_queue

	def process(self, *args, **kwargs):
		for ent, (item, collision) in self.world.get_components(components.Pickable, components.Collidable):

			# Process everything that collided with item
			for col_event_entity in collision.collision_events.copy():
					
					# If entity can collect items (has inventory)
					if self.world.has_component(col_event_entity, components.HasInventory):
						
						# Get the HasItem component of the entity
						col_event_entity_inventory = self.world.component_for_entity(col_event_entity, components.HasInventory) 
						
						# Get the Collidable component of the entity - in order to remove the collision
						col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

						# Add the Item entity into the HasInventory,inventory list
						col_event_entity_inventory.inventory.append(ent)

						# Remove Position component from the item so that it is not displayable on the map - item is picked
						self.world.remove_component(ent, components.Position) 

						# Remove Camera component from the item so that the screen disappears - item is picked
						try:
							self.world.remove_component(ent, components.Camera) 
						except KeyError:
							pass

						# Remove the col_event_entity from Item entity
						collision.collision_events.remove(col_event_entity)

						# Remove the col event related to item from the Entity
						col_event_entity_coll.collision_events.remove(ent)

						# Report that item was picked up - generate event
						teleport_event = event.Event('ITEM_PICKUP', ent, col_event_entity, params={'item' : ent, 'picker' : col_event_entity})
						self.item_pickup_event_queue.append(teleport_event)


# TODO - this does not work well - collision of player and npc with brain does not work - player cannot colide but npc can walk into the player
# This is because first entity 1 is fixed and all related collisions with number 1 are deleted, so also NPCs collision events are deleted before they are processed
class CollisionEntityProcessor(esper.Processor):
	''' It is basically CollisionCorrectorProcessor but also generates events
	on collisions
	'''

	def __init__(self, entity_coll_event_queue, input_command_queue):
		super().__init__()
		self.entity_coll_event_queue = entity_coll_event_queue
		self.input_command_queue = input_command_queue

	def process(self, *args, **kwargs):

		for ent, (position, collision) in self.world.get_components(components.Position, components.Collidable):

			##### New collision process
			# 1. Iterate all collidable entities
			# 2. Iterate all entities with whom there was a collision
			# 3. Generate collision event
			# 4. Calculate the positions so that objects are not collided - do not use last position - this was causing stuck states

			for col_event_entity in collision.collision_events.copy():

				# Report that entity collision occured - generate event
				collision_event = event.Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
				self.entity_coll_event_queue.append(collision_event)

				# Calculate and update possition
				col_event_entity_pos = self.world.component_for_entity(col_event_entity, components.Position)
				col_event_entity_collidable = self.world.component_for_entity(col_event_entity, components.Collidable)

				# collision on X axis (distance is lower then coll area)
				if abs(col_event_entity_pos.x - position.x) < (col_event_entity_collidable.x + collision.x):
					# Call move 
					if position.x < col_event_entity_pos.x: 
						self.input_command_queue.append(('move', {"entity" : ent, "dx" : -config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dx" : config.MOVE_SPEED}))
					else:
						self.input_command_queue.append(('move', {"entity" : ent, "dx" : config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dx" : -config.MOVE_SPEED}))
					
					# position.x = position.lastx
					# col_event_entity_pos.x = col_event_entity_pos.lastx

				# collision on Y axis (distance is lower then coll area)
				if abs(col_event_entity_pos.y - position.y) <= (col_event_entity_collidable.y + collision.y) + 10:
					# Call move 
					if position.y < col_event_entity_pos.y: 
						self.input_command_queue.append(('move', {"entity" : ent, "dy" : -config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dy" : config.MOVE_SPEED}))
					else:
						self.input_command_queue.append(('move', {"entity" : ent, "dy" : config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dy" : -config.MOVE_SPEED}))
					
					
					# try to use last position for both
					#position.y = position.lasty
					#col_event_entity_pos.y = col_event_entity_pos.lasty

				# Remove the col_event_entity from  entity
				collision.collision_events.remove(col_event_entity)


			''' Old process
			# If some collision occured, the collision_event set is not empty
			if collision.collision_events:
				
				# Fix position for the entity that has moved
				position.x = position.lastx
				position.y = position.lasty

			# Process everything that collided with entity ent
			for col_event_entity in collision.collision_events.copy():

				# Report that entity collision occured - generate event
				collision_event = Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
				self.entity_coll_event_queue.append(collision_event)

				# Fix position for the entity that has moved
				#position.x = position.lastx
				#position.y = position.lasty

				##### All below is for removal of collision event from the entities
				# Get the Collidable component of the entity - in order to remove the collision
				
				# Below commented as it caused that NPCs were walking into player
				#col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

				# Remove the col event related to item from the Entity
				# Below commented as it caused that NPCs were walking into player
				#col_event_entity_coll.collision_events.remove(ent)

				# Remove the col_event_entity from  entity
				collision.collision_events.remove(col_event_entity)
			'''


class BrainProcessor(esper.Processor):

	def __init__(self, input_command_queue):
		super().__init__()
		
		self.input_command_queue = input_command_queue

	def process(self, *args, **kwargs):
		for ent, (brain) in self.world.get_component(components.Brain):
			
			# Only continue processing if the brain is enabled
			if brain.enabled:

				# Get the command unit for processing
				try:
					unit = brain.commands[brain.next_cmd_idx]
				except:
					print(f'No command found, disabling brain. {brain}')
					brain.enabled = False
					return
				
				# Move pointers - next_cmd_idx is not yet decided, depends on the result of unit execution
				brain.last_cmd_idx = brain.current_cmd_idx
				brain.current_cmd_idx = brain.next_cmd_idx
				
				# Parse command unit - cmd_fnc is string
				_, cmd_fnc, cmd_params = unit

				# Put the command into the queue for processing - entity and brain can be override by the command
				# itself. It is used for global scripting functionality.
				self.input_command_queue.append((cmd_fnc, {**{"entity" : ent, "brain" : brain}, **cmd_params}))

				# If the unit exist then check if it was previously called
				# remember the self.unit_first_call_time
				if brain.next_cmd_idx != brain.last_cmd_idx:
					brain.cmd_first_call_time = pygame.time.get_ticks()
					#print(f'Setting up first call cmd time: {cmd_fnc}')

				# DEBUG
				#print(f'CMD inserted - Cmd: {cmd_fnc}, last_idx: {brain.last_cmd_idx}, current_idx: {brain.current_cmd_idx}, next_idx: {brain.next_cmd_idx}')

				# The result of the command will be communicated by the command_queue directly to component function
				#brain.process_resutt()


class GameEventsProcessor(esper.Processor):

	def __init__(self, game_event_handler):
		super().__init__()

		self.game_event_handler = game_event_handler

	def process(self, *args, **kwargs):
		''' Call external function that processes all events
		'''
		self.game_event_handler()


class CommandProcessor(esper.Processor):

	def __init__(self, game_commands_handler, debug=False):
		super().__init__()

		self.game_commands_handler = game_commands_handler
		self.debug = debug

	def process(self, *args, **kwargs):
		''' Call external function that processes all commands
		'''

		self.game_commands_handler(self.debug)

########################################################
### Processors Classes - NOT USED
########################################################

class RenderMapProcessorFullScan(esper.Processor):
	''' For rendering maps on camera surfaces. 
	
	For ALL maps ALL TILES are blitted - even those that are out of visible area.
	
	Hence this is not optimal version of the RenderMapProcessor.
	'''

	def __init__(self, window, maps, tile_res=64, debug=False):
		'''
		'''
		super().__init__()
		self.window = window
		self.maps = maps
		self.tile_res = tile_res
		self.debug = debug

	def process(self, *args, **kwargs):
		''' 
		'''
		
		# Find the entity with Camera and use its position
		# cam_pos - position and map of the object that is in camera's focus
		# cam_cam - camera component itself
		for _ , (cam_pos, cam_cam) in self.world.get_components(components.Position, components.Camera):

			# Clear the camera surface
			cam_cam.screen.fill((0,0,0))

			# Get map that is on the object in camera's focus
			map = self.maps.get(cam_pos.map)

			# Blit the map ground layer			
			for i in range(len(map.ground_layer)): # Y axis	
				for j in range(len(map.ground_layer[0])): # X axis
					if map.ground_layer[i][j] != 0:
						#cam_cam.screen.blit(map.get_tile('ground', j, i), self.apply_camera(cam_cam, (j * self.tile_res, i * self.tile_res)))
						cam_cam.screen.blit(map.get_tile_image(j, i, 'ground'), cam_cam.apply((j * self.tile_res, i * self.tile_res)))

			# Blit the map wall layer
			for i in range(len(map.wall_layer)): # Y axis	
				for j in range(len(map.wall_layer[0])): # X axis
					if map.wall_layer[i][j] != 0:
						#cam_cam.screen.blit(map.get_tile('wall', j, i), self.apply_camera(cam_cam, (j * self.tile_res, i * self.tile_res)))
						cam_cam.screen.blit(map.get_tile_image(j, i, 'wall'), cam_cam.apply((j * self.tile_res, i * self.tile_res)))
		
						

			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window, maps)
		'''
		self.window = None
		self.maps = None

	def post_load(self, window, maps):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window and maps again
		'''
		self.window = window
		self.maps = maps

class RenderModelWorldProcessorDifferentFramesOnCameras(esper.Processor):
	''' 
	WHY OBSOLETE?
	^^^^^^^^^^^^^
	NOTE - This version was marked as obsolete because of the problem 
	with generating of weapon collision zone when Renderable model weapon
	action reaches the last animation frame.

	The problem is that in this implementation if one character is shown 
	on multiple cameras, the frame can be on every camera different. The
	reason is that for each camera iteration the processor is asking for 
	the model frame again - and in this get_frame function, changing of frame
	can happen (due to change of animation duration).

	This processor will be substituted by the new version that will always
	display same model frame on all cameras. This will be achieved by adding
	new processor that will update all models once and new RenderModelWorldProcessor
	will only read the frame from RenderableModel - not any shifts in frames.

	Draws the entities in the world. Unlike RenderWorldProcessor
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
			for ent, (position, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel)):
				camera.screen.blit(renderable.get_frame(position.dir_name, renderable.action), camera.apply(renderable.topleft((position.x, position.y))))

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
							camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))

				#####
				# Blit weapons for those displayable- using body information in order to sync the animations
				#####

				# Blit all weapons for the above Entity - if possible
				if self.world.has_component(ent, components.HasWeapon):

					# Get the HasWeapon component of the entity that picked up Weapon
					has_weapon = self.world.component_for_entity(ent, components.HasWeapon)

					# Get the weapon entity - RenderableModel
					if has_weapon.weapon:
						w_renderable = self.world.component_for_entity(has_weapon.weapon, components.RenderableModel)

						# Blit it on the screen the weapon - using state / position and frame id from the character's RenderableModel
						camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))


			#####
			# Blit text bubbles
			#####

			# Blit all Texts that are entities saying (CanSpeak + Position component)
			for _, (position, can_talk, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.CanTalk, components.RenderableModel)):

				# If there is something to say
				if can_talk.text:
					
					# Blit the text bubble on the position offset specified by CanTalk component
					
					if position.direction == (1,0): # RIGHT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - renderable.model.d_w - can_talk.text_rect[2], position.y - can_talk.text_rect[3])))
					
					elif position.direction == (-1,0): # if direction is (-1, 0) LEFT
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x + renderable.model.d_w, position.y - can_talk.text_rect[3])))

					elif position.direction == (0,-1): # if direction is (0,-1) UP
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y + renderable.model.d_h )))

					else: # if direction is (0,1) DOWN
						camera.screen.blit(can_talk.text_surf, 
							camera.apply((position.x - can_talk.text_rect[2] / 2, position.y - renderable.model.d_h - can_talk.text_rect[3])))


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

class RenderWorldProcessor(esper.Processor):
	''' Draws the entities in the world. Entity is represented just by
	the picture stored in Renderable component.

	This is substituted by RenderModelWorldProcessor which supports 
	animated entities by using RenderModel component.

	Also this component does not use filter to draw only entities that 
	are currently displayable on the screen.
	
	Input parameters:
		-	window - reference to main game screen
		-	debug

	Involved components:
		-	Position
		-	Camera
		-	Renderable
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

			# Blit all the Entities that have Renderable and Position components
			for _ , (renderable, position) in self.world.get_components(components.Renderable, components.Position):
				camera.screen.blit(renderable.image, camera.apply(renderable.topleft((position.x, position.y))))

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

class CollisionMapProcessorFullScan(esper.Processor):
	''' Checks for collisions with the titles on the map.

	It checks collisions for all world entities. Unlike 
	CollisionMapProcessor that checks collisions only for the
	entities that are visible on the map.

	'''

	def __init__(self, maps):
		''' maps is link to global dict of maps
		'''
		super().__init__()

		self.maps = maps
	
	def process(self, *args, **kwargs):
		
		# Do collision against the map
		for ent_moved, (coll_moved, pos_moved) in self.world.get_components(components.Collidable, components.Position):
			
			# Get collision map using the global dict of maps
			#collision_map = self.maps.get(pos_moved.map).collision_map
			collision_map = self.maps.get(pos_moved.map)

			# Get the map position where the entity is situated
			
			# Topleft corner is situated
			#if (collision_map[int(pos_moved.y - coll_moved.y) // 64][int(pos_moved.x - coll_moved.x) // 64] != 0 or
			#	# Topright corner is situated
			#	collision_map[int(pos_moved.y - coll_moved.y) // 64][int(pos_moved.x + coll_moved.x) // 64] != 0 or
			#	# Bottomleft corner
			#	collision_map[int(pos_moved.y + coll_moved.y) // 64][int(pos_moved.x - coll_moved.x) // 64] != 0 or
			#	# Bottom right corner
			#	collision_map[int(pos_moved.y + coll_moved.y) // 64][int(pos_moved.x + coll_moved.x) // 64] != 0):

			# NEW check collisions by function collision_map.check_collision(((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)))
			if (collision_map.check_collision((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)) or 
				collision_map.check_collision((int(pos_moved.x - coll_moved.x) // 64),(int(pos_moved.y + coll_moved.y) // 64)) or
				collision_map.check_collision((int(pos_moved.x + coll_moved.x) // 64),(int(pos_moved.y - coll_moved.y) // 64)) or
				collision_map.check_collision((int(pos_moved.x + coll_moved.x) // 64),(int(pos_moved.y + coll_moved.y) // 64))):

				# Fix position for the entity that has moved
				pos_moved.x = pos_moved.lastx
				pos_moved.y = pos_moved.lasty

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components
		'''
		self.maps = None

	def post_load(self, maps):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to maps again
		'''
		self.maps = maps

class CollisionEntityGeneratorProcessorFullScan(esper.Processor):
	''' 
	-	COLLISION SYSTEM
			Checks for collisions and resolves them
			-	COLLISION + MOTION - Only entities that has moved are checked for collision
			-	COLLISION + POSITION - Above entities are checked against Collision and Position.
	'''

	def __init__(self):
		super().__init__()
		

	def process(self, *args, **kwargs):
			
		# Get all entities that have Motion and Collidable (only those can activelly hit something) - i.e. that could have moved and iterate those
		for ent_moved, (coll_moved, pos_moved) in self.world.get_components(components.Collidable, components.Position):
			# Compare that all collision + position entities - DUMMY WAY
			for ent_other, (coll_other, pos_other) in self.world.get_components(components.Collidable, components.Position):
				
				# Heuristic no.-1 - Test only those that have Motion component
				#if not self.world.has_component(ent_moved, Motion): continue

				# Heuristic no.0 - Test only those that have moved component
				#if not self.world.component_for_entity(ent_moved, Motion).has_moved: continue

				# Heuristic no.1 - Skip if testing itself
				if ent_moved == ent_other: continue

				# Heuristic no 1.5 - Test only entities on the same map
				if pos_moved.map != pos_other.map: continue

				# Heuristic no.2 - Test only those in close distance
				#if abs(pos_moved.x - pos_other.y) > 200 or abs(pos_moved.y - pos_other.y) > 200: continue 

				# Heuristic no.3 - Do not test twice the same double of entities, i.e. 1,3 and 3,1
				
				# AABB comaprison - Collision
				if(pos_moved.x - coll_moved.x < pos_other.x + coll_other.x and
					pos_moved.x + coll_moved.x > pos_other.x - coll_other.x and
					pos_moved.y - coll_moved.y < pos_other.y + coll_other.y and
					pos_moved.y + coll_moved.y > pos_other.y - coll_other.y):
					
					# Add collision to the collision component 
					coll_other.collision_events.add(ent_moved)
					#coll_moved.collision_events.add(ent_other)

class CollisionCorrectorProcessor(esper.Processor):
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		for ent, (collision, position) in self.world.get_components(components.Collidable, components.Position):
			
			# If some collision occured, the collision_event set is not empty
			if collision.collision_events:
				
				# Fix position for the entity that has moved
				position.x = position.lastx
				position.y = position.lasty

				# Clear all collisions
				collision.collision_events.clear()

class RenderDebugProcessorFullScan(esper.Processor):
	''' Information displayed only on visible entities
	using the filter_only_visible function.

	'''

	def __init__(self, window):

		super().__init__()
		self.window = window
		self.font = pygame.font.Font(None, 14)

	def process(self, *args, **kwargs):

		# Get information about required debug information
		debug = kwargs.get('debug', {})

		# Show debug information on all cameras
		for _, (cam_cam) in self.world.get_component(components.Camera):

			# Show debug information only for displayable entities with Debug flag - only for visible entities
			for debug_entity, (pos_comp, deb_comp, render_comp) in self.world.get_components(components.Position, components.Debug, components.Renderable):

				# Print inventory
				if debug.get('show_inventory', False):
					try:
						inventory_debug = self.world.component_for_entity(debug_entity, components.HasInventory)
						text = f'Inventory: {inventory_debug.inventory}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 20))))
					except KeyError:
						pass

				# Print labels
				if debug.get('show_labels', False):
					try:
						label_debug = self.world.component_for_entity(debug_entity, components.Labeled)
						text = str(debug_entity) + ', ' + str(label_debug.id) + ', ' + str(label_debug.name)
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 10))))
					except KeyError:
						pass

				
				# Print position
				if debug.get('show_position', False):
					try:
						pos_debug = self.world.component_for_entity(debug_entity, components.Position)
						text = 'Pos: (' + str(int(pos_debug.x)) + ', ' + str(int(pos_debug.y)) + ')' + str(pos_comp.dir_name)
						pos = deb_comp.font.render(text, True, pygame.Color('white'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y))))
					except KeyError:
						pass

				# Print brain
				if debug.get('show_brain', False):
					try:
						brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
						for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
							color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
							cmd = deb_comp.font.render(str(cmd_idx) + ' -> ' + str(cmd_txt), True, color)
							cam_cam.screen.blit(cmd, cam_cam.apply(render_comp.topleft((pos_comp.x, 10 + pos_comp.y + (cmd_idx * 10)))))
					except KeyError:
						pass

				# Print collision area
				if debug.get('show_collision', False):
					try:
						coll_debug = self.world.component_for_entity(debug_entity, components.Collidable)
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((pos_comp.x - coll_debug.x,pos_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

				# Print direction of entity
				if debug.get('show_direction', False):
					try:
						pygame.draw.line(cam_cam.screen, pygame.Color('red'), 
							cam_cam.apply((pos_comp.x, pos_comp.y)),
							cam_cam.apply((pos_comp.x + pos_comp.direction[0] * 20, pos_comp.y + pos_comp.direction[1] * 20)),
							2)
					except KeyError:
						pass

			if debug.get('show_map_screen_area', False):
				map_display_area = self.font.render(str(cam_cam.map_screen_rect), True, pygame.Color('white'))
				cam_cam.screen.blit(map_display_area, (0,0))

			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window).
		'''
		self.window = None
		self.font = None


	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window
		self.font = pygame.font.Font(None, 14)