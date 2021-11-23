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

import json
import pickle # for savegame/loadgame
import re # for removing of comments from json files
import importlib
import logging
from typing import ClassVar

# Create logger
logger = logging.getLogger(__name__)

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

from pyrpg.functions import get_class_object # for dynamic creation of components and processors from json definition

import pyrpg.core.config.fonts # Initiate fonts for the game

import pyrpg.core.config.keys as keys

from pyrpg.core.config.paths import Path, ENTITY_PATH, DIALOG_PATH, SAVE_PATH, IMAGE_PATH, FONT_PATH

import pyrpg.core.ecs.esper as esper
import pyrpg.core.ecs.components as components
import pyrpg.core.ecs.processors as processors

import pyrpg.core.commands as commands

import pyrpg.core.maps.map as map
import pyrpg.core.quests.quest as quest

from pyrpg.core.config.config import MESSAGES # to decide if message should be generater on event
import pyrpg.core.messages.messages as messages # Fore in-game messages

import pyrpg.utils.dialog as dialog # for creation of dialogs

import pyrpg.core.lua as lua # for usage of lua scripts

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
global dialogs # stores all the dialogs that are necessary for the quest phase

global cons_update_fnc # remember the function that is bliting text to the console

global screen_copy # make copy of the window - used for pause game

cons_update_fnc = lambda x: None # console update function is empty function by default

message_queue = []
command_queue = []
event_queue = []
maps = {}
alias_to_entity = {}
quests = {}
entity_to_alias = {}
dialogs = {}

########################################################
########################################################
###             MODULE FUNCTIONS
########################################################
########################################################

def get_entity_id(entity_alias):
    ''' Translate entity alias (string) to entity id (integer)
    based on alias_to_entity dictionary.
    '''

    global alias_to_entity

    try:
        return alias_to_entity.get(entity_alias, None)
    except TypeError:
        # If entity_alias is list or dictionary (non hashable)
        return None

########################################################
### Module Functions - Module Init Functions
########################################################

def show_console(key_events, key_pressed, dt):
    global window
    global screen_copy

    window.blit(screen_copy, (0, 0))

    return 'CONSOLE'

def save_screen_copy(flip_before_copy=False):
    ''' Parameter is used to force displaying everything on screen.
    Was prepared due to PHASE start of the first quest that was processed
    before anything was blitted on the screen
    '''
    # Make copy of the window content
    global screen_copy
    global window

    if flip_before_copy: pygame.display.update()
    
    screen_copy = window.copy()
    print(f'Screen has been copied')

def init_console_fnc(cns_fnc):
    ''' Assign the function that prints and displays messages onto
    the console.
    '''
    global cons_update_fnc

    cons_update_fnc = cns_fnc if cns_fnc is not None else (lambda x: None)

def init_world(timed=False):
    ''' Prepare ECS instances for the game
    '''

    global world

    world = esper.World(timed=timed)
    #create_processors(world)
    cons_update_fnc('engine->init_world. World initiation finished.')
    logger.info(f'Init is done.')

########################################################
### Module Functions - Game commands handler
########################################################

def get_game_commands():
    ''' Returns commands contained in the command queue
    '''
    global command_queue

    return command_queue

def add_game_command(cmd):
    ''' Adds single command (tuple) to the command queue

        :param cmd: Command (tuple or list with 2 items)
        :returns: 0 on success
    '''
    global command_queue

    try:
        cmd_fnc, cmd_params = cmd
        command_queue.append((cmd_fnc, cmd_params))
        return 0
    except ValueError:
        raise

def clear_game_commands():
    ''' Deletes all commands from the command queue
    '''
    global command_queue

    del command_queue[:]

def process_game_commands(keys=None, events=None, debug=False):
    ''' Process game commands. It is called by CommandsProcessor.
    Processes the command_queue.
    '''
    global command_queue
    global alias_to_entity

    if debug and command_queue:
        print(f'{__name__} - command queue content: "{command_queue}"')


    # Process every command in the queue
    while command_queue:

        # pop out command from the beginning of the queue
        command = command_queue.pop(0)

        if debug: 
            print(f'{__name__} - processing command "{command}"')

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

def get_game_events():
    ''' Returns events contained in the event queue
    '''
    global event_queue

    return event_queue

def add_game_event(event):
    ''' Adds single event to the event queue

        :param event: Event object
        :returns: 0 on success
    '''
    global event_queue

    event_queue.append(event)
    return 0

