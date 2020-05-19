import core.config.config as config

import core.ecs.esper as esper
import core.ecs.components as components
import core.ecs.processors as processors

import core.commands.commands as commands

import core.maps.map as map
import core.quests.quest as quest

import pygame
import math
import json
import pickle # for savegame

global world
global _maps
global _quests
global window
global c_event_queue
global command_queue
global _entity_map


########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()

########################################################
### Game commands handler
########################################################

def process_game_commands(debug=False):
	''' Process game commands. It is called by CommandsProcessor.
	Processes the command_queue.
	'''
	global command_queue
	global _entity_map

	if debug and command_queue: print(f'*Command Queue: {command_queue}')


	# Process every command in the queue
	while command_queue:

		# pop out command from the beginning of the queue
		command = command_queue.pop(0)

		if debug: print(f'*Processing command: {command}')
		
		(cmd_fnc, cmd_params) = command
		
		# Check if in cmd_params there is entity parameter that is not an integer but a string.
		# Such commands can be submitted by the global script processor Brain
		entity_id = cmd_params.get('entity')
		if isinstance(entity_id, str): cmd_params.update({'entity' : _entity_map.get(entity_id)})

		brain = cmd_params.get("brain", None)

		# Execute the command - command is a text hence need to get reference to command func. first
		# result = cmd_fnc(**cmd_params) # originally, this was called when command fnc was reference to the fnc
		# If command is not recognized by the command module, none command function is returned
		
		result = commands.get_cmd_fnc(cmd_fnc)(**cmd_params)
		
		# Notify brain about the result of the cmd unit currently on current_cmd_idx
		#print(f'\n*process_game_commands: {cmd_fnc} PRE calling process_result({result})')

		if brain: brain.process_result(result)

		#print(f'*process_game_commands: POST calling process_result: {command_queue}')

########################################################
### Game event handler
########################################################

def process_game_events():
	''' Process game/quest events. It is called by GameEventProcessor
	'''
	global _quests

	# Process every waiting event
	'''
	for event in c_event_queue:

		# Send every event to every quest for handling
		for quest in _quests:

			# Call event handler
			quest.event_handler(event)

		# Remove the event from the queue
		c_event_queue.remove(event)
	'''
	while c_event_queue:

		# out event from the beginning of the queue
		event = c_event_queue.pop(0)

		# Send every event to every quest for handling
		for quest_name, quest_object in _quests.items():

			# Call event handler
			quest_object.event_handler(event)

########################################################
### Game world creator
########################################################

def _create_entity(json_ent_obj, register=True, child_ref=None):
	''' Create entity from json definition. See Quest for definitions
	'''

	global world
	global _entity_map

	# Prepare new_entity obj
	new_entity_obj = None
	
	# Decode entity id 
	new_entity_id = json_ent_obj.get("id")

	# Create new entity obj for the root elntity
	if not child_ref: new_entity_obj = world.create_entity()

	# Read the components from the templates - order matters! latter has priority and overwrites the previous components
	for template in json_ent_obj.get("templates", []):

		# Read the entity.json		
		try:		
			with open(config.ENTITY_PATH + template + '.json', 'r') as entity_file:
				json_entity_data = entity_file.read()
				template_entity_data = json.loads(json_entity_data)
		except FileNotFoundError:
			print(f"Entity file {config.ENTITY_PATH + template + '.json'} not found.")
			raise

		print(f'Trying to create entity from {template + ".json"}')
		_create_entity(template_entity_data, child_ref=new_entity_obj if not child_ref else child_ref)

	# Initiate every component
	for component in json_ent_obj.get("components"):
		
		# Get component type
		comp_type = component.get("type")

		# Get component params
		comp_params = component.get("params", {})

		# Create component - volat s odkazem na root entity obj
		try:
			result = components.create_component(world, new_entity_obj if not child_ref else child_ref, comp_type, comp_params)
			print(f'Entity: {new_entity_obj if not child_ref else child_ref}, child ref: {child_ref}, Comp type: {comp_type}')
		except ValueError:
			print(f'Error in creation of component {comp_type} with parameters {comp_params}')
			raise ValueError


	# Add entity to the entity map - for the root entity
	if not child_ref and register: 
		_entity_map.update({new_entity_id : new_entity_obj})
	
	return new_entity_obj

