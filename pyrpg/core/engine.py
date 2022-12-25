''' core.engine_3ex module
'''

import logging

# Create logger
logger = logging.getLogger(__name__)

import pygame # for pygame.QUIT, pygame.KEYDOWN
import pyrpg.core.config.keys as keys

from threading import Thread

from pyrpg.core.config.states import State
from pyrpg.core.managers.gui_manager import GUIManager
from pyrpg.core.managers.sound_manager import SoundManager

from pyrpg.core.managers.map_manager import MapManager
from pyrpg.core.managers.message_manager import MessageManager
from pyrpg.core.managers.dialog_manager import DialogManager
from pyrpg.core.managers.command_manager import CommandManager
from pyrpg.core.managers.quest_manager import QuestManager
from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.managers.event_manager import EventManager
from pyrpg.core.managers.script_manager import ScriptManager

logger.info(f'Engine initiated')

class Game:

    def __init__(self, gui_manager: GUIManager, sound_manager: SoundManager, progress_bar, timed: bool=False) -> None:

        self.gui_manager = gui_manager # for drawing anything on the screen
        self.sound_manager = sound_manager # for playing music and sounds

        self.map_manager = MapManager()
        self.message_manager = MessageManager()
        self.dialog_manager = DialogManager()
        self.command_manager = CommandManager() # command manager must have reference to Game in order commands can manipulate the game world
        self.quest_manager = QuestManager()
        self.ecs_manager = ECSManager()
        self.script_manager = ScriptManager(alias_to_entity_dict=self.ecs_manager._alias_to_entity) #!!! new parameter added

        # Class representing the progress bar
        self.progress_bar = progress_bar
        
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
        logger.info(f'Game initiated')


    def _clear_game(self, progress) -> None:
        '''Clear all game related resources'''

        # Init the cleaning progress
        self.progress_bar.update(total=8, text='Clearing resources')

        self.map_manager.clear_maps()
        self.progress_bar.update(progress=1)

        self.dialog_manager.clear_dialogs()
        self.progress_bar.update(progress=2)

        self.message_manager.clear_messages()
        self.progress_bar.update(progress=3)

        self.command_manager.clear_commands()
        self.progress_bar.update(progress=4)

        self.event_manager.clear_events()
        self.progress_bar.update(progress=5)

        self.quest_manager.clear_quests()
        self.progress_bar.update(progress=6)

        self.ecs_manager.clear_ecs()
        self.progress_bar.update(progress=7)

        self.script_manager.clear_scripts()
        self.progress_bar.update(progress=8)

        logger.info(f'All game resources cleared.')

    def new_game(self, filepath: str, clear_before_load: bool=True, show_progress: bool=True) -> None:

        if show_progress:
            # Get the progress bar ready for new game
            self.progress_bar.update(progress=0, total=0, header="LOADING", text='', finished=False)
            
            # Thread with displaying of the progress bar
            t = Thread(target=self.progress_bar.run)
            t.start()

        if clear_before_load:
            # Clear everything
            self._clear_game(progress=self.progress_bar.update)

        #add new quest
        self.quest_manager.add_quest(
            progress_fnc=self.progress_bar.update,
            quest_filepath=filepath,
            map_mng=self.map_manager,
            dialog_mng=self.dialog_manager,
            event_mng=self.event_manager,
            ecs_mng=self.ecs_manager)

        if show_progress:
            # End the progress bar
            self.progress_bar.update(finished=True)

        logger.info(f'Quest "{filepath}" successfully loaded.')

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
