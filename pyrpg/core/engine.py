''' core.engine_3ex module
'''

import logging

# Create logger
logger = logging.getLogger(__name__)

import pygame # for pygame.QUIT, pygame.KEYDOWN
import pyrpg.core.config.keys as keys

from pyrpg.core.config.states import State
from pyrpg.core.managers.gui_manager import GUIManager
from pyrpg.core.managers.sound_manager import SoundManager

from pyrpg.core.managers.map_manager import MapManager
from pyrpg.core.managers.message_manager import MessageManager
from pyrpg.core.managers.dialog_manager import DialogManager
from pyrpg.core.managers.command_manager import CommandManager
from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.managers.event_manager import EventManager
from pyrpg.core.managers.script_manager import ScriptManager

from pyrpg.core.managers.quest_loader import QuestLoader

from pathlib import Path
from pyrpg.core.config.paths import QUEST_PATH
from pyrpg.core.events.event import Event

logger.info(f'Engine initiated')

class Game:

    def __init__(self, gui_manager: GUIManager, sound_manager: SoundManager, timed: bool=False) -> None:

        # System resources managers
        self.gui_manager = gui_manager # for drawing anything on the screen
        self.sound_manager = sound_manager # for playing music and sounds

        # Gameplay managers
        self.map_manager = MapManager()
        self.message_manager = MessageManager()
        self.dialog_manager = DialogManager()
        self.command_manager = CommandManager() # command manager must have reference to Game in order commands can manipulate the game world
        self.ecs_manager = ECSManager()
        self.script_manager = ScriptManager(alias_to_entity_dict_fnc=self.ecs_manager.get_alias_to_entity_dict)
        
        # Reference function for adding events
        # TODO - maybe it would be better to handle processing of events within processor that
        # would receive list of events and handle event function and using those would implement
        # event processing.
        #self.event_manager = EventManager(self.quest_manager.handle_event)
        self.event_manager = EventManager(self.script_manager.execute_event_actions)

        self.ecs_manager.initialize(timed=timed, game_functions={
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
            'FNC_ADD_EVENT' : self.event_manager.add_event,
            'add_event_fnc' : self.event_manager.add_event,
            'clear_events_fnc' : self.event_manager.clear_events,
            'get_events_fnc' : self.event_manager.get_events,
            # ECS
            'FNC_GET_ENTITY_ID' : self.ecs_manager.get_entity_id,
            # Sound and Music
            'FNC_PLAY_SOUND' : self.sound_manager.play_sound
        })

        self._quests = {}

        # Quest loader managing creting of new quest from json/yaml file and creation
        # of the game objects
        self.quest_loader = QuestLoader(
            gui_manager=self.gui_manager,
            process_fncs=[
                ['prereqs', None],
                ['cleanup/processors', self.ecs_manager.delete_processor],
                ['cleanup/maps', self.map_manager.delete_map],
                ['cleanup/templates', self.ecs_manager.delete_template],
                ['cleanup/entities', self.ecs_manager.delete_entity],
                ['cleanup/dialogs', self.dialog_manager.delete_dialog],
                ['cleanup/handlers', self.event_manager.delete_handler],
                ['processors', self.ecs_manager.load_processor],
                ['maps', self.map_manager.add_map],
                ['dialogs', self.dialog_manager.add_dialog],
                ['templates', self.ecs_manager.load_template],
                ['entities', self.ecs_manager.create_entity],
                ['handlers', self.event_manager.load_handler]
            ]
        )

        logger.info(f'Game initiated')


    def _clear_game(self) -> None:
        '''Clear all game related resources'''

        self.map_manager.clear_maps()
        self.dialog_manager.clear_dialogs()
        self.message_manager.clear_messages()
        self.command_manager.clear_commands()
        self.event_manager.clear_events()
        self.ecs_manager.clear_ecs()
        self.script_manager.clear_scripts()

        self.clear_quests()

        logger.info(f'All game resources cleared.')

    def new_game(self, filepath: str, clear_before_load: bool=True, show_progress: bool=True) -> None:

        logger.debug(f'Loading quest "{filepath}".')

        if clear_before_load:
            # Clear everything
            self._clear_game()

        # Add new quest
        quest = self.quest_loader.load_quest_from_file(filepath=filepath)
        self._quests.update({quest.alias : quest})

        # Trigger the event
        self.event_manager.add_event(Event('QUEST_START', self, None, params={'quest_id': quest.alias}))

        logger.info(f'Quest "{filepath}" successfully loaded.')

    def delete_quest(self, quest_name: str) -> None:
        '''Deletes quests from the game'''

        del self._quests[quest_name]
        logger.info(f'Quest "{quest_name}" was deleted.')

    def clear_quests(self) -> None:
        ''' Clears all the loaded quests.'''

        quests = list(self._quests.keys()).copy()

        for quest_name in quests:
            self.delete_quest(quest_name)

        logger.info(f'Quests cleared.')


    def exit_game(self) -> None:
        self._clear_game()

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
