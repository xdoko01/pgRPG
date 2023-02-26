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

from pyrpg.functions import get_dict_from_file
from pathlib import Path
from pyrpg.core.config.paths import QUEST_PATH
from pyrpg.core.events.event import Event

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
        #self.script_manager = ScriptManager(alias_to_entity_dict=self.ecs_manager._alias_to_entity) #!!! new parameter added TEST
        self.script_manager = ScriptManager(alias_to_entity_dict_fnc=self.ecs_manager.get_alias_to_entity_dict)
        
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

        self._quests = {}

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

        logger.debug(f'Loading quest "{filepath}".')

        logger.debug(f'ECSManager Info Dump - BEFORE LOAD\n{self.ecs_manager}')

        if show_progress:
            # Get the progress bar ready for new game
            self.progress_bar.update(progress=0, total=0, header="LOADING", text='', finished=False)
            
            # Thread with displaying of the progress bar
            t = Thread(target=self.progress_bar.run)
            t.start()

        if clear_before_load:
            # Clear everything
            self._clear_game(progress=self.progress_bar.update)
            logger.debug(f'ECSManager Info Dump - AFTER CLEARING\n{self.ecs_manager}')


        #add new quest
        self.add_quest(quest_filepath=filepath)

        if show_progress:
            # End the progress bar
            self.progress_bar.update(finished=True)

        logger.debug(f'ECSManager Info Dump - AFTER LOAD\n{self.ecs_manager}')

        logger.info(f'Quest "{filepath}" successfully loaded.')

    def add_quest(self, quest_filepath: str) -> str:
        '''Adds new quest to the game'''
        
        # Read the quest prescription
        quest_data = get_dict_from_file(filepath=Path(quest_filepath), dir=QUEST_PATH)

        # Check that the quest is not yet loaded
        quest_id = quest_data["id"]
        assert quest_id not in self._quests.keys()

        # Translate quest data into the game objects
        self.process_quest_data(quest_data)
        
        # Update the dict with loaded quests
        self._quests.update({quest_id : quest_data})
        logger.info(f'Quest "{quest_id}" was added to the game.')

    def process_quest_data(self, quest_data):
        '''Loads the quest data into the game data structures of individual managers'''

        quest_id = quest_data["id"]

        #####
        # PRE-LOAD prerequisity quests
        #####

        # Load prerequisity quests
        for prereq_quest_filepath in quest_data.get("prereqs", []):

            logger.info(f'Start of processing prereq "{prereq_quest_filepath}".')
            self.add_quest(prereq_quest_filepath)

        logger.info(f'Load of prerequisities has finished.')

        #####
        # PRE-LOAD cleanup
        #####

        logger.info(f'Starting cleanup for quest "{quest_id}".')

        self._cleanup_processors(processors_data=quest_data.get("cleanup", {}).get("processors", []))
        self._cleanup_templates(templates_data=quest_data.get("cleanup", {}).get("templates", []))
        self._cleanup_entities(entities_data=quest_data.get("cleanup", {}).get("entities", []))
        self._cleanup_maps(maps_data=quest_data.get("cleanup", {}).get("maps", []))
        self._cleanup_dialogs(dialogs_data=quest_data.get("cleanup", {}).get("dialogs", []))
        self._cleanup_handlers(handlers_data=quest_data.get("cleanup", {}).get("handlers", []))

        logger.info(f'Cleanup for quest "{quest_id}" has finished.')

        #####
        # LOAD
        #####

        logger.info(f'Starting loading objects for quest "{quest_id}".')

        self._load_processors(processors_data=quest_data.get("processors", []))
        self._load_maps(maps_data=quest_data.get("maps", []))
        self._load_dialogs(dialogs_data=quest_data.get("dialogs", []))
        self._load_templates(templates_data=quest_data.get("templates", []))
        self._load_entities(entities_data=quest_data.get("entities", []))
        self._load_handlers(handlers_data=quest_data.get("event_handlers", {}))

        logger.info(f'Loading objects for quest "{quest_id}" has finished.')

        # Report that quest was loaded - generate event
        self.event_manager.add_event(Event('QUEST_START', self, None, params={'quest_id' : quest_id}))

    def _cleanup_processors(self, processors_data: list):
        '''Deletes all processors from processors_data'''

        self.progress_bar.update(text='Cleaning Processors', progress=0, total=len(processors_data))

        logger.debug(f'No. of processors to clean: {len(processors_data)}')

        try:
            for n, processor in enumerate(processors_data):
                self.ecs_manager.delete_processor(processor)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of processors "{processor}".')
            raise ValueError(f'Problem during cleaning of processors.')

    def _cleanup_templates(self, templates_data: list):
        '''Deletes all templates from templates_data'''

        self.progress_bar.update(text='Cleaning Templates', progress=0, total=len(templates_data))

        logger.debug(f'No. of templates to clean: {len(templates_data)}')

        try:
            for n, template in enumerate(templates_data):
                self.ecs_manager.delete_template(template)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of templates "{template}".')
            raise ValueError(f'Problem during cleaning of templates.')

    def _cleanup_entities(self, entities_data: list):
        '''Deletes all entities from entities_data'''

        self.progress_bar.update(text='Cleaning Entities', progress=0, total=len(entities_data))

        logger.debug(f'No. of entities to clean: {len(entities_data)}')

        try:
            for n, entity_name in enumerate(entities_data):
                self.ecs_manager.delete_entity(entity_alias=entity_name)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of entities "{entity_name}".')
            raise ValueError(f'Problem during cleaning of entities.')

    def _cleanup_maps(self, maps_data: list):
        '''Deletes all maps from maps_data'''

        self.progress_bar.update(text='Cleaning Maps', progress=0, total=len(maps_data))

        logger.debug(f'No. of maps to clean: {len(maps_data)}')

        try:
            for n, map in enumerate(maps_data):
                self.map_manager.delete_map(map)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of maps "{map}".')
            raise ValueError(f'Problem during cleaning of maps.')

    def _cleanup_dialogs(self, dialogs_data: list):
        '''Deletes all dialogs from dialogs_data'''

        self.progress_bar.update(text='Cleaning Dialogs', progress=0, total=len(dialogs_data))

        logger.debug(f'No. of dialogs to clean: {len(dialogs_data)}')

        try:
            for n, dialog in enumerate(dialogs_data):
                self.dialog_manager.delete_dialog(dialog)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of dialog "{dialog}".')
            raise ValueError(f'Problem during cleaning of dialogs.')

    def _cleanup_handlers(self, handlers_data: list):
        '''Deletes all handlers from handlers_data'''

        self.progress_bar.update(text='Cleaning Handlers', progress=0, total=len(handlers_data))

        logger.debug(f'No. of handlers to clean: {len(handlers_data)}')

        try:
            for n, handler in enumerate(handlers_data):
                self.event_manager.delete_handler(handler)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of handler "{handler}".')
            raise ValueError(f'Problem during cleaning of handlers.')

    def _load_processors(self, processors_data: list):
        '''Loads all processors from processors_data'''

        self.progress_bar.update(text='Loading Processors', progress=0, total=len(processors_data))

        logger.debug(f'No. of processors to load: {len(processors_data)}')

        try:
            for n, processor in enumerate(processors_data):
                self.ecs_manager.load_processor(processor)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during loading of processor "{processor}".')
            raise ValueError(f'Problem during loading of processors.')

    def _load_maps(self, maps_data: list):
        '''Loads all maps from maps_data'''

        self.progress_bar.update(text='Loading Maps', progress=0, total=len(maps_data))

        logger.debug(f'No. of maps to load: {len(maps_data)}')

        try:
            for n, map in enumerate(maps_data):
                self.map_manager.add_map(map)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during loading of map "{map}".')
            raise ValueError(f'Problem during loading of maps.')

    def _load_dialogs(self, dialogs_data: list):
        '''Loads all dialogs from dialogs_data'''

        self.progress_bar.update(text='Loading Dialogs', progress=0, total=len(dialogs_data))

        logger.debug(f'No. of dialogs to load: {len(dialogs_data)}')

        try:
            for n, dialog in enumerate(dialogs_data):
                self.dialog_manager.add_dialog(dialog)
                self.progress_bar.update(progress=n+1)
        except ValueError:
            logger.error(f'Problem during loading of dialog "{dialog}".')
            raise ValueError(f'Problem during loading of dialogs.')

    def _load_templates(self, templates_data: list):
        '''Loads all templates from templates_data'''

        self.progress_bar.update(text='Loading Entity Templates', progress=0, total=len(templates_data))

        logger.debug(f'No. of templates to load: {len(templates_data)}')

        try:
            for n, template in enumerate(templates_data):
                self.ecs_manager.store_template_definition(template, template['id'])
                self.progress_bar.update(progress=n+1)
        except KeyError:
            raise ValueError(f'Template definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during loading of templates.')
            raise ValueError(f'Problem during loading of templates.')

    def _create_empty_entities(self, entities_data: list):
        '''Extract all aliases for the entities and create them as an empty and
        registered in lookup tables in ecs_manager.
        '''

        self.progress_bar.update(text='Loading Entities - Registration', progress=0, total=len(entities_data))

        try:
            for n, entity in enumerate(entities_data):
                # Only create new empty entity if alias not yet exists.
                if not self.ecs_manager.get_entity_id(entity['id']):
                    self.ecs_manager.create_empty_entity(entity_alias=entity['id'])
                self.progress_bar.update(progress=n+1)
        except KeyError:
            raise ValueError(f'Entity definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during creating of empty entities.')
            raise ValueError(f'Problem during creating of empty entities.')

    def _update_entities(self, entities_data: list):
        '''Stores every entity definition in ecs_manager.
        '''

        self.progress_bar.update(text='Loading Entities - Components Update', progress=0, total=len(entities_data))

        try:
            for n, entity in enumerate(entities_data):
                entity_id = self.ecs_manager.get_entity_id(entity_alias=entity['id'])
                self.ecs_manager.update_entity(entity, entity_id)
                self.progress_bar.update(progress=n+1)
        except KeyError:
            raise ValueError(f'Entity definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during storing of components for entities.')
            raise ValueError(f'Problem during storing of components for entities.')

    def _load_entities(self, entities_data: list):
        '''Loads all entities from entities_data'''

        logger.debug(f'No. of entities to load: {len(entities_data)}')

        try:
            self._create_empty_entities(entities_data=entities_data)
            self._update_entities(entities_data=entities_data)
        except ValueError:
            logger.error(f'Problem during loading of entities.')
            raise ValueError(f'Problem during loading of entities.')

    def _load_handlers(self, handlers_data: dict):
        '''Loads all handlers from handlers_data '''

        self.progress_bar.update(text='Loading Handlers', progress=0, total=1)

        logger.debug(f'No. of events that have defined handler: {len(handlers_data.values())}')

        for event_type in handlers_data:
            for handler_data in handlers_data[event_type]:
                self.event_manager.load_handler(event_type=event_type, handler_data=handler_data)

        self.progress_bar.update(progress=1)  



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