def clear_game_events():
    ''' Deletes all events from the event queue
    '''
    global event_queue

    del event_queue[:]

def process_game_events_ex(process=None, ignore=None):
    ''' Process particular game/quest event types that are specified on the input.
    '''

    global quests
    global message_queue
    global event_queue

    # This will be filled by the events that are outstanding for processing
    new_event_queue = []

    while event_queue:

        # Pop out event from the beginning of the queue
        event = event_queue.pop(0)

        # If event is to be ignored move it to the new queue
        if ignore is not None and event.event_type in ignore:
          new_event_queue.append(event)

        # If event is not in process list
        elif process is not None and event.event_type not in process:
          new_event_queue.append(event)

        # Process the rest of the events
        else:

            # add information to the message queue if event returns a message
            event_message = event.to_string()
            message_queue.append(messages.Message(text=event_message)) if event_message else None

            # Send every event to every quest for handling
            for quest_name, quest_object in quests.items():

                # Call event handler
                quest_object.event_handler(event)

    # Renew the value of the event queue - it must be done via extend. I cannot reassigned like
    # event_queue = new_event_queue because other processors have stored link directly to original
    # global event_queue
    event_queue.extend(new_event_queue)

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

def create_dialog(dlg_data):
    ''' Create dialog from dictionary definition contained in dictionary
    json_dlg_obj and stores it in global engine.dialogs dictionary

     - dlg_data - original data from the quest
     - new_dlg_data - data after taking into account all templates
     - new_dlg_obj - dictionary with surface objects generated from the data
    '''

    global dialogs

    def prepare_dlg_data_from_template(dlg_template):
        ''' Returns dictionary based of json file with dialog
        template specification.
        '''

        # Read the json file with dialog definition
        try:
            with open(DIALOG_PATH / Path(dlg_template + '.json'), 'r') as dlg_file:
                json_dlg_data = dlg_file.read()
                dlg_data = json.loads(re.sub("//.*","", json_dlg_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
        except FileNotFoundError:
            print(f"Dialog file '{DIALOG_PATH / Path(dlg_template + '.json')}' not found.")
            raise

        # Final dlg data - empty at the start
        final_dlg_data = {}

        # Check if some template is used - first merge templates together - deeper and first go first
        for template in dlg_data.get('templates', []):
            
            # Get the json definition of the template and merge it
            final_dlg_data = { **prepare_dlg_data_from_template(template), **final_dlg_data }

        final_dlg_data = { **final_dlg_data, **dlg_data }

        return final_dlg_data

    # Prepare new empty dictionary that will hold the dialog's data
    new_dlg_data = {}

    # Decode dialog's id (name) - mandatory
    new_dlg_id = dlg_data.get('id')

    # Create the final dictionary definition using existing templates
    for template in dlg_data.get("templates", []):

        # Get the json definition of the template and merge it
        new_dlg_data = { **prepare_dlg_data_from_template(template), **new_dlg_data }

    # Now the final dialog description is stored here
    new_dlg_data = { **new_dlg_data, **dlg_data }
    cons_update_fnc(new_dlg_data)

    # Now there is time to make surfaces and register the data object
    new_dlg_obj = dialog.prepare_dlg_obj_from_data(new_dlg_data, img_path=IMAGE_PATH, font_path=FONT_PATH)

    # Store the dialog
    dialogs.update({new_dlg_id : new_dlg_obj})

def _create_entity(json_ent_obj, entity_id=None, register=True, child_ref=None):
    ''' Create entity from json definition. See Quest for definitions

        Parameters:
            :param json_ent_obj: Description of entity in JSON format (python dict).
            :type json_ent_obj: dict

            :param entity_id: Parameter overrides entity id that is present in json_ent_obj definition.
            :type entity_id: str

            :param register: Should the entity be globally registered with engine.
            :type register: bool

            :param child_ref: Used for recursive creation of entity from templates.
            :type child_ref: world.entity Object

            :raise: ValueError - in case of problem with component creation
    '''

    global world
    global alias_to_entity
    global entity_to_alias

    # Prepare new_entity obj
    new_entity_obj = None

    # Decode entity id - use the one from fcion call with priority or the on fron entity description
    new_entity_id = entity_id if entity_id else json_ent_obj.get("id")

    # Create new entity obj for the root entity
    if not child_ref:
        new_entity_obj = world.create_entity()
        print(f'\n*Creating new entity "{new_entity_id}", id: {new_entity_obj}')

    # Read the components from the templates - order matters! latter has priority and overwrites
    # the previous components
    for template in json_ent_obj.get("templates", []):

        # Read the entity.json
        try:
            with open(ENTITY_PATH / Path(template + '.json'), 'r') as entity_file:
                json_entity_data = entity_file.read()
                template_entity_data = json.loads(re.sub("//.*","", json_entity_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
        except FileNotFoundError:
            print(f"Entity file {ENTITY_PATH / Path(template + '.json')} not found.")
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
                alias_to_entity, # Part of the init of component might be reference to other entity in form of string alias. Hence we need to pass the translation dictionary to the component factory
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

def delete_entity_id(entity_id):
    ''' Delete and un-register entity from the world.
    Entity is represented by its integer id
    '''

    global world
    global alias_to_entity
    global entity_to_alias

    # Get alias
    alias = entity_to_alias.get(entity_id, None)

    # Delete it from Esper world
    world.delete_entity(entity_id)
        
    # Un-register the entity - ignore if not found, can be unregistered entity
    try:
        del alias_to_entity[alias]
        del entity_to_alias[entity_id]
    except KeyError:
        pass

def delete_entity_alias(alias):
    ''' Delete and un-register entity from the world.
    Entity is represented by its alias
    '''

    global world
    global alias_to_entity
    global entity_to_alias

    # Get entity number
    entity_id = alias_to_entity.get(alias, None)

    # If entity is registered, delete it
    if entity is not None:

        # Delete it from Esper world
        world.delete_entity(entity_id)
        
        # Un-register the entity
        del alias_to_entity[alias]
        del entity_to_alias[entity_id]

def delete_dialog(dialog_name):
    ''' Delete and unregister dialog object
    '''

    global dialogs

    # Get dialog object based on its name
    dialog = dialogs.get(dialog_name, None)

    # If dialog exists, delete it
    if dialog is not None:
        del dialogs[dialog_name]

########################################################
### Module Functions - Manage Processors
########################################################

# List of processor parameters that are maped to core.engine functions
PROC_PARAMS = {
    'create_entity_fnc' : _create_entity,
    'remove_entity_fnc' : delete_entity_id,
    'ammo_pack_event_queue' : event_queue,
    'window' : window,
    'maps' :maps,
    'input_command_queue' : command_queue,
    'teleport_event_queue' : event_queue,
    'weapon_event_queue' : event_queue,
    'ammo_pack_event_queue' : event_queue,
    'wearable_event_queue' : event_queue,
    'item_pickup_event_queue' : event_queue, # obsolete, use add_event_fnc instead
    'entity_coll_event_queue' : event_queue,
    'game_event_handler' : process_game_events_ex,
    'game_commands_handler' : process_game_commands,
    'game_messages_handler' : process_game_messages,
    'damage_event_queue' : event_queue,
    'destroy_event_queue' : event_queue,
    'score_event_queue' : event_queue,
    # Commands
    'add_command_fnc' : add_game_command,
    'clear_commands_fnc' : clear_game_commands,
    'get_commands_fnc' : get_game_commands,
    # Events
    'add_event_fnc' : add_game_event,
    'clear_events_fnc' : clear_game_events,
    'get_events_fnc' : get_game_events
}

def _check_processor(proc_class: esper.Processor) -> str:
    '''Checks if the class representing the processors contains all necessary
    parts in order to successfully work in the game.

    Checks are following:
        - Existence of prerequisited classes in the game world
    '''

    # Check that the dependencies of the processor on other processors are kept - are already in the world
    try:
        prereqs = proc_class.PREREQ
    except AttributeError:
        prereqs = []    # no prerequisities if class attr PREREQ does not exist

    for prereq in prereqs:

        # Unpack the prerequisity processor information
        prereq_module, prereq_class = prereq

        # Get the prerequisity processor class
        try:
            check_class = get_class_object(None, 'pyrpg.core.ecs.processors.' + prereq_module, prereq_class)
        except ValueError:
            raise ValueError(f'Prerequisite class "{prereq_module}.{prereq_class}" cannot be loaded from definition of processor "{proc_class.__name__}".')

        # Verify that the prerequisite processor class has been already instantiated
        if not world.get_processor(check_class):
            raise ValueError(f'Processor "{proc_class.__name__}" is missing prereq. processor {prereq_class}. Game might work incorrectly!')


def _load_processor(proc_module : str, proc_class : str, cust_proc_class_attrs : dict) -> esper.Processor:
    '''Imports the processor class and registers it into the world'''

    # Get the definition of the processor class
    try:
        new_class = get_class_object(None, 'pyrpg.core.ecs.processors.' + proc_module, proc_class)
    except ValueError:
        raise ValueError(f'Error during loading of processor class "{proc_class}"')

    # Check that prerequisities are fulfilled - all required processors are already initiated in the game world
    try:
       _check_processor(new_class)
    except ValueError:
        raise ValueError(f'Error during checking of prerequisities of processor "{new_class.__name__}"')

    # Get all attributes of the processor class
    proc_attrs = new_class.__init__.__code__.co_varnames[1:]

    # Substitute the attributes with reference to specifice engine functions
    proc_attrs = { arg : PROC_PARAMS.get(arg) for arg in proc_attrs if PROC_PARAMS.get(arg) is not None}

    # Overwrite the attributes with custom attributes from the json definition of the quest
    proc_attrs = {**proc_attrs, **cust_proc_class_attrs}

    # Initiate and return the processor class
    return new_class(**proc_attrs)


def load_processors(processors: list) -> None:
    '''Imports and registers to the world processors specified by the quest definition.'''

    for processor in processors:
        module_name, class_name, params = processor
        new_proc = _load_processor(module_name, class_name, params)
        world.add_processor(new_proc)
        cons_update_fnc(f'Processor {class_name} initiated.')


# Soon to be obsolete
def _create_processor(proc_str):
    '''
    Example:
        _create_processor(['ExampleProcessor', {'example_arg' : arg})

        - adds the processor to the world
    '''

    # Get processor class and arguments
    try:
        proc_class, proc_args = processors.get_processor(proc_str[0])
    except ValueError:
        raise ValueError(f'Error in creation of processor "{proc_str}"')

    # Check that the dependencies of the processor on other processors are kept - are already in the world
    try:
        prereqs = proc_class.PREREQ
    
    except AttributeError:
        prereqs = []    # no prerequisities if class attr PREREQ does not exist

    for prereq in prereqs:

        # Get class and arguments of the prerequisited processor
        try:
            prereq_proc_class, _ = processors.get_processor(prereq)
        except ValueError:
            raise ValueError(f'Error in creation of prerequisity processor "{prereq}" for processor {proc_class}')

        # Verify that the prerequisite processor has been already instantiated
        if not world.get_processor(prereq_proc_class):
             print(f'WARNING: Processor "{proc_class}" is missing prereq. processor {prereq}. Game might work incorrectly!')

    # Create and register new processor in the game world

    # First, try to prepare params from PROC_PARAMS dictionary
    new_proc_params = { arg : PROC_PARAMS.get(arg) for arg in proc_args if PROC_PARAMS.get(arg) is not None}
    # Second, add params that are passed from the quest definition, to override and add to PROC_PARAMS
    new_proc_params = {**new_proc_params, **proc_str[1]}
    new_proc = proc_class(**new_proc_params)
    
    # Add processor to the world
    world.add_processor(new_proc)
    cons_update_fnc(f'{proc_str[0]} ({new_proc_params}) initiated.')
    print(f'Processor "{proc_class}" was created')

########################################################
### Module Functions - Save and load game
########################################################

def new_game(quest_name):
    ''' Loads definitions and objects from the defined quest
    into the game world.

    Parameters:
        :param quest_name: Name of the quest with definitions (mapped to json file)
        :type quest_name: str
    '''

    global quests
    global event_queue

    new_quest = quest.load_quest(quest_name, event_queue)
    quests.update({quest_name : new_quest})
    cons_update_fnc(f'engine->new_game. Game definition contained in "{quest_name}" was loaded.')

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

def pause_game(key_events, key_pressed, dt):

    global window
    global screen_copy
    global dialogs

    # Paste window copy
    window.blit(screen_copy, (0, 0))

    dialog.display_dlg(window, [100, 100], dialogs.get('dlg_pause'))

    for event in key_events:
        if event.type == pygame.QUIT:
            return 'QUIT_GAME'
        elif event.type == pygame.KEYDOWN:
            if event.key == keys.K_PAUSE_GAME:
                return 'GAME'

    return 'PAUSE_GAME'


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
                # Do copy of the game window
                save_screen_copy()
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

    # Run finalize method on all processors - important for example for closing of files
    world.finalize()

    pygame.quit()
