"""Scene loading pipeline and manager wiring for the pgrpg engine.

Initializes all managers with a shared ``game_functions`` dict, loads
scenes from JSON/YAML definition files via an ordered pipeline, and
provides cleanup/teardown utilities.

Module Globals:
    _scenes: Dict mapping scene alias to Scene instances.
    _init: Whether ``init()`` has been called.
    load_scene_def_fncs: Ordered list of [data_path, handler_fn] pairs
        driving the scene loading pipeline.
"""

import logging

# Create logger
logger = logging.getLogger(__name__)

import pgrpg.core.config.gui as gui_manager
import pgrpg.core.config.sound as sound_manager

from pgrpg.core.managers import map_manager
from pgrpg.core.managers import message_manager
from pgrpg.core.managers import dialog_manager
from pgrpg.core.managers import command_manager
from pgrpg.core.managers import ecs_manager
from pgrpg.core.managers import event_manager
from pgrpg.core.managers import script_manager
from pgrpg.core.managers import pathfind_manager

from pgrpg.core.config.gui import ProgressBar
from contextlib import nullcontext # for empty progress bar/skipping progress bar

from pgrpg.core.config import FILEPATHS, Path #SCENE_PATH, Path # for SCENE_PATH
from pgrpg.core.events.event import Event
from pgrpg.functions import get_dict_from_file, get_coll_value, get_coll_len



from pgrpg.core.scene import Scene

script_manager.init(alias_to_entity_dict_fnc=ecs_manager.get_alias_to_entity_dict)


# Reference function for adding events
# TODO - maybe it would be better to handle processing of events within processor that
# would receive list of events and handle event function and using those would implement
# event processing.
event_manager.init(exec_event_actions_fnc=script_manager.execute_event_actions)

_scenes = {}
_init: bool = False # is engine initiated?

def get_init() -> bool:
    """Return whether the engine has been initialized."""
    return _init

def init() -> None:
    """Wire all managers together via the game_functions dict and mark engine as initialized."""
    ecs_manager.initialize(game_functions={
        "window": gui_manager.window,
        "create_entity_fnc": ecs_manager.create_entity,
        "remove_entity_fnc": ecs_manager.delete_entity,
        "maps": map_manager._maps,
        "teleport_event_queue": event_manager.add_event,
        "weapon_event_queue": event_manager.add_event,
        "ammo_pack_event_queue": event_manager.add_event,
        "wearable_event_queue": event_manager.add_event,
        "item_pickup_event_queue": event_manager.add_event,
        "entity_coll_event_queue": event_manager.add_event,
        "game_event_handler": event_manager.process_events,
        "game_messages": message_manager.get_messages,
        "add_message": message_manager.add_message,
        "damage_event_queue": event_manager.add_event,
        "destroy_event_queue": event_manager.add_event,
        "score_event_queue": event_manager.add_event,
        # Maps
        "FNC_GET_MAP": map_manager.get_map,
        # Commands
        "FNC_ADD_COMMAND": command_manager.add_command,
        "FNC_CLEAR_COMMANDS": command_manager.clear_command_queue,
        "FNC_GET_COMMANDS": command_manager.get_command_queue,
        "FNC_PROCESS_COMMANDS": command_manager.process_commands,
        "FNC_EXEC_CMD_INIT": command_manager.execute_command_init, # for do_parallel command
        "FNC_EXEC_CMD": command_manager.execute_command, # for do_parallel command

        # Paths
        "FNC_CALC_PATHS": pathfind_manager.continue_pathfinding,
        "FNC_REQUEST_PATHFIND": pathfind_manager.request_path,
        "FNC_GET_PATH": pathfind_manager.get_path,
        # Events
        "FNC_ADD_EVENT": event_manager.add_event,
        "add_event_fnc": event_manager.add_event,
        "clear_events_fnc": event_manager.clear_events,
        "get_events_fnc": event_manager.get_events,
        # ECS
        "FNC_GET_ENTITY_ID": ecs_manager.get_entity_id,
        "REF_ECS_MNG": ecs_manager,
        # Sound and Music
        "FNC_PLAY_SOUND": sound_manager.play_sound
    })

    global _init
    _init = True

    logger.info(f"Game initiated")

