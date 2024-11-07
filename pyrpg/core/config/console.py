
# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import cons

def write(text):
    """ Mandatory function used (not only) by the logger handler to write 
    directly onto the game console.

    Link is specified in the logger configuration
    """
    if cons: cons.write(text)


"""
Functions that feed the console with header and footer data.
"""
from pyrpg.core.config import MAIN_GAME_MODULE

# Get process object to determine info about python process (mem usage etc.)
import os, psutil
python_process = psutil.Process(os.getpid())

def cons_get_info_header():
    '''Returns info that is displayed in the console's header'''

    memory_use = python_process.memory_info()[0]/2.**30  # memory use in GB...I think
    game_state = MAIN_GAME_MODULE.state_manager.game_state #if main else 'N/A'
    no_of_entities =  len(MAIN_GAME_MODULE.engine.ecs_manager._world._entities) if MAIN_GAME_MODULE.engine else 'N/A'

    return f'Memory usage: {memory_use} GB | game state: {str(game_state)} | ECS entities: {no_of_entities}'

def cons_get_info_footer():
    '''Returns info that is displayed in the console's footer'''

    loaded_quests = MAIN_GAME_MODULE.engine._scenes.keys() if MAIN_GAME_MODULE.engine else 'N/A'

    return f'Loaded scenes: {loaded_quests}'