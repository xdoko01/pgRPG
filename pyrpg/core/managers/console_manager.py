""" Initiates and manipulates game console.
"""

'''
# Initiate logging
import logging
logger = logging.getLogger(__name__)

# Reference to program module that will be called from within the console
from importlib import import_module

console = None

def init():

    global console

    # Get the console class
    from pyrpg.utils import Console
    #from pyrpg.core.config.console import CONSOLE_CONFIG, CONSOLE_CLI_MODULE
    #from pyrpg.core.config.display import DISPLAY_WIDTH
    #from pyrpg.core.config.lua import LUA_RUNTIME
    from pyrpg.core.config.console import CONSOLE
    from pyrpg.core.config.display import DISPLAY

    # Load the console from utils
    console = Console(
        app=import_module(CONSOLE["CLI_MODULE"]),
        lua_runtime=None,
        width=DISPLAY["RESOLUTION"].width,
        config=CONSOLE
    )
    logger.info(f"Console initiated.")

def reload():
    if not console: return


    from pyrpg.core.config.console import CONSOLE
    from pyrpg.core.config.display import DISPLAY

    console.set_cli_module(CONSOLE["CLI_MODULE"]) # to be implemented
    console.set_width(DISPLAY["RESOLUTION"].width) # 
    
def write(text):
    """ Mandatory function used (not only) by the logger handler to write 
    directly onto the game console.
    """
    if console: console.write(text)

'''