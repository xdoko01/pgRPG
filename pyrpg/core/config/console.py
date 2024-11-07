# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import CONSOLE

###
# Reference to program module that will be called from within the console
###

from pyrpg.utils import Console
from pyrpg.core.config.display import DISPLAY

# Load the console from utils
console = Console(
    #app=import_module(CONSOLE["CLI_MODULE"]), #Carefull this triggers import of the module!!!
    app=None, # set the main module as entry point to the console
    lua_runtime=None,
    width=DISPLAY["RESOLUTION"].width,
    config=CONSOLE
)
logger.info(f"Console initiated.")



'''
_INIT: bool = False

def get_init() -> bool:
    """Return True, if console config is already initiated.
    """
    return _INIT

def init() -> None:
    """Prepare the config data.
    """
    # Do not run init more than once
    if get_init(): return

    from pyrpg.core.config import FILEPATHS # for IMAGE_PATH, FONT_PATH, CONSOLE_SCRIPT_PATH

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

    from pyrpg.utils import Console
    from pyrpg.core.config.display import DISPLAY

    global console
    # Load the console from utils
    console = Console(
        #app=import_module(CONSOLE["CLI_MODULE"]), #Carefull this triggers import of the module!!!
        app=None, # set the main module as entry point to the console
        lua_runtime=None,
        width=DISPLAY["RESOLUTION"].width,
        config=CONSOLE
    )
    logger.info(f"Console initiated.")

    global _INIT
    _INIT = True
'''

def init_cli_module():

    try:
        import sys
        console.set_cli_app(app=sys.modules[CONSOLE["CLI_MODULE"]]) # must be called after the cli module is imported
    except KeyError:
        logger.info(f"{CONSOLE["CLI_MODULE"]} not yet imported. No console CLI module loaded.")

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
