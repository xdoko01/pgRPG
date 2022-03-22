''' core.engine_5ex module
'''

import logging

# Create logger
logger = logging.getLogger(__name__)

import pygame # for pygame.QUIT, pygame.KEYDOWN
import pyrpg.core.config.keys as keys

from pyrpg.core.config.states import State

from pyrpg.main_5ex import gui_manager
from pyrpg.main_5ex import sound_manager

from pyrpg.core.managers.map_manager import MapManager
map_manager = MapManager()

from pyrpg.core.managers.message_manager import MessageManager
message_manager = MessageManager()

from pyrpg.core.managers.dialog_manager import DialogManager
dialog_manager = DialogManager()

from pyrpg.core.managers.command_manager import CommandManager
command_manager = CommandManager()

from pyrpg.core.managers.quest_manager import QuestManager
quest_manager = QuestManager()

from pyrpg.core.managers.ecs_manager import ECSManager
ecs_manager = ECSManager()

# Reference function for adding events
# TODO - maybe it would be better to handle processing of events within processor that
# would receive list of events and handle event function and using those would implement
# event processing.
from pyrpg.core.managers.event_manager import EventManager
event_manager = EventManager(quest_manager.handle_event)

# Functions that can be used by ESC processors
game_functions={
        'window' : gui_manager.window,
        'create_entity_fnc' : ecs_manager.create_entity,
        'remove_entity_fnc' : ecs_manager.delete_entity,
        #'ammo_pack_event_queue' : event_queue,
        'maps' : map_manager._maps,
        #'input_command_queue' : command_manager.add_command,
        'teleport_event_queue' : event_manager.add_event,
        'weapon_event_queue' : event_manager.add_event,
        'ammo_pack_event_queue' : event_manager.add_event,
        'wearable_event_queue' : event_manager.add_event,
        'item_pickup_event_queue' : event_manager.add_event,
        'entity_coll_event_queue' : event_manager.add_event,
        'game_event_handler' : event_manager.process_events,
        'game_messages' : message_manager.get_messages,
        'add_message' : message_manager.add_message,
        'damage_event_queue' : event_manager.add_event,
        'destroy_event_queue' : event_manager.add_event,
        'score_event_queue' : event_manager.add_event,
        # Commands
        'FNC_ADD_COMMAND' : command_manager.add_command,
        'FNC_CLEAR_COMMANDS' : command_manager.clear_commands,
        'FNC_GET_COMMANDS' : command_manager.get_commands,
        'FNC_PROCESS_COMMANDS' : command_manager.process_commands,
        # Events
        'add_event_fnc' : event_manager.add_event,
        'clear_events_fnc' : event_manager.clear_events,
        'get_events_fnc' : event_manager.get_events,
        # ECS
        'FNC_GET_ENTITY_ID' : ecs_manager.get_entity_id}

def initialize(timed):
    ecs_manager.initialize(timed=timed, game_functions=game_functions)
    logger.info(f'Engine initiated')


def _clear_game() -> None:
    '''Clear all game related resources'''
    map_manager.clear_maps()
    dialog_manager.clear_dialogs()
    message_manager.clear_messages()
    command_manager.clear_commands()
    event_manager.clear_events()
    quest_manager.clear_quests()
    ecs_manager.clear_ecs()
    
    logger.info(f'All game resources cleared.')

def new_game(quest_name: str) -> None:

    #clear everything
    _clear_game()

    #add new quest
    quest_manager.add_quest(quest_name,
        map_mng=map_manager,
        dialog_mng=dialog_manager,
        event_mng=event_manager,
        ecs_mng=ecs_manager)

    logger.info(f'Quest "{quest_name}" successfully loaded.')

def exit_game() -> None:
    _clear_game()
    logger.info(f'Game exited.')

def run(key_events, key_pressed, dt, debug):
    # Check for End Game
    for event in key_events:
        if event.type == pygame.QUIT:
            logger.info(f'Exiting the game')
            return State.EXIT_GAME_DIALOG
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                #self.gui_manager.save_screen()
                logger.info(f'Leaving to main menu')
                return State.MAIN_MENU
            elif event.key == keys.K_SAVE_GAME:
                pass
            elif event.key == keys.K_LOAD_GAME:
                pass

    # maps and quests added in order that command can be informed about quest to change the phase
    ecs_manager.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)

    return State.GAME
