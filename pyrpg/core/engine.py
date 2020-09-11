''' core.engine module
'''
########################################################
########################################################
###             MODULE IMPORT INIT
########################################################
########################################################

########################################################
### Module Import Init - Import libs
########################################################

import math
import json
import pickle # for savegame/loadgame

########################################################
### Module Import Init - Init pygame
########################################################

import pygame

global window
global clock

pygame.init()

from pyrpg.core.config.config import DISPLAY

window = pygame.display.set_mode(
                DISPLAY['resolution'],
                pygame.FULLSCREEN if DISPLAY['fullscreen'] else 0,
                DISPLAY['bitdepth']
            )

clock = pygame.time.Clock()

########################################################
### Module Import Init - Import game packages and modules
########################################################

import pyrpg.core.config.fonts # Initiate fonts for the game

import pyrpg.core.config.keys as keys

from pyrpg.core.config.paths import ENTITY_PATH, SAVE_PATH

import pyrpg.core.ecs.esper as esper
import pyrpg.core.ecs.components as components
import pyrpg.core.ecs.processors as processors

import pyrpg.core.commands as commands

import pyrpg.core.maps.map as map
import pyrpg.core.quests.quest as quest

from pyrpg.core.config.config import MESSAGES # to decide if message should be generater on event
import pyrpg.core.messages.messages as messages # Fore in-game messages

########################################################
### Module Import Init - Init global variables
########################################################

global world
global maps
global quests
global event_queue
global command_queue
global message_queue
global alias_to_entity
global entity_to_alias # mapping of entity id to alias id - for displaying of in-game messages

message_queue = []
command_queue = []
event_queue = []
maps = {}
alias_to_entity = {}
quests = {}
entity_to_alias = {}

########################################################
########################################################
###             MODULE FUNCTIONS
########################################################
########################################################

########################################################
### Module Functions - Module Init Functions
########################################################

def init_world():
    ''' Prepare ECS instances for the game
    '''

    global world

    world = esper.World(timed=False)
    create_processors(world)

########################################################
### Module Functions - Game commands handler
########################################################

def process_game_commands(keys=None, events=None, debug=False):
    ''' Process game commands. It is called by CommandsProcessor.
    Processes the command_queue.
    '''
    global command_queue
    global alias_to_entity

    if debug and command_queue:
        print(f'*Command Queue: {command_queue}')


    # Process every command in the queue
    while command_queue:

        # pop out command from the beginning of the queue
        command = command_queue.pop(0)

        if debug: 
            print(f'*Processing command: {command}')

        (cmd_fnc, cmd_params) = command

        # Add reference to pressed keys and keyboard/mouse events to the parameters of md
        cmd_params.update({'keys' : keys})
        cmd_params.update({'events' : events})

        # Check if in cmd_params there is entity parameter that is not an integer but a string.
        # Such commands can be submitted by the global script processor Brain
        entity_id = cmd_params.get('entity')
        if isinstance(entity_id, str): cmd_params.update({'entity' : alias_to_entity.get(entity_id)})

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
### Module Functions - Game event handler
########################################################

def process_game_events():
    ''' Process game/quest events. It is called by GameEventProcessor
    '''
    global quests
    global message_queue

    # Process every waiting event
    while event_queue:

        # out event from the beginning of the queue
        event = event_queue.pop(0)

        # add information to the message queue if event returns a message
        event_message = event.to_string()
        message_queue.append(messages.Message(text=event_message)) if event_message else None

        # Send every event to every quest for handling
        for quest_name, quest_object in quests.items():

            # Call event handler
            quest_object.event_handler(event)

########################################################
### Module Functions - Game messages handler
########################################################

def process_game_messages():
    ''' Process game text messages. It is called by GameMessagesProcessor
    '''
    global message_queue
    global window

    # Get current time to evaluate ttl of the message
    current_time = pygame.time.get_ticks()

    # Remove all the expired messages from the message queue
    message_queue = [msg for msg in message_queue if current_time - msg.created < msg.ttl]

    # Process the valid queued messages
    messages.process(window, message_queue)

########################################################
### Module Functions - Game world creator/destructor methods
########################################################

