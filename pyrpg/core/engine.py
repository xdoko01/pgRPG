""" core.engine module
"""

import logging

# Create logger
logger = logging.getLogger(__name__)

import pygame # for pygame.QUIT, pygame.KEYDOWN
from pyrpg.core.config.keys import KEYS

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
from pyrpg.core.managers.pathfind_manager import PathfindManager

from pyrpg.core.menus.progress_bar2 import ProgressBar2

from pyrpg.core.config.filepaths import SCENE_PATH, Path # for SCENE_PATH
from pyrpg.core.events.event import Event
from pyrpg.functions import get_dict_from_file, get_coll_value


logger.info(f"Engine initiated")

class Scene:
    def __init__(self, alias: str, scene_def: dict) -> None:
        self.filepath: str = None
        self.id, self.alias = alias, alias
        self.title = scene_def.get("title")
        self.description = scene_def.get("description")
        self.objective = scene_def.get("objective")
        self.stats = {
            "no_of_prereqs": len(scene_def.get("prereqs", [])),
            "no_of_procs": len(scene_def.get("processors", [])),
            "no_of_maps": len(scene_def.get("maps", [])),
            "no_of_dlgs": len(scene_def.get("dialogs", [])),
            "no_of_temps": len(scene_def.get("templates", [])),
            "no_of_ents": len(scene_def.get("entities", [])),
            "no_of_handlers": len(scene_def.get("handlers", [])),
            "no_of_comps": {e.get("id"): len(e.get("components", [])) for e in scene_def.get("entities", [])}
        }

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
        self.pathfind_manager = PathfindManager()
        
        # Reference function for adding events
        # TODO - maybe it would be better to handle processing of events within processor that
        # would receive list of events and handle event function and using those would implement
        # event processing.
        self.event_manager = EventManager(self.script_manager.execute_event_actions)

        self.ecs_manager.initialize(timed=timed, game_functions={
            "window" : self.gui_manager.window,
            "create_entity_fnc" : self.ecs_manager.create_entity,
            "remove_entity_fnc" : self.ecs_manager.delete_entity,
            #"ammo_pack_event_queue" : event_queue,
            "maps" : self.map_manager._maps,
            #"input_command_queue" : self.command_manager.add_command,
            "teleport_event_queue" : self.event_manager.add_event,
            "weapon_event_queue" : self.event_manager.add_event,
            "ammo_pack_event_queue" : self.event_manager.add_event,
            "wearable_event_queue" : self.event_manager.add_event,
            "item_pickup_event_queue" : self.event_manager.add_event,
            "entity_coll_event_queue" : self.event_manager.add_event,
            "game_event_handler" : self.event_manager.process_events,
            "game_messages" : self.message_manager.get_messages,
            "add_message" : self.message_manager.add_message,
            "damage_event_queue" : self.event_manager.add_event,
            "destroy_event_queue" : self.event_manager.add_event,
            "score_event_queue" : self.event_manager.add_event,
            # Maps
            "FNC_GET_MAP": self.map_manager.get_map,
            # Commands
            "FNC_ADD_COMMAND" : self.command_manager.add_command,
            "FNC_CLEAR_COMMANDS" : self.command_manager.clear_command_queue,
            "FNC_GET_COMMANDS" : self.command_manager.get_command_queue,
            "FNC_PROCESS_COMMANDS" : self.command_manager.process_commands,
            "FNC_EXEC_CMD_INIT" : self.command_manager.execute_command_init, # for do_parallel command
            "FNC_EXEC_CMD" : self.command_manager.execute_command, # for do_parallel command

            # Paths
            "FNC_CALC_PATHS": self.pathfind_manager.continue_pathfinding,
            "FNC_REQUEST_PATHFIND": self.pathfind_manager.request_path,
            "FNC_GET_PATH": self.pathfind_manager.get_path,
            # Events
            "FNC_ADD_EVENT" : self.event_manager.add_event,
            "add_event_fnc" : self.event_manager.add_event,
            "clear_events_fnc" : self.event_manager.clear_events,
            "get_events_fnc" : self.event_manager.get_events,
            # ECS
            "FNC_GET_ENTITY_ID" : self.ecs_manager.get_entity_id,
            "REF_ECS_MNG": self.ecs_manager,
            # Sound and Music
            "FNC_PLAY_SOUND" : self.sound_manager.play_sound
        })

        self._scenes = {}

        # Scene loader managing creting of new scene from json/yaml file and creation
        # of the game objects
        self.load_scene_def_fncs = [
            ["prereqs", self.load_scene_from_file],
            ["cleanup/processors", self.ecs_manager.delete_processor],
            ["cleanup/maps", self.map_manager.delete_map],
            ["cleanup/templates", self.ecs_manager.delete_template],
            ["cleanup/entities", self.ecs_manager.delete_entity],
            ["cleanup/dialogs", self.dialog_manager.delete_dialog],
            ["cleanup/handlers", self.event_manager.delete_handler],
            ["processors", self.ecs_manager.load_processor],
            ["maps", self.map_manager.load_map],
            ["dialogs", self.dialog_manager.load_dialog],
            ["templates", self.ecs_manager.load_template],
            ["entities", self.ecs_manager.load_register_empty_entity], # first register all entities
            ["entities", self.ecs_manager.load_update_empty_entity], # next fill them in order to be able to use aliases everywhere
            ["entities/components/params/handlers", self.event_manager.load_handler], # look for handlers in the parameters of components
            ["handlers", self.event_manager.load_handler]
        ]

        logger.info(f"Game initiated")

    def load_scene_from_file(self, filepath: str) -> Scene:
        """Reads file with the scene, translates it to scene definition
        and processes scene definition into game world objects.
        
        Parameters:
            :param filepath: Absolute or relative path to the file containing
                             scene definition (JSON/YAML/other).
            :type filepath: str

            :returns: Scene object with basic scene information
        """

        # Read the scene definition from a file
        scene_def = get_dict_from_file(filepath=Path(filepath), dir=SCENE_PATH)

        # Translate scene definition into the game objects
        scene = self.load_scene_from_def(scene_def)

        # Remember the path
        scene.filepath = filepath

        # Return the scene objects containing usefull information
        return scene

    def load_scene_from_def(self, scene_def: dict) -> Scene:
        """Translates the scene definition into the objects representing the
        game world - entities, components, maps, dialogs, handlers, etc.

        Parameters:
            :param scene_def: Dictionary containing all information about the
                              scene.
            :type scene_def: dict

            :returns: Scene object with basic scene information
        """

        scene = Scene(alias=scene_def["id"], scene_def=scene_def)

        logger.info(f"Loading objects for scene {scene.alias} has started.")

        # Search every defined location in the scene_def and try to process
        # it using the given functions for processing.
        for data_path, process_fnc in self.load_scene_def_fncs:

            # Get the data on the path to be processed
            data_to_process = get_coll_value(coll=scene_def, path=data_path, sep="/") # generator

            logger.info(f'Start of processing of "{data_path}" for scene "{scene.alias}".')

            # Cycle this data and process them using progress bar
            with ProgressBar2(gui_manager=self.gui_manager, header="Loading", text=data_path) as progress:
                for item in progress(data_to_process):
                    logger.debug(f'About to process following item "{item}" using function "{process_fnc}".')
                    process_fnc(item)

            logger.info(f'End of processing of "{data_path}" for scene "{scene.alias}".')
        
        logger.info(f'Loading objects for scene "{scene.alias}" has finished.')

        return scene

    def new_game(self, filepath: str, clear_before_load: bool=True, show_progress: bool=True) -> None:
        """Loads new game from the scene"""

        logger.debug(f'Loading scene "{filepath}".')

        # Delete every game object
        if clear_before_load: self._clear_game()

        # Load the scene, register it and create QUEST_START event
        scene = self.load_scene_from_file(filepath=filepath)
        self._scenes[scene.alias] = scene
        self.event_manager.add_event(
            Event("QUEST_START", 
            self, 
            None, 
            params={
                "filepath": scene.filepath,
                "id": scene.id,
                "alias": scene.alias,
                "title": scene.title,
                "description": scene.description,
                "objective": scene.objective,
                "stats": scene.stats
            })
        )

        logger.info(f'Scene "{filepath}" successfully loaded.')

    def _clear_game(self) -> None:
        """Clear all game related resources"""

        self.map_manager.clear_maps()
        self.dialog_manager.clear_dialogs()
        self.message_manager.clear_messages()
        self.command_manager.clear_command_queue()
        self.event_manager.clear_events()
        self.ecs_manager.clear_ecs()
        self.script_manager.clear_scripts()

        self.clear_scenes()

        logger.info(f"All game resources cleared.")

    def delete_scene(self, scene_name: str) -> None:
        """Deletes scenes from the game"""

        del self._scenes[scene_name]
        logger.info(f'Scene "{scene_name}" was deleted.')

    def clear_scenes(self) -> None:
        """ Clears all the loaded scenes."""

        for scene_name in self._scenes.copy().keys():
            self.delete_scene(scene_name)

        logger.info(f"Quests cleared.")


    def exit_game(self) -> None:
        self._clear_game()

    def run(self, key_events, key_pressed, dt, debug: bool=False) -> State:
        # Check for End Game
        for event in key_events:
            if event.type == pygame.QUIT:
                logger.info(f"Exiting the game")
                return State.EXIT_GAME_DIALOG
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    #self.gui_manager.save_screen()
                    logger.info(f"Leaving to main menu")
                    return State.MAIN_MENU
                elif event.key == KEYS["K_SAVE_GAME"]:
                    pass
                elif event.key == KEYS["K_LOAD_GAME"]:
                    pass

        # maps and scenes added in order that command can be informed about scene to change the phase
        self.ecs_manager.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)

        return State.GAME
