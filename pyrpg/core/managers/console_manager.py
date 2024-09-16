""" Initiates and manipulates game console.
"""

# Initiate logging
import logging
logger = logging.getLogger(__name__)

console = None

def init():

    global console

    # Get the console class
    from pyrpg.utils import Console
    #from pyrpg.core.config.console import CONSOLE_CONFIG, CONSOLE_CLI_MODULE
    from pyrpg.core.config.console import CONSOLE
    from pyrpg.core.config.display import DISPLAY
    #from pyrpg.core.config.display import DISPLAY_WIDTH
    #from pyrpg.core.config.lua import LUA_RUNTIME

    # Load the console from utils
    console = Console(
        app=CONSOLE["CLI_MODULE"],
        lua_runtime=None,
        width=DISPLAY["WIDTH"],
        config=CONSOLE
    )
    logger.info(f"Console initiated.")

def write(text):
    """ Mandatory function used (not only) by the logger handler to write 
    directly onto the game console.
    """
    if console: console.write(text)