def _create_entity(json_ent_obj, register=True, child_ref=None):
    ''' Create entity from json definition. See Quest for definitions
    '''

    global world
    global alias_to_entity
    global entity_to_alias

    # Prepare new_entity obj
    new_entity_obj = None

    # Decode entity id 
    new_entity_id = json_ent_obj.get("id")

    # Create new entity obj for the root entity
    if not child_ref: 
        new_entity_obj = world.create_entity()
        print(f'\n*Creating new entity "{new_entity_id}", id: {new_entity_obj}')

    # Read the components from the templates - order matters! latter has priority and overwrites
    # the previous components
    for template in json_ent_obj.get("templates", []):

        # Read the entity.json
        try:
            with open(ENTITY_PATH / str(template + '.json'), 'r') as entity_file:
                json_entity_data = entity_file.read()
                template_entity_data = json.loads(json_entity_data)
        except FileNotFoundError:
            print(f"Entity file {ENTITY_PATH + template + '.json'} not found.")
            raise

        print(f'**Creating components from template {template + ".json"}')
        _create_entity(template_entity_data, child_ref=new_entity_obj if not child_ref else child_ref)
        print(f'**Creating components from template {template + ".json"} done.')

    # Initiate every component
    for component in json_ent_obj.get("components"):

        # Get component type
        comp_type = component.get("type")

        # Get component params
        comp_params = component.get("params", {})

        # Create component
        try:
            result = components.create_component(
                world,
                new_entity_obj if not child_ref else child_ref,
                comp_type,
                comp_params
            )

            print(f'***{result[1]} for entity {result[0]} created.')

        except ValueError:
            print(f'Error in creation of component {comp_type} with parameters {comp_params}')
            raise ValueError

    # Add entity to the entity map - for the root entity
    if not child_ref and register:
        alias_to_entity.update({new_entity_id : new_entity_obj})
        entity_to_alias.update({new_entity_obj: new_entity_id})

    return new_entity_obj

def create_processors(world):

    global window
    global event_queue
    global command_queue
    global message_queue
    global maps

    # Processor that updates constant speed movement
    linear_movement_processor = processors.LinearMovementProcessor()

    # Processor that generates projectiles
    generate_projectiles_processor = processors.GenerateProjectileProcessor()

    # Processor that deletes entities with Temporary component from the world - once ttl expires
    clear_temporary_entity_processor = processors.ClearTemporaryEntityProcessor()

    # Update the animation for rendering the model
    render_model_anim_update_processor = processors.RenderableModelAnimationUpdateProcessor()

    # Status procesor updates status of the entity - idle, walk, ...
    render_model_anim_action_processor = processors.RenderableModelAnimationActionProcessor()

    # Movement processor updates entity position based on the velocity 
    movement_processor = processors.MovementProcessor()

    # Render GAME WINDOW background procesor to display game stats and anything else
    render_background_processor = processors.RenderBackgroundProcessor(window=window)

    # Render CAMERA background processor 
    render_camera_background_processor = processors.RenderCameraBackgroundProcessor()

    # Render processor to display map
    render_map_processor = processors.RenderMapProcessor(window=window, maps=maps)

    # Render processor to place renderable entities with position on the screen
    render_world_processor = processors.RenderWorldProcessor(window=window)
    render_model_world_processor = processors.RenderModelWorldProcessor(window=window)
    render_talk_processor = processors.RenderTalkProcessor2(window=window)


    # Render debug processor to display debug information for renderable entities
    render_debug_processor = processors.RenderDebugProcessor(window=window)

    # Input processor to process keys pressed - the commands are queued and processed later by 
	# CommandProcessor
    input_processor = processors.InputProcessor(command_queue)

    # Collision Entity processor
    collision_entity_generator_processor = processors.CollisionEntityGeneratorProcessor()

    # Collision Map processor
    collision_map_processor = processors.CollisionMapProcessor(maps=maps)

    # Teleport Collision processor
    collision_teleport_processor = processors.CollisionTeleportProcessor(event_queue)

    # Damaging Collision processor
    collision_damage_processor = processors.CollisionDamageProcessor(event_queue)

    # Weapon Collision processor
    collision_weapon_processor = processors.CollisionWeaponProcessor(event_queue)

    # Wearable Collision processor
    collision_wearable_processor = processors.CollisionWearableProcessor(event_queue)

    # Item Collision processor
    collision_item_processor = processors.CollisionItemProcessor(event_queue)

    # Entity Collision processor - added command queue processor to generate corrective movements
    collision_entity_processor = processors.CollisionEntityProcessor(event_queue, command_queue)

    # Collision Deletion processor - deletes entities with component DeleteOnCollision
    collision_deletion_processor = processors.CollisionDeletionProcessor()

    # Collision position corrector processor - OBSOLETE - substituted by CollisionEntityProcessor
    #collision_corrector_processor = processors.CollisionCorrectorProcessor()

    # Camera processor - update position of the camera
    update_camera_offset_processor = processors.UpdateCameraOffsetProcessor(maps=maps)

    # Game events processor - triggers actions based on previously generated events
    game_events_processor = processors.GameEventsProcessor(process_game_events)

    # Command processor - processes all commands from the command queue
    command_processor = processors.CommandProcessor(process_game_commands)

    # Brain processor
    brain_processor = processors.BrainProcessor(command_queue)

    # Game messages processor
    game_messages_processor = processors.GameMessagesProcessor(process_game_messages)

    ##### #### #### ####
    # Beware of order of the processors
    ##### #### #### ####

    ### First lets read input from player or/and AI. The resulting commands are stored in cmd_stream
    world.add_processor(input_processor)
    world.add_processor(brain_processor)

    ### Process all the commands from the command stream
    world.add_processor(command_processor)

    ### Move the entities based on their movement vector
    world.add_processor(linear_movement_processor)  # update entities that are moving at constant speed (projectiles/arrows)
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
    world.add_processor(collision_deletion_processor)	# Deletes entities that collided and have DeleteOnCollision component


    ### Process all events that were generated by collision processors
    world.add_processor(game_events_processor)	# Based on events generated by the collisions (teleportation, item pickups) now is the time to see if there are some game actions that we want to do - e.g. cinematics


    ##################################
    ### Render the world on the screen
    ##################################
    # Update all cameras
    world.add_processor(update_camera_offset_processor)

    ### Change the entity state based on everything what has happened before rendering
    world.add_processor(render_model_anim_action_processor)

    ### Update the entity animation
    world.add_processor(render_model_anim_update_processor)

    # Render game window background - stats / inventory / picture
    world.add_processor(render_background_processor)

    # Render cameras background - in order not to have blured screen on
    # parts where map is not displayed.
    world.add_processor(render_camera_background_processor)

    # Render maps
    world.add_processor(render_map_processor)

    # Render objects with Renderable component
    world.add_processor(render_world_processor)

    # Render world entities
    #world.add_processor(render_world_processor)
    world.add_processor(render_model_world_processor)

    # Render text bubbles
    world.add_processor(render_talk_processor)

    # Render additional debug information on the screen
    world.add_processor(render_debug_processor)

    # Render game messages on the screen
    world.add_processor(game_messages_processor)

    ##################################
    ### Clearing processors
    ##################################

    # Delete entities with Temporary component from the world
    world.add_processor(clear_temporary_entity_processor)

