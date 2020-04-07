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

fh = logging.FileHandler('proc_perf.log')
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
		if config.DEBUG: logger.info(f'Method {f} took {(time.time() - start) * 1000} msecs.')
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

	def __init__(self, debug=False):
		''' Initiation of CameraProcessor processor.
		'''
		super().__init__()
		
		self.debug = debug

	@time_dec
	def process(self, *args, **kwargs):
		''' Process entities having Camera and Transform components. Check
		the following video for more details about camera implementation
		https://youtu.be/3zV2ewk-IGU.
		'''

		for _ , (transform, camera) in self.world.get_components(components.Transform, components.Camera):
			
			# Updates camera offset based on position of the Transform (component that the camera follows). 

			# Offset moves opposite direction than the object + we need to keep it in the centre of the screen
			x = -transform.x + int(camera.screen_width / 2)
			y = -transform.y + int(camera.screen_height / 2)
		
			# Correction - do not centre while entity is at the edge of the map
			x = min(0, x)
			y = min(0, y)
			x = max(-(transform.map.width - camera.screen_width), x)
			y = max(-(transform.map.height - camera.screen_height), y)

			# Update the Camera offset
			camera.offset_x, camera.offset_y = x, y

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

	def __init__(self, debug=False):
		''' Initiation of MovementProcessor processor.
		'''
		super().__init__()
		self.debug = debug

	@time_dec
	def process(self, *args, **kwargs):
		''' Process entities having Motion and Transform components. Basically,
		add motion diffs to the position represented by Transform component.
		'''
		
		# Get the time of processing of the frame from the game main loop in seconds 
		dt = kwargs.get('dt') / 1000

		for _ , (transform, motion) in self.world.get_components(components.Transform, components.Motion):
			
			# Save last position - used for collision resolution
			transform.lastx = transform.x
			transform.lasty = transform.y

			# Compensate the speed of the diagonal movement - division by sqrt(2)
			if motion.dx != 0 and motion.dy != 0:
				motion.dx *= 0.7071
				motion.dy *= 0.7071

			# Update the position by the velocity. Compensate by dt
			transform.x += motion.dx * dt
			transform.y += motion.dy * dt

			# Return the velocity to 0
			motion.dx = 0
			motion.dy = 0

# TODO - optimize
# TODO - use vector2
class RenderProcessor(esper.Processor):
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

	def __init__(self, window, tile_res=64, clear_color=(0, 0, 0), debug=False):
		''' Initiation of RenderProcessor processor.
		'''
		super().__init__()
		self.window = window
		self.clear_color = clear_color
		self.tile_res = tile_res
		self.debug = debug

	def apply_camera(self, camera: components.Camera, pos=(0,0)):
		''' Applying camera offset to some position. Returns new position
		of the object and hence enables scrolling effect.
		'''
		# Move the sprite of the entity - returns new shifted coordinates
		return (pos[0] + camera.offset_x, pos[1] + camera.offset_y)

	def centre_sprite(self, pos):
		''' Centre the sprite so it is centered on the map position
		'''
		return (pos[0] - self.tile_res / 2, pos[1] - self.tile_res / 2)

	@time_dec
	def process(self, *args, **kwargs):
		''' Draws screen for every camera. Every screen then is drawn map, objects
		and dialog texts. Check the following video for more details about camera 
		implementation of scrolling https://youtu.be/3zV2ewk-IGU.
		'''
		
		# Clear the main game window surface
		self.window.fill(self.clear_color)

		# Find the entity with Camera and use its position
		# cam_trans - position and map of the object that is in camera's focus
		# cam_cam - camera component itself
		for _ , (cam_trans, cam_cam) in self.world.get_components(components.Transform, components.Camera):

			# Clear the camera surface
			cam_cam.screen.fill((0,0,0))

			# Get map that is on the object in camera's focus
			map = cam_trans.map

			# Blit the map ground layer			
			for i in range(len(map.ground_layer)): # Y axis	
				for j in range(len(map.ground_layer[0])): # X axis
					if map.ground_layer[i][j] != 0:
						cam_cam.screen.blit(map.get_tile('ground', j, i), self.apply_camera(cam_cam, (j * self.tile_res, i * self.tile_res)))

			# Blit the map wall layer
			for i in range(len(map.wall_layer)): # Y axis	
				for j in range(len(map.wall_layer[0])): # X axis
					if map.wall_layer[i][j] != 0:
						cam_cam.screen.blit(map.get_tile('wall', j, i), self.apply_camera(cam_cam, (j * self.tile_res, i * self.tile_res)))

			# Blit all the Entities that have Renderable and Transform components
			for _ , (renderable, transform) in self.world.get_components(components.Renderable, components.Transform):
				cam_cam.screen.blit(renderable.image, self.apply_camera(cam_cam, self.centre_sprite((transform.x, transform.y))))

			# Blit all Texts that are entities saying (CanSpeak + Transform component)
			for _ , (can_talk, transform) in self.world.get_components(components.CanTalk, components.Transform):

				# If there is something to say
				if can_talk.text:
					
					# Blit the text bubble on the position offset specified by CanTalk component
					cam_cam.screen.blit(can_talk.text_surf, self.apply_camera(cam_cam, self.centre_sprite((transform.x - can_talk.text_rect[2], transform.y - can_talk.text_rect[3]))))
		
			if self.debug:
				# Blit debug information
				for debug_entity , (deb_comp, trans_comp) in self.world.get_components(components.Debug,components.Transform):

					# Print possition
					try:
						trans_debug = self.world.component_for_entity(debug_entity, components.Transform)
						text = 'Pos: (' + str(int(trans_debug.x)) + ', ' + str(int(trans_debug.y)) + ')'
						pos = deb_comp.font.render(text, True, pygame.Color('white'))
						cam_cam.screen.blit(pos, self.apply_camera(cam_cam, self.centre_sprite((trans_comp.x, trans_comp.y))))
					except KeyError:
						pass

					# Print brain
					try:
						brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
						for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
							color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
							cmd = deb_comp.font.render(str(cmd_idx) + ' -> ' + str(cmd_txt), True, color)
							cam_cam.screen.blit(cmd, self.apply_camera(cam_cam, self.centre_sprite((trans_comp.x, 10 + trans_comp.y + (cmd_idx * 10)))))
					except KeyError:
						pass

					# Print collision area
					try:
						coll_debug = self.world.component_for_entity(debug_entity, components.Collidable)
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(self.apply_camera(cam_cam, (trans_comp.x - coll_debug.x,trans_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

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

#continue here
class CollisionMapProcessor(esper.Processor):
	''' Checks for collisions with the titles on the map
	'''

	def __init(self):
		super().__init__()
	
	@time_dec
	def process(self, *args, **kwargs):
		
		# Do collision against the map
		for ent_moved, (coll_moved, trans_moved) in self.world.get_components(components.Collidable, components.Transform):
			
			# Get collision map
			collision_map = trans_moved.map.collision_map

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

						# Remove the col_event_entity from Item entity
						collision.collision_events.remove(col_event_entity)

						# Remove the col event related to item from the Entity
						col_event_entity_coll.collision_events.remove(ent)

						# Report that item was picked up - generate event
						teleport_event = Event('ITEM_PICKUP', ent, col_event_entity, params={'item' : ent, 'picker' : col_event_entity})
						self.item_pickup_event_queue.append(teleport_event)


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

				# Put the command into the queue for processing
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