def create_processors(world):
	
	global window
	global c_event_queue
	global command_queue
	global _maps

	# Processor that generates projectiles
	generate_projectiles_processor = processors.GenerateProjectileProcessor()

	# Processor that deletes entities with Temporary component from the world - once ttl expires
	clear_temporary_entity_processor = processors.ClearTemporaryEntityProcessor()
	
	# Status procesor updates status of the entity - idle, walk, ...
	render_model_anim_action_processor = processors.RenderableModelAnimationActionProcessor()

	# Movement processor updates entity position based on the velocity 
	movement_processor = processors.MovementProcessor()

	# Render background procesor to display game stats and anything else
	render_background_processor = processors.RenderBackgroundProcessor(window=window)

	# Render processor to display map
	render_map_processor = processors.RenderMapProcessor(window=window, maps=_maps)

	# Render processor to place renderable entities with position on the screen
	render_world_processor = processors.RenderWorldProcessor(window=window)
	render_model_world_processor = processors.RenderModelWorldProcessor(window=window)


	# Render debug processor to display debug information for renderable entities
	render_debug_processor = processors.RenderDebugProcessor(window=window)

	# Input processor to process keys pressed - the commands are queued and processed later by CommandProcessor
	input_processor = processors.InputProcessor(command_queue)

	# Collision Entity processor
	collision_entity_generator_processor = processors.CollisionEntityGeneratorProcessor()

	# Collision Map processor
	collision_map_processor = processors.CollisionMapProcessor(maps=_maps)

	# Teleport Collision processor
	collision_teleport_processor = processors.CollisionTeleportProcessor(c_event_queue)

	# Damaging Collision processor
	collision_damage_processor = processors.CollisionDamageProcessor(c_event_queue)

	# Weapon Collision processor
	collision_weapon_processor = processors.CollisionWeaponProcessor(c_event_queue)

	# Wearable Collision processor
	collision_wearable_processor = processors.CollisionWearableProcessor(c_event_queue)

	# Item Collision processor
	collision_item_processor = processors.CollisionItemProcessor(c_event_queue)

	# Entity Collision processor - added command queue processor to generate corrective movements
	collision_entity_processor = processors.CollisionEntityProcessor(c_event_queue,command_queue)

	# Collision position corrector processor - OBSOLETE - substituted by CollisionEntityProcessor
	#collision_corrector_processor = processors.CollisionCorrectorProcessor()

	# Camera processor - update position of the camera
	update_camera_offset_processor = processors.UpdateCameraOffsetProcessor(maps=_maps)

	# Game events processor - triggers actions based on previously generated events
	game_events_processor = processors.GameEventsProcessor(process_game_events)

	# Command processor - processes all commands from the command queue
	command_processor = processors.CommandProcessor(process_game_commands)

	# Brain processor
	brain_processor = processors.BrainProcessor(command_queue)
	
	##### #### #### ####
	# Beware of order of the processors
	##### #### #### ####

	### First lets read input from player or/and AI. The resulting commands are stored in cmd_stream
	world.add_processor(input_processor)
	world.add_processor(brain_processor)

	### Process all the commands from the command stream
	world.add_processor(command_processor)

	### Move the entities based on their movement vector 
	world.add_processor(movement_processor)

	### Generate projectiles GenerateProjectileProcessor
	world.add_processor(generate_projectiles_processor)
	
	### Process all collisions and produce events where necessary
	world.add_processor(collision_map_processor)	# Resolves all the collisions on the map - correct movements and nothing more
	world.add_processor(collision_entity_generator_processor)	# Fills information about which entities collided together into the Collision components
	world.add_processor(collision_damage_processor) # Makes damage to entity if applicable
	world.add_processor(collision_teleport_processor)	# Resolves teleport collisions + generates events to the main program where those can be further processed
	world.add_processor(collision_weapon_processor)	# Resolves weapon pickups collisions + generates events to the main program where those can be further processed	
	world.add_processor(collision_wearable_processor)	# Resolves wearable pickups collisions + generates events to the main program where those can be further processed	
	world.add_processor(collision_item_processor)		# Resolves item pickups collisions + generates events to the main program where those can be further processed
	world.add_processor(collision_entity_processor)		# Resolves entity collisions + generates events to the main program where those can be further processed
	#world.add_processor(collision_corrector_processor)	# Fixes positions of collided entities - OBSOLETE - substituted by CollisionEntityProcessor

	### Process all events that were generated by collision processors	
	world.add_processor(game_events_processor)	# Based on events generated by the collisions (teleportation, item pickups) now is the time to see if there are some game actions that we want to do - e.g. cinematics

	
	##################################
	### Render the world on the screen
	##################################
	# Update all cameras
	world.add_processor(update_camera_offset_processor)

	### Change the entity state basedon everything what has happened before rendering
	world.add_processor(render_model_anim_action_processor)

	# Render background - stats / inventory / picture
	world.add_processor(render_background_processor)

	# Render maps
	world.add_processor(render_map_processor)

	# Render objects with Renderable component
	world.add_processor(render_world_processor)
	
	# Render world entities
	#world.add_processor(render_world_processor)
	world.add_processor(render_model_world_processor)

	# Render additional debug information on the screen
	world.add_processor(render_debug_processor)

	##################################
	### Clearing processors
	##################################

	# Delete entities with Temporary component from the world
	world.add_processor(clear_temporary_entity_processor)