def create_map(map_name):
    ''' Register and create new map if not already created
    Called from Quest/Phase class
    '''

    # All maps are here
    global maps

    # Create map, if not exists
    if not maps.get(map_name, None):
        new_map = map.Map(map_name)	
        maps.update({map_name : new_map})

def delete_map(map_name):
    ''' Unregister and delete the map object
    '''

    # All maps are here
    global maps

    # If map is registered - de-reference it
    # As map reference is stored only in global dictionary and
    # not on individual entities, it is enough to dereference it
    # here and not on individual entities.
    if maps.get(map_name, None):
        del maps[map_name]

def delete_entity(entity_name):
    ''' Delete and un-register entity from the world
    '''

    global world
    global alias_to_entity

    # If entity is registered, delete it
    if alias_to_entity.get(entity_name, None):

        # Delete it from Esper world
        world.delete_entity(alias_to_entity.get(entity_name))
        
        # Un-register the entity
        del alias_to_entity[entity_name]

########################################################
### Module Functions - Save and load game
########################################################

def new_game():
    global quests
    global event_queue

    sample_quest = quest.load_quest('test_quest', event_queue)
    quests.update({'test_quest' : sample_quest})

def load_game():
    ''' Load game state 
    '''

    with open(SAVE_PATH / 'save.dat','rb') as f: game_state = pickle.load(f)

    # Restore command queue
    global command_queue
    command_queue = game_state.get('command_queue')

    # Restore event queue
    global event_queue
    event_queue = game_state.get('event_queue')

    # Restore maps
    global maps
    maps = {}

    for map_name in game_state.get('maps'):
        sample_map = map.Map(map_name)	
        maps.update({ map_name : sample_map})

    # Restore entity mapping
    global alias_to_entity
    alias_to_entity = game_state.get('entity_map')

    # Restore quests
    global quests
    quests = game_state.get('quests')

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

    world.get_processor(processors.CollisionMapProcessor).post_load(maps)
    print(world.get_processor(processors.CollisionMapProcessor))

    world.get_processor(processors.UpdateCameraOffsetProcessor).post_load(maps)
    print(world.get_processor(processors.UpdateCameraOffsetProcessor))

    world.get_processor(processors.RenderBackgroundProcessor).post_load(window) 
    print(world.get_processor(processors.RenderBackgroundProcessor))

    world.get_processor(processors.RenderMapProcessor).post_load(window, maps) 
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
    global event_queue
    global maps
    global alias_to_entity
    global world
    global quests

    game_state = {}

    # Prepare command queue for save
    game_state.update({'command_queue' : command_queue})

    # Prepare event queue for save
    game_state.update({'event_queue' : event_queue})

    # Preapare maps for save - we will only save list of names
    # and reload maps from scratch during load game
    game_state.update({'maps' : [map_name for map_name in maps.keys()]})
    
    # Prepare entity name -> entity id mapping for save
    game_state.update({'entity_map' : alias_to_entity})

    # Prepare quests for save
    game_state.update({'quests' : quests})
    
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

    with open(SAVE_PATH / 'save.dat', 'wb') as f: pickle.dump(game_state, f)

    ### Restore the non-serializable objects so that game can continue
    for entity_id in world._entities.keys():
    # Go through every component of the entity
        for component in world.components_for_entity(entity_id):
            # Execute pre-save steps on the component			
            component.post_load()
            print(f'SAVE: Finished post-load steps for entity {entity_id} and component {component}')

    ### Restore processor references
    world.get_processor(processors.CollisionMapProcessor).post_load(maps)
    print(world.get_processor(processors.CollisionMapProcessor))

    world.get_processor(processors.UpdateCameraOffsetProcessor).post_load(maps)
    print(world.get_processor(processors.UpdateCameraOffsetProcessor))

    world.get_processor(processors.RenderBackgroundProcessor).post_load(window) 
    print(world.get_processor(processors.RenderBackgroundProcessor))

    world.get_processor(processors.RenderMapProcessor).post_load(window, maps) 
    print(world.get_processor(processors.RenderMapProcessor))

    world.get_processor(processors.RenderWorldProcessor).post_load(window) 
    print(world.get_processor(processors.RenderWorldProcessor))

    world.get_processor(processors.RenderDebugProcessor).post_load(window) 
    print(world.get_processor(processors.RenderDebugProcessor))

    return 0

