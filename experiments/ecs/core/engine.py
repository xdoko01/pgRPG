import core.config.config as config

import core.ecs.esper as esper
import core.ecs.components as components
import core.ecs.processors as processors

import core.commands.commands as commands

import core.maps.map as map
import core.quests.quest as quest

import pygame
import math


global world
global _maps
global _quests
global window
global c_event_queue
global command_queue

########################################################
### Game commands handler
########################################################

def process_game_commands(debug=False):
	''' Process game commands. It is called by CommandsProcessor.
	Processes the command_queue.
	'''
	global command_queue

	if debug and command_queue: print(f'*Command Queue: {command_queue}')

	# Process every command in the queue
	while command_queue:

		# pop out command from the beginning of the queue
		command = command_queue.pop(0)

		if debug: print(f'*Processing command: {command}')
		
		(cmd_fnc, cmd_params) = command
		
		brain = cmd_params.get("brain", None)

		# Execute the command
		result = cmd_fnc(**cmd_params)

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

def create_entities(world):
	#####
	# Initiate entities with components
	#####
	global _maps

	# Create player entity that can move
	player = world.create_entity(components.Labeled(id='player01', name='First Player'))
	#world.add_component(player, Labeled(id='player01', name='First Player'))
	world.add_component(player, components.Transform(x=200, y=200, map=_maps.get('map01', None)))	# Player has position in the world
	world.add_component(player, components.Motion(dx=0, dy=0))	# Player can move, hence can have velocity that will change based on key inputs
	world.add_component(player, components.Controllable(control_keys={}, control_cmds={"up": commands.cmd_move,"down": commands.cmd_move,"left": commands.cmd_move,"right": commands.cmd_move}))	# Player can be managed by pressing keys
	world.add_component(player, components.Renderable(image=pygame.image.load(config.IMAGE_PATH + "player.png"))) # Player has sprite
	world.add_component(player, components.Teleportable())
	world.add_component(player, components.Collidable(32,32))
	world.add_component(player, components.Camera(screen_pos_x=0, screen_pos_y=0, screen_width=300, screen_height=300))
	world.add_component(player, components.HasInventory())
	world.add_component(player, components.Brain(commands=[]))
	world.add_component(player, components.CanTalk())
	world.add_component(player, components.Debug())


	# Create static entity being observed by the camera - it is also a key for the teleport
	item = world.create_entity()
	world.add_component(item, components.Labeled(id='item01', name='Static Item'))
	world.add_component(item, components.Transform(x=300, y=300, map=_maps.get('map01', None)))	# Player has position in the world
	world.add_component(item, components.Motion(dx=0, dy=0))	# Player can move, hence can have velocity that will change based on key inputs
	#world.add_component(item, components.Controllable(control_keys={}))	# Player can be managed by pressing keys
	world.add_component(item, components.Renderable(image=pygame.image.load(config.IMAGE_PATH + "item.png"))) # Player has sprite
	world.add_component(item, components.Collidable(32,32))
	world.add_component(item, components.Camera(screen_pos_x=0, screen_pos_y=310, screen_width=300, screen_height=300))
	world.add_component(item, components.Pickable())

	# Create moving camera without any followed object 	engine.world.remove_component(event.generator_obj, components.Collidable)		
	camera = world.create_entity()
	world.add_component(camera, components.Labeled(id='camera01', name='Dynamic Camera'))
	world.add_component(camera, components.Transform(x=400, y=300, map=_maps.get('map01', None)))	# Player has position in the world
	world.add_component(camera, components.Motion(dx=0, dy=0))	# Player can move, hence can have velocity that will change based on key inputs
	world.add_component(camera, components.Controllable(control_keys={'up': pygame.K_w, 'down':pygame.K_s, 'left':pygame.K_a, 'right':pygame.K_d}, control_cmds={"up": commands.cmd_none,"down": commands.cmd_move,"left": commands.cmd_move,"right": commands.cmd_move}))	# Player can be managed by pressing keys
	#world.add_component(camera, components.Renderable(image=pygame.image.load(config.IMAGE_PATH + "bluesquare.png"))) # Player has sprite
	#world.add_component(camera, components.Collidable(32,32))
	world.add_component(camera, components.Camera(screen_pos_x=310, screen_pos_y=0, screen_width=300, screen_height=300))
	world.add_component(camera, components.CanTalk())
	world.add_component(camera, components.Debug())

	world.add_component(camera, 
		components.Brain(
			commands=[
				# IF-EXCEPTION-GOTO, CMD-FNC, CMD-PARAM
				### Move Left
				(None, 	commands.cmd_move, {"dx" : -config.MOVE_SPEED}), #0
				(0, 	commands.cmd_loop, {"iterations" : 1}), #1
				### Move Up
				(None, 	commands.cmd_move, {"dy" : -config.MOVE_SPEED}), #2
				(2, 	commands.cmd_loop, {"iterations" : 1}), #3
				### Move Right
				(None, 	commands.cmd_move, {"dx" : config.MOVE_SPEED}), #4
				(4, 	commands.cmd_loop, {"iterations" : 1}), #5
				###	Move Down
				(None, 	commands.cmd_move, {"dy" : config.MOVE_SPEED}), #6
				(6, 	commands.cmd_loop, {"iterations" : 1}), #7
				### Show Text
				(8, 	commands.cmd_show_dialog, {"time" : 1000, "text" : 'Hello world!'}), #8
				### Wait for space pressed
				(9, 	commands.cmd_wait_key, {"key" : 276}), #9
				(0, 	commands.cmd_goto, {}) #10
			]
		)
	)

	# Create GlobalScript entity		
	script = world.create_entity()
	world.add_component(script, components.Labeled(id='script_engine', name='Global Script Engine'))
	world.add_component(script, 
		components.Brain(
			commands=[
				# IF-EXCEPTION-GOTO, CMD-FNC, CMD-PARAM
				(None, commands.cmd_move, {"entity" : 3, "dx" : -config.MOVE_SPEED}), #0
				(0, commands.cmd_loop, {"iterations" : 100}), #1
				(None, commands.cmd_move, {"entity": 3, "dy" : -config.MOVE_SPEED}), #2
				(2, commands.cmd_loop, {"iterations" : 20}), #3
				(None, commands.cmd_toggle_brain, {"entity" : 3, "enable" : False}), #4
				(0, commands.cmd_goto, {})  #5
			]
		)
	)

	# Create static teleport
	teleport = world.create_entity()
	world.add_component(teleport, components.Labeled(id='tele01', name='Static Teleport'))	
	world.add_component(teleport, components.Transform(x=400, y=400, map=_maps.get('map01', None)))	# Player has position in the world
	world.add_component(teleport, components.Motion(dx=0, dy=0))	# Player can move, hence can have velocity that will change based on key inputs
	#world.add_component(teleport, components.Controllable(control_keys={'up': pygame.K_w, 'down':pygame.K_s, 'left':pygame.K_a, 'right':pygame.K_d}))	# Player can be managed by pressing keys
	world.add_component(teleport, components.Renderable(image=pygame.image.load(config.IMAGE_PATH + "teleport.png"))) # Player has sprite
	world.add_component(teleport, components.Collidable(32,32))
	world.add_component(teleport, components.Camera(screen_pos_x=310, screen_pos_y=310, screen_width=300, screen_height=300))
	world.add_component(teleport, components.Teleport(dest_map=_maps.get('map01', None), dest_x=764, dest_y=164, key=item))

	# Create key to the cellar
	key = world.create_entity(components.Labeled(id='key01', name='Key to the cellar'))
	#world.add_component(key, components.Transform(x=800, y=200, map=_maps.get('map01', None)))
	world.add_component(key, components.Renderable(image=pygame.image.load(config.IMAGE_PATH + "key.png")))
	world.add_component(key, components.Collidable(20,20))
	world.add_component(key, components.Pickable())

	# Create NPC
	npc = world.create_entity(components.Labeled(id='npc01', name='Merchant'))
	world.add_component(npc, components.Transform(x=800, y=200, map=_maps.get('map01', None)))
	world.add_component(npc, components.Motion(dx=0, dy=0))	
	world.add_component(npc, components.Renderable(image=pygame.image.load(config.IMAGE_PATH + "npc.png")))
	world.add_component(npc, components.Collidable(40,40))
	world.add_component(npc, components.HasInventory(inventory=[key]))
	world.add_component(npc, components.CanTalk())
	world.add_component(npc, components.Debug())
	world.add_component(npc, 
		components.Brain(
			commands=[
				# IF-EXCEPTION-GOTO, CMD-FNC, CMD-PARAM
				### Move Left
				(None, 	commands.cmd_move, {"dx" : -config.MOVE_SPEED}), #0
				(0, 	commands.cmd_loop, {"iterations" : 30}), #1
				### Wait and show text
				(2, 	commands.cmd_show_dialog, {"time" : 3000, "text" : '... who will help me ...?'}), #2
				### Move Right
				(None, 	commands.cmd_move, {"dx" : config.MOVE_SPEED}), #3
				(3, 	commands.cmd_loop, {"iterations" : 30}), #4
				### Wait and show text
				(5, 	commands.cmd_show_dialog, {"time" : 3000, "text" : '... Somebody please help me !!'}), #5
				(0, 	commands.cmd_goto, {}) #10
			]
		)
	)

	# Print entity mappings
	print({
		'player' : player,
		'item' : item,
		'teleport' : teleport,
		'camera' : camera,
		'key' : key,
		'npc' : npc,
		'script' : script
	})