########################################################
### Save and load game
########################################################

def load_game():
	''' Load game state 
	'''

	with open(config.SAVE_PATH + 'save.dat','rb') as f: game_state = pickle.load(f)

	# Restore command queue
	global command_queue
	command_queue = game_state.get('command_queue')

	# Restore event queue
	global c_event_queue
	c_event_queue = game_state.get('event_queue')

	# Restore maps
	global _maps
	_maps = {}

	for map_name in game_state.get('maps'):
		sample_map = map.Map(map_name)	
		_maps.update({ map_name : sample_map})

	# Restore entity mapping
	global _entity_map
	_entity_map = game_state.get('entity_map')

	# Restore quests
	global _quests
	_quests = game_state.get('quests')

	##### Restore world
	global world
	world = game_state.get('world')

	# Restore references to non-serializable objects on entities
	for entity_id in world._entities.keys():
		# Go through every component of the entity
		for component in world.components_for_entity(entity_id):
			# Execute pre-save steps on the component			
			component.post_load()
			print(f'LOAD: Finished post-load steps for entity {entity_id} and component {component}')

	# Restore processor references
	global window

	world.get_processor(processors.CollisionMapProcessor).post_load(_maps)
	print(world.get_processor(processors.CollisionMapProcessor))

	world.get_processor(processors.UpdateCameraOffsetProcessor).post_load(_maps)
	print(world.get_processor(processors.UpdateCameraOffsetProcessor))

	world.get_processor(processors.RenderBackgroundProcessor).post_load(window) 
	print(world.get_processor(processors.RenderBackgroundProcessor))

	world.get_processor(processors.RenderMapProcessor).post_load(window, _maps) 
	print(world.get_processor(processors.RenderMapProcessor))

	world.get_processor(processors.RenderWorldProcessor).post_load(window) 
	print(world.get_processor(processors.RenderWorldProcessor))
	
	world.get_processor(processors.RenderDebugProcessor).post_load(window) 
	print(world.get_processor(processors.RenderDebugProcessor))	
	
	return 0

