import core.ecs.esper as esper
import core.ecs.components as components
import core.config.config as config

import pygame
import random
import time 
import logging

from functools import wraps

########################################################
### Package init commands
########################################################

logger = logging.getLogger('processors')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(config.LOG_PATH + 'proc_perf.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

########################################################
### Decorators
########################################################

def time_dec(f):
	@wraps(f)
	def wrapped(*args, **kwargs):
		start = time.time()
		r = f(*args, **kwargs)
		if config.DEBUG.get('log_performance', False): logger.info(f'Method {f} took {(time.time() - start) * 1000} msecs.')
		return r
	return wrapped

########################################################
### Event class
########################################################

class Event:
	''' Class encapsulating event sent by event dispatcher
	'''
	
	EVENT_TYPES = ['COLLISION','TELEPORTATION', 'ITEM_PICKUP']
	
	def __init__(self, event_type, generator_obj, other_obj, params={}):
		
		assert(event_type in Event.EVENT_TYPES)
		
		self.event_type = event_type
		self.generator_obj = generator_obj
		self.other_obj = other_obj
		self.params = params
	
	def __str__(self):
		return f'*Event type:\t{self.event_type}\nSource entity:\t{self.generator_obj}\nDestination entity:\t{self.other_obj}\nParams:\t{self.params}\n'


########################################################
### Processors Classes
########################################################

# TODO - Implement debug
class UpdateCameraOffsetProcessor(esper.Processor):
	'''Updates Camera offset based on position (Transform) of the entity. Updated
	camera offset is necessary later for RenderProcessor component to correctly display
	the screen.
	
	Input parameters:
		-	debug

	Involved components:
		-	Transform
		-	Camera
	
	Related processors:
		-	RenderProcessor

	What if this processor is disabled?
		-	scrolling will not work
	
	Where the processor should be planned?
		-	before RenderProcessor - camera must be updated before graphics is drawn
		-	after MovementProcessor - the position of the object in camera focus must be final
	'''

	def __init__(self, maps, debug=False):
		''' Initiation of CameraProcessor processor.
		'''
		super().__init__()
		
		self.debug = debug
		self.maps = maps

	@time_dec
	def process(self, *args, **kwargs):
		''' Process entities having Camera and Transform components. Check
		the following video for more details about camera implementation
		https://youtu.be/3zV2ewk-IGU.
		'''

		for _ , (transform, camera) in self.world.get_components(components.Transform, components.Camera):
			
			# Updates camera offset based on position of the Transform (component that the camera follows). 

			# Offset moves opposite direction than the object + we need to keep it in the centre of the screen
			#x = -transform.x + int(camera.screen_width / 2)
			#y = -transform.y + int(camera.screen_height / 2)
			x = -transform.x + camera.screen_width_half
			y = -transform.y + camera.screen_height_half
		
			# Correction - do not centre while entity is at the edge of the map

			# In case centred camera is required then skip all corrections
			if not camera.always_center:
				# Get the reference to the map from the global dict of maps
				try:
					trans_map_ref = self.maps.get(transform.map)
				except KeyError:
					raise

				# Do the correction
				x = min(0, x)
				y = min(0, y)
				x = max(-(trans_map_ref.width - camera.screen_width), x)
				y = max(-(trans_map_ref.height - camera.screen_height), y)

			# Update the Camera offset
			camera.offset_x, camera.offset_y = x, y

			# Update camera.map_screen_rect - rectancle that specifies in pixel coordinates what part of 
			# map area is displayed on the camera.screen - area should not exceed map edges, that is
			# why the correction is applied
			
			# tl means top-left, br means bottom-right. These are supportive variables that are added to
			# corners of the area in case that camera is at the border of the map. In those cases there
			# was a problem that the area was incorrectly calculated because the transform position 
			# was not in the centre of the camera. Those variables are correcting this.

			# Top-left corner - initial values (camera in the centre of the screen)
			x1 = transform.x - camera.screen_width_half
			y1 = transform.y - camera.screen_height_half

			# Bottom-right corner - initial values (camera in the centre of the screen)
			x2 = transform.x + camera.screen_width_half
			y2 = transform.y + camera.screen_height_half

			# In case centred camera is required then skip all corrections
			if not camera.always_center:

				# If the camera is freezed on top or left map edge, calculate correction
				# that is later added to bottom-right corner.
				tl_dx = -x1 if x1 < 0 else 0
				tl_dy = -y1 if y1 < 0 else 0			

				# If the camera is freezed on bottom or right map edge, calculate correction
				# that is later added to top-left corner.
				br_dx = -(x2 - trans_map_ref.width) if x2 > trans_map_ref.width else 0
				br_dy = -(y2 - trans_map_ref.height) if y2 > trans_map_ref.height else 0

				# Top-left corner is never negative
				x1 = max(0, x1 + br_dx)
				y1 = max(0, y1 + br_dy)

				# Bottom-right corner cannot exceed map borders
				x2 = min(trans_map_ref.width , x2 + tl_dx)
				y2 = min(trans_map_ref.height, y2 + tl_dy)

			# Update the part of map that is displayed on camera.screen
			camera.map_screen_rect = (x1, y1 , x2, y2)

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


# TODO - use vector2 for transform and motion
# TODO - implement debug
# TODO - implement direction
class MovementProcessor(esper.Processor):
	''' Updates Transform component (position of an entity on the map) based on Motion
	component (movement).
	
	Input parameters:
		-	debug

	Involved components:
		-	Transform
		-	Motion
	
	Related processors:
		-	CommandProcessor - movement commands generate movement

	What if this processor is disabled?
		-	movements on the map will not work
	
	Where the processor should be planned?
		-	before RenderProcessor - camera must be updated before graphics is drawn
		-	after MovementProcessor - the position of the object in camera focus must be final
	'''

	def __init__(self, stand_delay_ms=1500, debug=False):
		''' Initiation of MovementProcessor processor.
		'''
		super().__init__()
		self.debug = debug
		# How long entity stays without movement before reseting its direction to SOUTH
		self.stand_delay_ms = stand_delay_ms

	@time_dec
	def process(self, *args, **kwargs):
		''' Process entities having Motion and Transform components. Basically,
		add motion diffs to the position represented by Transform component.
		'''
		
		# Get the time of processing of the frame from the game main loop in seconds 
		dt = kwargs.get('dt') / 1000

		for _ , (transform, motion) in self.world.get_components(components.Transform, components.Motion):
			
			# Motion can be disabled from script or brain
			if motion.enabled:

				# If the position of the entity needs to be updated 
				if (motion.dx !=0 or motion.dy !=0):

					# Save last position - used for collision resolution
					transform.lastx = transform.x
					transform.lasty = transform.y
					transform.lastmap = transform.map
					#transform.lastdir = transform.direction
					motion.last_move = pygame.time.get_ticks()

					# Compensate the speed of the diagonal movement - division by sqrt(2)
					if motion.dx != 0 and motion.dy != 0:
						motion.dx *= 0.7071
						motion.dy *= 0.7071

					# Update the position by the velocity. Compensate by dt
					transform.x += motion.dx * dt
					transform.y += motion.dy * dt

					####
					## Update the direction
					####

					# Update the direction based on motion attributes
					sign = lambda x: -1 if x<0 else (1 if x>0 else 0)
					transform.direction = (sign(motion.dx), sign(motion.dy))

					# If movement is in both axises then use NORD-SOUTH direction
					if motion.dx != 0 and motion.dy != 0:
						transform.direction = (0, transform.direction[1])

					# Return the velocity to 0 - movement has been processed
					motion.dx = 0
					motion.dy = 0
				
				# No update of velocity in this cycle
				else:
					# if the time from the last movement is longer than given duration, change the direction to SOUTH
					if pygame.time.get_ticks() - motion.last_move > self.stand_delay_ms:
						transform.direction = (0,1)


class RenderMapProcessor(esper.Processor):
	''' For rendering maps on camera surfaces. 
	'''

	def __init__(self, window, maps, tile_res=64, debug=False):
		'''
		'''
		super().__init__()
		self.window = window
		self.maps = maps
		self.tile_res = tile_res
		self.debug = debug

	@time_dec
	def process(self, *args, **kwargs):
		''' 
		'''
		
		# Find the entity with Camera and use its position
		# cam_trans - position and map of the object that is in camera's focus
		# cam_cam - camera component itself
		for _ , (cam_trans, cam_cam) in self.world.get_components(components.Transform, components.Camera):

			# Clear the camera surface
			cam_cam.screen.fill((0,0,0))

			# Get map that is on the object in camera's focus
			map = self.maps.get(cam_trans.map)


			for x, y, tile in map.get_tile_images_by_rect('ground', cam_cam.map_screen_rect):
				cam_cam.screen.blit(tile, cam_cam.apply((x * self.tile_res, y * self.tile_res)))

			for x, y, tile in map.get_tile_images_by_rect('wall', cam_cam.map_screen_rect):
				cam_cam.screen.blit(tile, cam_cam.apply((x * self.tile_res, y * self.tile_res)))
			

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


# TODO - optimize
# TODO - use vector2
class RenderWorldProcessor(esper.Processor):
	''' Draws the whole game sceen - camera screens, map and sprites.
	
	Input parameters:
		-	window - reference to main game screen
		-	tile_res - resolution of game tile (default 64x64)
		-	clear_color - backgroun screen color
		-	debug

	Involved components:
		-	Transform
		-	Camera
		-	Renderable
		-	CanTalk
	
	Related processors:
		-	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

	What if this processor is disabled?
		-	nothing will be shown on the game window
	
	Where the processor should be planned?
		-	at the very end of all processors in order to display calculated reality
		-	after UpdateCameraOffsetProcessor - in order to display scrolling
	'''

	def __init__(self, window, debug=False):
		''' Initiation of RenderProcessor processor.
		window ... main drawing surface
		maps ... reference to the dictionary of all maps
		'''
		super().__init__()
		self.window = window
		self.debug = debug

	@time_dec
	def process(self, *args, **kwargs):
		''' Draws screen for every camera. Every screen then is drawn map, objects
		and dialog texts. Check the following video for more details about camera 
		implementation of scrolling https://youtu.be/3zV2ewk-IGU.
		'''
		
		# Find the entity with Camera and use its position
		# cam_trans - position and map of the object that is in camera's focus
		# cam_cam - camera component itself
		for _ , (cam_cam) in self.world.get_component(components.Camera):

			# Blit all the Entities that have Renderable and Transform components
			for _ , (renderable, transform) in self.world.get_components(components.Renderable, components.Transform):
				#cam_cam.screen.blit(renderable.image, self.apply_camera(cam_cam, self.centre_sprite((transform.x, transform.y))))
				cam_cam.screen.blit(renderable.image, cam_cam.apply(renderable.topleft((transform.x, transform.y))))

			# Blit all Texts that are entities saying (CanSpeak + Transform component)
			for _ , (can_talk, renderable, transform) in self.world.get_components(components.CanTalk, components.Renderable, components.Transform):

				# If there is something to say
				if can_talk.text:
					
					# Blit the text bubble on the position offset specified by CanTalk component
					#cam_cam.screen.blit(can_talk.text_surf, self.apply_camera(cam_cam, self.centre_sprite((transform.x - can_talk.text_rect[2], transform.y - can_talk.text_rect[3]))))
					
					if transform.direction == (1,0): # RIGHT
						cam_cam.screen.blit(can_talk.text_surf, 
							cam_cam.apply((transform.x - renderable.d_w - can_talk.text_rect[2], transform.y - can_talk.text_rect[3])))
					
					elif transform.direction == (-1,0): # if direction is (-1, 0) LEFT
						cam_cam.screen.blit(can_talk.text_surf, 
							cam_cam.apply((transform.x + renderable.d_w, transform.y - can_talk.text_rect[3])))

					elif transform.direction == (0,-1): # if direction is (0,-1) UP
						cam_cam.screen.blit(can_talk.text_surf, 
							cam_cam.apply((transform.x - can_talk.text_rect[2] / 2, transform.y + renderable.d_h )))

					else: # if direction is (0,1) DOWN
						cam_cam.screen.blit(can_talk.text_surf, 
							cam_cam.apply((transform.x - can_talk.text_rect[2] / 2, transform.y - renderable.d_h - can_talk.text_rect[3])))


			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

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

class RenderDebugProcessor(esper.Processor):

	def __init__(self, window):

		super().__init__()
		self.window = window
		self.font = pygame.font.Font(None, 14)


	@time_dec
	def process(self, *args, **kwargs):

		# Get information about required debug information
		debug = kwargs.get('debug', {})

		# Show debug information on all cameras
		for _ , (cam_cam) in self.world.get_component(components.Camera):

			# Show debug information only for displayable entities with Debug flag
			for debug_entity , (deb_comp, render_comp, trans_comp) in self.world.get_components(components.Debug, components.Renderable, components.Transform):

				# Print inventory
				if debug.get('show_inventory', False):
					try:
						inventory_debug = self.world.component_for_entity(debug_entity, components.HasInventory)
						text = f'Inventory: {inventory_debug.inventory}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((trans_comp.x, trans_comp.y - 20))))
					except KeyError:
						pass

				# Print labels
				if debug.get('show_labels', False):
					try:
						label_debug = self.world.component_for_entity(debug_entity, components.Labeled)
						text = str(debug_entity) + ', ' + str(label_debug.id) + ', ' + str(label_debug.name)
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((trans_comp.x, trans_comp.y - 10))))
					except KeyError:
						pass

				
				# Print position
				if debug.get('show_position', False):
					try:
						trans_debug = self.world.component_for_entity(debug_entity, components.Transform)
						text = 'Pos: (' + str(int(trans_debug.x)) + ', ' + str(int(trans_debug.y)) + ')'
						pos = deb_comp.font.render(text, True, pygame.Color('white'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((trans_comp.x, trans_comp.y))))
					except KeyError:
						pass

				# Print brain
				if debug.get('show_brain', False):
					try:
						brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
						for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
							color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
							cmd = deb_comp.font.render(str(cmd_idx) + ' -> ' + str(cmd_txt), True, color)
							cam_cam.screen.blit(cmd, cam_cam.apply(render_comp.topleft((trans_comp.x, 10 + trans_comp.y + (cmd_idx * 10)))))
					except KeyError:
						pass

				# Print collision area
				if debug.get('show_collision', False):
					try:
						coll_debug = self.world.component_for_entity(debug_entity, components.Collidable)
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((trans_comp.x - coll_debug.x,trans_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

				# Print direction of entity
				if debug.get('show_direction', False):
					try:
						pygame.draw.line(cam_cam.screen, pygame.Color('red'), 
							cam_cam.apply((trans_comp.x, trans_comp.y)),
							cam_cam.apply((trans_comp.x + trans_comp.direction[0] * 20, trans_comp.y + trans_comp.direction[1] * 20)),
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

	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window


class RenderBackgroundProcessor(esper.Processor):
	def __init__(self, window, clear_color=(0, 0, 0), debug=False):

		super().__init__()
		self.window = window
		self.clear_color = clear_color
		self.debug = debug

	@time_dec
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

	@time_dec
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
	''' Checks for collisions with the titles on the map
	'''

	def __init__(self, maps):
		''' maps is link to global dict of maps
		'''
		super().__init__()

		self.maps = maps
	
	@time_dec
	def process(self, *args, **kwargs):
		
		# Do collision against the map
		for ent_moved, (coll_moved, trans_moved) in self.world.get_components(components.Collidable, components.Transform):
			
			# Get collision map using the global dict of maps
			collision_map = self.maps.get(trans_moved.map).collision_map

			# Get the map position where the entity is situated
			
			# Topleft corner is situated
			if (collision_map[int(trans_moved.y - coll_moved.y) // 64][int(trans_moved.x - coll_moved.x) // 64] != 0 or
				# Topright corner is situated
				collision_map[int(trans_moved.y - coll_moved.y) // 64][int(trans_moved.x + coll_moved.x) // 64] != 0 or
				# Bottomleft corner
				collision_map[int(trans_moved.y + coll_moved.y) // 64][int(trans_moved.x - coll_moved.x) // 64] != 0 or
				# Bottom right corner
				collision_map[int(trans_moved.y + coll_moved.y) // 64][int(trans_moved.x + coll_moved.x) // 64] != 0):

				# Fix position for the entity that has moved
				trans_moved.x = trans_moved.lastx
				trans_moved.y = trans_moved.lasty

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
	''' -	COLLISION SYSTEM
			Checks for collisions and resolves them
			-	COLLISION + MOTION - Only entities that has moved are checked for collision
			-	COLLISION + TRANSFORM - Above entities are checked against Collision and Transform.
	'''

	def __init__(self):
		super().__init__()
		

	@time_dec
	def process(self, *args, **kwargs):
			
		# Get all entities that have Motion and Collidable (only those can activelly hit something) - i.e. that could have moved and iterate those
		for ent_moved, (coll_moved, trans_moved) in self.world.get_components(components.Collidable, components.Transform):
			# Compare that all collision + transform entities - DUMMY WAY
			for ent_other, (coll_other, trans_other) in self.world.get_components(components.Collidable, components.Transform):
				
				# Heuristic no.-1 - Test only those that have Motion component
				#if not self.world.has_component(ent_moved, Motion): continue

				# Heuristic no.0 - Test only those that have moved component
				#if not self.world.component_for_entity(ent_moved, Motion).has_moved: continue

				# Heuristic no.1 - Skip if testing itself
				if ent_moved == ent_other: continue

				# Heuristic no 1.5 - Test only entities on the same map
				if trans_moved.map != trans_other.map: continue

				# Heuristic no.2 - Test only those in close distance
				#if abs(trans_moved.x - trans_other.y) > 200 or abs(trans_moved.y - trans_other.y) > 200: continue 

				# Heuristic no.3 - Do not test twice the same double of entities, i.e. 1,3 and 3,1
				
				# AABB comaprison - Collision
				if(trans_moved.x - coll_moved.x < trans_other.x + coll_other.x and
					trans_moved.x + coll_moved.x > trans_other.x - coll_other.x and
					trans_moved.y - coll_moved.y < trans_other.y + coll_other.y and
					trans_moved.y + coll_moved.y > trans_other.y - coll_other.y):
					
					# Add collision to the collision component 
					coll_other.collision_events.add(ent_moved)
					#coll_moved.collision_events.add(ent_other)

					if ent_other == 8:
						print(f'COLLISION EVENTS for 8 {coll_other.collision_events}')


class CollisionTeleportProcessor(esper.Processor):
	def __init__(self, teleport_event_queue):
		super().__init__()

		self.teleport_event_queue = teleport_event_queue

	@time_dec
	def process(self, *args, **kwargs):
		for ent, (teleport, collision) in self.world.get_components(components.Teleport, components.Collidable):

			# Process everything that collided with teleport
			for col_event_entity in collision.collision_events.copy():
					
					# If entity is Teleportable and has position
					if self.world.has_components(col_event_entity, components.Teleportable, components.Transform, components.Collidable):
						
						# Get the Transform, Collidable and HasInventory component of the teleportee entity
						col_event_entity_trans = self.world.component_for_entity(col_event_entity, components.Transform) 
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
							col_event_entity_trans.x = teleport.dest_x
							col_event_entity_trans.y = teleport.dest_y
							col_event_entity_trans.map = teleport.dest_map 

							# Report that teleportation occured - generate event
							teleport_event = Event('TELEPORTATION', ent, col_event_entity, params={'teleport' : ent, 'teleportee' : col_event_entity})
							self.teleport_event_queue.append(teleport_event)

						# Remove the col_event_entity from Teleport
						collision.collision_events.remove(col_event_entity)

						# Remove the col event related to teleport from the Entity
						col_event_entity_coll.collision_events.remove(ent)


class CollisionItemProcessor(esper.Processor):
	def __init__(self, item_pickup_event_queue):
		super().__init__()
		self.item_pickup_event_queue = item_pickup_event_queue

	@time_dec
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

						# Remove Transform component from the item so that it is not displayable on the map - item is picked
						self.world.remove_component(ent, components.Transform) 

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
						teleport_event = Event('ITEM_PICKUP', ent, col_event_entity, params={'item' : ent, 'picker' : col_event_entity})
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

	@time_dec
	def process(self, *args, **kwargs):
		for ent, (collision, transform) in self.world.get_components(components.Collidable, components.Transform):

			##### New collision process
			# 1. Iterate all collidable entities
			# 2. Iterate all entities with whom there was a collision
			# 3. Generate collision event
			# 4. Calculate the positions so that objects are not collided - do not use last position - this was causing stuck states

			for col_event_entity in collision.collision_events.copy():

				# Report that entity collision occured - generate event
				collision_event = Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
				self.entity_coll_event_queue.append(collision_event)

				# Calculate and update possition
				col_event_entity_trans = self.world.component_for_entity(col_event_entity, components.Transform)
				col_event_entity_collidable = self.world.component_for_entity(col_event_entity, components.Collidable)

				# collision on X axis (distance is lower then coll area)
				if abs(col_event_entity_trans.x - transform.x) < (col_event_entity_collidable.x + collision.x):
					# Call move 
					if transform.x < col_event_entity_trans.x: 
						self.input_command_queue.append(('move', {"entity" : ent, "dx" : -config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dx" : config.MOVE_SPEED}))
					else:
						self.input_command_queue.append(('move', {"entity" : ent, "dx" : config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dx" : -config.MOVE_SPEED}))
					
					# transform.x = transform.lastx
					# col_event_entity_trans.x = col_event_entity_trans.lastx

				# collision on Y axis (distance is lower then coll area)
				if abs(col_event_entity_trans.y - transform.y) <= (col_event_entity_collidable.y + collision.y) + 10:
					# Call move 
					if transform.y < col_event_entity_trans.y: 
						self.input_command_queue.append(('move', {"entity" : ent, "dy" : -config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dy" : config.MOVE_SPEED}))
					else:
						self.input_command_queue.append(('move', {"entity" : ent, "dy" : config.MOVE_SPEED}))
						self.input_command_queue.append(('move', {"entity" : col_event_entity, "dy" : -config.MOVE_SPEED}))
					
					
					# try to use last position for both
					#transform.y = transform.lasty
					#col_event_entity_trans.y = col_event_entity_trans.lasty

				# Remove the col_event_entity from  entity
				collision.collision_events.remove(col_event_entity)


			''' Old process
			# If some collision occured, the collision_event set is not empty
			if collision.collision_events:
				
				# Fix position for the entity that has moved
				transform.x = transform.lastx
				transform.y = transform.lasty

			# Process everything that collided with entity ent
			for col_event_entity in collision.collision_events.copy():

				# Report that entity collision occured - generate event
				collision_event = Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
				self.entity_coll_event_queue.append(collision_event)

				# Fix position for the entity that has moved
				#transform.x = transform.lastx
				#transform.y = transform.lasty

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

class CollisionCorrectorProcessor(esper.Processor):
	def __init__(self):
		super().__init__()

	@time_dec
	def process(self, *args, **kwargs):
		for ent, (collision, transform) in self.world.get_components(components.Collidable, components.Transform):
			
			# If some collision occured, the collision_event set is not empty
			if collision.collision_events:
				
				# Fix position for the entity that has moved
				transform.x = transform.lastx
				transform.y = transform.lasty

				# Clear all collisions
				collision.collision_events.clear()


class BrainProcessor(esper.Processor):

	def __init__(self, input_command_queue):
		super().__init__()
		
		self.input_command_queue = input_command_queue

	@time_dec
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

	@time_dec
	def process(self, *args, **kwargs):
		''' Call external function that processes all events
		'''
		self.game_event_handler()


class CommandProcessor(esper.Processor):

	def __init__(self, game_commands_handler, debug=False):
		super().__init__()

		self.game_commands_handler = game_commands_handler
		self.debug = debug

	@time_dec
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

	@time_dec
	def process(self, *args, **kwargs):
		''' 
		'''
		
		# Find the entity with Camera and use its position
		# cam_trans - position and map of the object that is in camera's focus
		# cam_cam - camera component itself
		for _ , (cam_trans, cam_cam) in self.world.get_components(components.Transform, components.Camera):

			# Clear the camera surface
			cam_cam.screen.fill((0,0,0))

			# Get map that is on the object in camera's focus
			map = self.maps.get(cam_trans.map)

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