def create_processors(world):
	
	global window
	global c_event_queue
	global command_queue

	# Movement processor updates entity position based on the velocity 
	movement_processor = processors.MovementProcessor()

	# Render processor to place renderable entities with position on the screen
	render_processor = processors.RenderProcessor(window=window, debug=True)

	# Input processor to process keys pressed - the commands are queued and processed later by CommandProcessor
	input_processor = processors.InputProcessor(command_queue)

	# Collision Entity processor
	collision_entity_generator_processor = processors.CollisionEntityGeneratorProcessor()

	# Collision Map processor
	collision_map_processor = processors.CollisionMapProcessor()

	# Teleport Collision processor
	collision_teleport_processor = processors.CollisionTeleportProcessor(c_event_queue)

	# Item Collision processor
	collision_item_processor = processors.CollisionItemProcessor(c_event_queue)

	# Entity Collision processor
	collision_entity_processor = processors.CollisionEntityProcessor(c_event_queue)

	# Collision position corrector processor - OBSOLETE - substituted by CollisionEntityProcessor
	#collision_corrector_processor = processors.CollisionCorrectorProcessor()

	# Camera processor - update position of the camera
	update_camera_offset_processor = processors.UpdateCameraOffsetProcessor()

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
	
	### Process all collisions and produce events where necessary
	world.add_processor(collision_map_processor)	# Resolves all the collisions on the map - correct movements and nothing more
	world.add_processor(collision_entity_generator_processor)	# Fills information about which entities collided together into the Collision components
	world.add_processor(collision_teleport_processor)	# Resolves teleport collisions + generates events to the main program where those can be further processed
	world.add_processor(collision_item_processor)		# Resolves item pickups collisions + generates events to the main program where those can be further processed
	world.add_processor(collision_entity_processor)		# Resolves entity collisions + generates events to the main program where those can be further processed
	#world.add_processor(collision_corrector_processor)	# Fixes positions of collided entities - OBSOLETE - substituted by CollisionEntityProcessor

	### Process all events that were generated by collision processors	
	world.add_processor(game_events_processor)	# Based on events generated by the collisions (teleportation, item pickups) now is the time to see if there are some game actions that we want to do - e.g. cinematics
	
	### Render the world on the screen
	world.add_processor(update_camera_offset_processor)
	world.add_processor(render_processor)

########################################################
### Main program
########################################################

def main():
	# Initialize Pygame stuff - at the beginning due to convert() function
	global window

	pygame.init()
	window = pygame.display.set_mode((850,850))
	clock = pygame.time.Clock()

	# All commands are queued here
	global command_queue
	command_queue = []

	# All events are queued here
	global c_event_queue
	c_event_queue = []

	# All quests are here
	global _quests

	_quests = {}

	sample_quest = quest.Quest()
	_quests.update({'test_quest' : sample_quest})

	# All maps are here
	global _maps

	sample_map = map.Map()	
	_maps = {}
	_maps.update({'map01' : sample_map})

	
	#####
	# Initialize Esper world with entites and processors
	#####
	global world

	world = esper.World()
	create_entities(world)
	create_processors(world)

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

		# Update all the processors, pass key events as a parameter
		# and dt (how long the previous frame was processed)
		# Parameter will be passed to all processors. Those who want it
		# will process it.
		world.process(events=key_events, keys=key_pressed, dt=dt)

		# Flip the framebuffers
		pygame.display.update()

		# Display FPS in window title
		pygame.display.set_caption('FPS: ' + str(int(clock.get_fps())))

	pygame.quit()

	print(f'Event queue content: {c_event_queue}')