def save_game():
	''' Before saving, all pygame.Surface must be removed
	and on load again refreshed.
	'''
	
	global window
	global command_queue
	global c_event_queue
	global _maps
	global _entity_map
	global world
	global _quests

	game_state = {}

	# Prepare command queue for save
	game_state.update({'command_queue' : command_queue})

	# Prepare event queue for save
	game_state.update({'event_queue' : c_event_queue})

	# Preapare maps for save - we will only save list of names
	# and reload maps from scratch during load game
	game_state.update({'maps' : [map_name for map_name in _maps.keys()]})
	
	# Prepare entity name -> entity id mapping for save
	game_state.update({'entity_map' : _entity_map})

	# Prepare quests for save
	game_state.update({'quests' : _quests})
	
	# Prepare game world for save - first it is needed
	# to remove all pygame.Surface references from components
	
	##### Go through every entity - in the world
	for entity_id in world._entities.keys():
		# Go through every component of the entity
		for component in world.components_for_entity(entity_id):
			# Execute pre-save steps on the component
			print(f'SAVE: Running pre-save steps for entity {entity_id} and component {component}')
			component.pre_save()


	##### Go through every processor that has problematic entity - remove and create all processors? Will it help?
	# Problematic - processor is referencing the WOrld so I need to clean processors first
	# processors.InputProcessor - OK
	# processors.BrainProcessor - OK
	# processors.CommandProcessor - OK
	# processors.MovementProcessor - OK
	# processors.CollisionMapProcessor - FAILED (self.maps) - TODO - would it be possible to pass maps to all processors during main loop rather than in constructor?
	world.get_processor(processors.CollisionMapProcessor).pre_save()
	# processors.CollisionEntityGeneratorProcessor - OK
	# processors.CollisionTeleportProcessor - OK
	# processors.CollisionItemProcessor - OK
	# processors.CollisionEntityProcessor - OK
	# processors.GameEventsProcessor - OK
	# processors.UpdateCameraOffsetProcessor - FAILED (self.maps) - TODO - would it be possible to pass maps to all processors during main loop rather than in constructor?
	world.get_processor(processors.UpdateCameraOffsetProcessor).pre_save()
	# processors.RenderBackgroundProcessor - FAILED (self.window) - TODO - would it be possible to pass maps to all processors during main loop rather than in constructor?
	world.get_processor(processors.RenderBackgroundProcessor).pre_save() 
	# processors.RenderMapProcessor - FAILED (self.window, self.maps)
	world.get_processor(processors.RenderMapProcessor).pre_save() 
	# processors.RenderWorldProcessor - FAILED (self.window) - TODO - would it be possible to pass maps to all processors during main loop rather than in constructor?
	world.get_processor(processors.RenderWorldProcessor).pre_save() 
	# processors.RenderDebugProcessor - FAILED (self.window) - TODO - would it be possible to pass maps to all processors during main loop rather than in constructor?
	world.get_processor(processors.RenderDebugProcessor).pre_save() 

	# Save the world
	game_state.update({'world' : world})
	
	with open(config.SAVE_PATH + 'save.dat', 'wb') as f: pickle.dump(game_state, f)

	### Restore the non-serializable objects so that game can continue
	for entity_id in world._entities.keys():
		# Go through every component of the entity
		for component in world.components_for_entity(entity_id):
			# Execute pre-save steps on the component			
			component.post_load()
			print(f'SAVE: Finished post-load steps for entity {entity_id} and component {component}')

	### Restore processor references
	world.get_processor(processors.CollisionMapProcessor).post_load(_maps)
	print(world.get_processor(processors.CollisionMapProcessor))

	world.get_processor(processors.UpdateCameraOffsetProcessor).post_load(_maps)
	print(world.get_processor(processors.UpdateCameraOffsetProcessor))

	world.get_processor(processors.RenderBackgroundProcessor).post_load(window) 
	print(world.get_processor(processors.RenderBackgroundProcessor))

	world.get_processor(processors.RenderMapProcessor).post_load(window, _maps) 
	print(world.get_processor(processors.RenderMapProcessor))

	world.get_processor(processors.RenderWorldProcessor).post_load(window) 
	print(world.get_processor(processors.RenderWorldProcessor))
	
	world.get_processor(processors.RenderDebugProcessor).post_load(window) 
	print(world.get_processor(processors.RenderDebugProcessor))

	return 0

########################################################
### Main program
########################################################

def main():
	# Initialize Pygame stuff - at the beginning due to convert() function
	global window

	pygame.init()
	window = pygame.display.set_mode((850,850), 0, 32)
	clock = pygame.time.Clock()

	# All commands are queued here
	global command_queue
	command_queue = []

	# All events are queued here
	global c_event_queue
	c_event_queue = []


	# All maps are here
	global _maps

	sample_map = map.Map('test_map')	
	_maps = {}
	_maps.update({'test_map' : sample_map})

	global _entity_map

	_entity_map = {}


	#####
	# Initialize Esper world with entites and processors
	#####
	global world

	world = esper.World()
	create_processors(world)

	# All quests are here
	global _quests
	_quests = {}

	sample_quest = quest.load_quest('test_quest')
	_quests.update({'test_quest' : sample_quest})

	# Print entity mappings
	print(_entity_map)

	#####
	# The main loop
	#####
	running = True
	while running:

		# Keep game at constant FPS
		dt = clock.tick(config.FPS)

		# Read the keys pressed, mouse, win resize etc.
		key_events = pygame.event.get()
		key_pressed = pygame.key.get_pressed()

		# Check for End Game
		for event in key_events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				if event.key == pygame.K_F1:
					print(f'Saving game ...')
					save_game()
					print(f'Game saved.')
				if event.key == pygame.K_F2:
					print(f'Loading game ...')
					load_game()
					print(f'Game loaded.')
					
		# Update all the processors, pass key events as a parameter
		# and dt (how long the previous frame was processed)
		# Parameter will be passed to all processors. Those who want it
		# will process it.
		world.process(events=key_events, keys=key_pressed, dt=dt, debug=config.DEBUG)

		# Flip the framebuffers
		#pygame.display.update()
		pygame.display.flip()

		# Display FPS in window title
		pygame.display.set_caption('FPS: ' + str(int(clock.get_fps())))

	pygame.quit()