def load_scene(scene_file: str, clear_before_load: bool=True, show_progress: bool=True) -> None:
    """Load a scene from file, register it, and emit a SCENE_START event.

    Args:
        scene_file: Path to the scene definition file (relative to SCENE_PATH).
        clear_before_load: If True, clear all game state before loading.
        show_progress: If True, display a progress bar during loading.
    """

    logger.debug(f'Loading scene "{scene_file}".')

    # Delete every game object
    if clear_before_load: _clear_game()

    # Load the scene, register it and create SCENE_START event
    scene = load_scene_from_file(scene_file=scene_file, show_progress=show_progress)
    
    # Register the scene
    _scenes[scene.alias] = scene
    
    # Create an SCENE_START event
    event_manager.add_event(
        Event("SCENE_START", 
        None, 
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

    logger.info(f'Scene "{scene_file}" successfully loaded.')

def load_scene_from_file(scene_file: str, show_progress: bool=False) -> Scene:
    """Read a scene file, translate it to a definition dict, and process it.

    Args:
        scene_file: Absolute or relative path to the scene file (JSON/YAML).
        show_progress: If True, display a progress bar during loading.

    Returns:
        A Scene object populated with basic scene metadata.
    """

    # Read the scene definition from a file
    scene_def = get_dict_from_file(filepath=Path(scene_file), dir=FILEPATHS["SCENE_PATH"])

    # Translate scene definition into the game objects
    scene = load_scene_from_def(scene_def=scene_def, show_progress=show_progress)

    # Remember the path
    scene.filepath = scene_file

    # Return the scene objects containing usefull information
    return scene

# Scene loader managing creting of new scene from json/yaml file and creation
# of the game objects
load_scene_def_fncs = [
    ["prereqs", load_scene_from_file],
    ["cleanup/processors", ecs_manager.delete_processor],
    ["cleanup/maps", map_manager.delete_maps_pattern], # no-pattern version map_manager.delete_map
    ["cleanup/templates", ecs_manager.delete_templates_pattern], # no-pattern version ecs_manager.delete_template
    ["cleanup/entities", ecs_manager.delete_entities_pattern], # no-patern version ecs_manager.delete_entity
    ["cleanup/dialogs", dialog_manager.delete_dialogs_pattern], # no-patern version dialog_manager.delete_dialog
    ["cleanup/handlers", event_manager.delete_handlers_pattern], # no-patern version event_manager.delete_handler
    ["processors", ecs_manager.load_processor],
    ["maps", map_manager.load_map],
    ["dialogs", dialog_manager.load_dialog],
    ["templates", ecs_manager.load_template],
    ["entities", ecs_manager.load_register_empty_entity], # first register all entities
    ["entities", ecs_manager.load_update_empty_entity], # next fill them in order to be able to use aliases everywhere
    ["entities/components/params/handlers", event_manager.load_handler], # look for handlers in the parameters of components
    ["handlers", event_manager.load_handler]
]

def load_scene_from_def(scene_def: dict, show_progress: bool=False) -> Scene:
    """Translate a scene definition dict into game world objects.

    Walks ``load_scene_def_fncs`` in order, extracting data at each path
    and processing items via the paired handler function.

    Args:
        scene_def: Full scene definition dict (from JSON/YAML file).
        show_progress: If True, display a progress bar during loading.

    Returns:
        A Scene object populated with basic scene metadata.
    """

    scene = Scene(alias=scene_def["id"], scene_def=scene_def)

    logger.info(f"Loading objects for scene {scene.alias} has started.")

    # Search every defined location in the scene_def and try to process
    # it using the given functions for processing.
    for data_path, process_fnc in load_scene_def_fncs:

        # Get the data on the path to be processed
        data_to_process = get_coll_value(coll=scene_def, path=data_path, sep="/") # generator

        # Get length of data for processing
        data_to_process_len = get_coll_len(coll=scene_def, path=data_path, sep="/")

        logger.info(f'Start of processing of "{data_path}" for scene "{scene.alias}". Total {data_to_process_len} items.')

        # Cycle this data and process them using progress bar if show_progress is set to True
        with ProgressBar(header="Loading", text=data_path, total=data_to_process_len) if show_progress else nullcontext(lambda x: x) as progress:
            for item in progress(data_to_process):
                logger.debug(f'About to process following item "{item}" using function "{process_fnc}".')
                process_fnc(item)

        logger.info(f'End of processing of "{data_path}" for scene "{scene.alias}". Total {data_to_process_len} items.')

    logger.info(f'Loading objects for scene "{scene.alias}" has finished.')

    return scene


def _clear_game() -> None:
    """Clear all game related resources"""

    map_manager.clear_maps()
    dialog_manager.clear_dialogs()
    message_manager.clear_messages()
    command_manager.clear_command_queue()
    event_manager.clear_events()
    ecs_manager.clear_ecs()
    script_manager.clear_scripts()

    clear_scenes()

    logger.info(f"All game resources cleared.")

def delete_scene(scene_name: str) -> None:
    """Remove a scene from the registry by alias."""

    del _scenes[scene_name]
    logger.info(f'Scene "{scene_name}" was deleted.')

def clear_scenes() -> None:
    """Remove all scenes from the registry."""

    for scene_name in _scenes.copy().keys():
        delete_scene(scene_name)

    logger.info(f"Quests cleared.")

def exit_game() -> None:
    """Clean up all game resources on exit."""
    _clear_game()