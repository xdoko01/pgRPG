''' core.engine_3ex module
'''

import pygame # for pygame.QUIT, pygame.KEYDOWN
import logging
import pyrpg.core.config.keys as keys
import pyrpg.core.quests.quest as quest

# Create logger
logger = logging.getLogger(__name__)

from pyrpg.core.config.states import State
from pyrpg.core.managers.gui_manager import GUIManager

from pyrpg.core.managers.map_manager import MapManager
from pyrpg.core.managers.message_manager import MessageManager
from pyrpg.core.managers.dialog_manager import DialogManager
from pyrpg.core.managers.command_manager import CommandManager
from pyrpg.core.managers.quest_manager import QuestManager
from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.managers.event_manager import EventManager

logger.info(f'Engine initiated')

class Game:

    def __init__(self, gui_manager: GUIManager, timed: bool=False) -> None:

        self.gui_manager = gui_manager # Reference to GUI manager created in main module
        self.map_manager = MapManager()
        self.message_manager = MessageManager()
        self.dialog_manager = DialogManager()
        self.command_manager = CommandManager() # command manager must have reference to Game in order commands can manipulate the game world
        self.quest_manager = QuestManager()
        self.ecs_manager = ECSManager(timed=timed)
        
        # Reference function for adding events
        # TODO - maybe it would be better to handle processing of events within processor that
        # would receive list of events and handle event function and using those would implement
        # event processing.
        self.event_manager = EventManager(self.quest_manager.handle_event)

        # Following functions will be visible for game processors. Processor can have several
        # references from different managers and thus realize integration between those managers.
        self._game_functions = {
            'window' : self.gui_manager.window,
            'create_entity_fnc' : self.ecs_manager.create_entity,
            'remove_entity_fnc' : self.ecs_manager.delete_entity,
            #'ammo_pack_event_queue' : event_queue,
            'maps' : self.map_manager._maps,
            #'input_command_queue' : self.command_manager.add_command,
            'teleport_event_queue' : self.event_manager.add_event,
            'weapon_event_queue' : self.event_manager.add_event,
            'ammo_pack_event_queue' : self.event_manager.add_event,
            'wearable_event_queue' : self.event_manager.add_event,
            'item_pickup_event_queue' : self.event_manager.add_event,
            'entity_coll_event_queue' : self.event_manager.add_event,
            'game_event_handler' : self.event_manager.process_events,
            'game_messages' : self.message_manager.get_messages,
            'add_message' : self.message_manager.add_message,
            'damage_event_queue' : self.event_manager.add_event,
            'destroy_event_queue' : self.event_manager.add_event,
            'score_event_queue' : self.event_manager.add_event,
            # Commands
            'FNC_ADD_COMMAND' : self.command_manager.add_command,
            'FNC_CLEAR_COMMANDS' : self.command_manager.clear_commands,
            'FNC_GET_COMMANDS' : self.command_manager.get_commands,
            'FNC_PROCESS_COMMANDS' : self.command_manager.process_commands,
            # Events
            'add_event_fnc' : self.event_manager.add_event,
            'clear_events_fnc' : self.event_manager.clear_events,
            'get_events_fnc' : self.event_manager.get_events,
            # ECS
            'FNC_GET_ENTITY_ID' : self.ecs_manager.get_entity_id
        }

        self.ecs_manager.set_game_functions(self._game_functions)
        logger.info(f'Game initiated')


    def _clear_game(self) -> None:
        '''Clear all game related resources'''
        self.map_manager.clear_maps()
        self.dialog_manager.clear_dialogs()
        self.message_manager.clear_messages()
        self.command_manager.clear_commands()
        self.event_manager.clear_events()
        self.quest_manager.clear_quests()
        self.ecs_manager.clear_ecs()
        logger.info(f'All game resources cleared.')

    def new_game(self, quest_name: str) -> None:

        #clear everything
        self._clear_game()

        #add new quest
        new_quest = quest.load_quest_ex(quest_name,
            map_mng=self.map_manager,
            dialog_mng=self.dialog_manager,
            event_mng=self.event_manager,
            ecs_mng=self.ecs_manager)

        self.quest_manager.add_quest(quest_name, new_quest)
        logger.info(f'Quest "{quest_name}" successfully loaded.')

    def exit_game(self) -> None:
        self._clear_game()
        pygame.quit()

    def run(self, key_events, key_pressed, dt, debug):
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
        self.ecs_manager.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)

        return State.GAME
