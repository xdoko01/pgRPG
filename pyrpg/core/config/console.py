# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import FILEPATHS # for IMAGE_PATH, FONT_PATH, CONSOLE_SCRIPT_PATH
from pyrpg.core.config import CONSOLE

def init() -> None:
    """Prepare the config data.
    """
    # Fix the relative paths so that they are directing into correct folders
    if CONSOLE.get('global', {}).get('bck_image', None): CONSOLE.get('global').update({'bck_image' : FILEPATHS["IMAGE_PATH"] / CONSOLE.get('global').get('bck_image')})
    if CONSOLE.get('header', {}).get('bck_image', None): CONSOLE.get('header').update({'bck_image' : FILEPATHS["IMAGE_PATH"] / CONSOLE.get('header').get('bck_image')})
    if CONSOLE.get('footer', {}).get('bck_image', None): CONSOLE.get('footer').update({'bck_image' : FILEPATHS["IMAGE_PATH"] / CONSOLE.get('footer').get('bck_image')})
    if CONSOLE.get('header', {}).get('font_file', None): CONSOLE.get('header').update({'font_file' : FILEPATHS["FONT_PATH"] / CONSOLE.get('header').get('font_file')})
    if CONSOLE.get('output', {}).get('font_file', None): CONSOLE.get('output').update({'font_file' : FILEPATHS["FONT_PATH"] / CONSOLE.get('output').get('font_file')})
    if CONSOLE.get('input', {}).get('font_file', None): CONSOLE.get('input').update({'font_file' : FILEPATHS["FONT_PATH"] / CONSOLE.get('input').get('font_file')})
    if CONSOLE.get('footer', {}).get('font_file', None): CONSOLE.get('footer').update({'font_file' : FILEPATHS["FONT_PATH"] / CONSOLE.get('footer').get('font_file')})

    # Add console_script_path to the console config
    CONSOLE.get('global').update({'script_path': FILEPATHS["CONSOLE_SCRIPT_PATH"]})

    # For now just text, reference is created in console manager, during creation of the Console entity
    CONSOLE["CLI_MODULE"] = CONSOLE.get("global").get("cli_module", "pyrpg")

    import pprint
    logger.debug(f"Console config initiated. {pprint.pformat(CONSOLE)}")


def cons_get_info_header(pyrpg_ref) -> str:
    '''Returns info that is displayed in the console's header'''

    memory_use = python_process.memory_info()[0]/2.**30  # memory use in GB...I think
    game_state = pyrpg_ref.state_manager.game_state if main else 'N/A'
    no_of_entities =  len(pyrpg_ref.engine.ecs_manager._world._entities) if main and main.engine else 'N/A'

    return f'memory usage: {memory_use} GB | game state: {str(game_state)} | ECS entities: {no_of_entities}'

def cons_get_info_footer(pyrpg_ref) -> str:
    '''Returns info that is displayed in the console's footer'''

    loaded_quests = pyrpg_ref.engine._quests.keys() if main and main.engine else 'N/A'

    return f'loaded scenes: {loaded_quests}'
    