def pause_game():
    global window
    pygame.draw.rect(window, (128, 128, 128, 0), pygame.Rect(100, 100, 200, 100))


########################################################
### Module Functions - Main game loop
########################################################

def run(key_events, key_pressed, dt, debug):
    # Initialize Pygame stuff - at the beginning due to convert() function
    ##global window

    ##pygame.init()
    ##window = pygame.display.set_mode((850, 850), 0, 32)
    ##clock = pygame.time.Clock()

    # All commands are queued here
    ##global command_queue
    ##command_queue = []

    # All events are queued here
    ##global event_queue
    ##event_queue = []

    # All maps are here
    ##global maps
    ##maps = {}

    # Entity name vs id is stored here
    ##global alias_to_entity
    ##alias_to_entity = {}

    #####
    # Initialize Esper world with entites and processors
    #####
    ##global world

    ##world = esper.World(timed=False)
    ##create_processors(world)

    # All quests are here
    ##global quests
    ##quests = {}

    ##sample_quest = quest.load_quest('test_quest', event_queue)
    ##quests.update({'test_quest' : sample_quest})

    # Print entity mappings
    ##print(alias_to_entity)

    #####
    # The main loop
    #####
    ##running = True
    ##while running:

    #global clock

    # Keep game at constant FPS
    #dt = clock.tick(config.FPS)

    # Read the keys pressed, mouse, win resize etc.
    ##key_events = pygame.event.get()
    ##key_pressed = pygame.key.get_pressed()

    # Check for End Game
    for event in key_events:
        if event.type == pygame.QUIT:
            return 'QUIT_GAME'
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'MAIN_MENU'
            elif event.key == keys.K_SAVE_GAME:
                print(f'Saving game ...')
                return 'SAVE_GAME' #save_game()
            elif event.key == keys.K_LOAD_GAME:
                print(f'Loading game ...')
                return 'LOAD_GAME' # load_game()
            elif event.key == keys.K_PAUSE_GAME:
                print(f'Pausing game')
                return 'PAUSE_GAME' # load_game()


    # Update all the processors, pass key events as a parameter
    # and dt (how long the previous frame was processed)
    # Parameter will be passed to all processors. Those who want it
    # will process it.

    # maps and quests added in order that command can be informed about quest to change the phase
    world.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)


    # Flip the framebuffers
    #pygame.display.update()
    #pygame.display.flip()

    # Display FPS in window title
    #pygame.display.set_caption('FPS: ' + str(int(clock.get_fps())))

    return 'GAME'



def quit():
    pygame.quit()
