from importlib import import_module
from .paths import IMAGE_PATH, FONT_PATH, CONSOLE_SCRIPT_PATH
from .config import CONSOLE as CONSOLE_CONFIG

# Fix the relative paths so that they are directing into correct folders
if CONSOLE_CONFIG.get('global').get('bck_image', None):
    CONSOLE_CONFIG.get('global').update({'bck_image' : IMAGE_PATH / CONSOLE_CONFIG.get('global').get('bck_image')})

if CONSOLE_CONFIG.get('header').get('bck_image', None):
    CONSOLE_CONFIG.get('header').update({'bck_image' : IMAGE_PATH / CONSOLE_CONFIG.get('header').get('bck_image')})

if CONSOLE_CONFIG.get('footer').get('bck_image', None):
    CONSOLE_CONFIG.get('footer').update({'bck_image' : IMAGE_PATH / CONSOLE_CONFIG.get('footer').get('bck_image')})

if CONSOLE_CONFIG.get('header').get('font_file', None):
    CONSOLE_CONFIG.get('header').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('header').get('font_file')})

if CONSOLE_CONFIG.get('output').get('font_file', None):
    CONSOLE_CONFIG.get('output').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('output').get('font_file')})

if CONSOLE_CONFIG.get('input').get('font_file', None):
    CONSOLE_CONFIG.get('input').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('input').get('font_file')})

if CONSOLE_CONFIG.get('footer').get('font_file', None):
    CONSOLE_CONFIG.get('footer').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('footer').get('font_file')})

# Add console_script_path to the console config
CONSOLE_CONFIG.get('global').update({'script_path' : CONSOLE_SCRIPT_PATH})

# Reference to program module that will be called from within the console
CONSOLE_CLI_MODULE = import_module(CONSOLE_CONFIG.get('global').get('cli_module', 'pyrpg.core.engine'))

"""
import pyrpg.core.config.paths as paths # for font path used in console
import pyrpg.core.config.config as cfg  # for console configuration stored in CONSOLE dict
import pyrpg.utils as utils # for Console class
import importlib # for passing module name to COnsole as a string from config file
from pyrpg.core.engine import window # for window get width - TODO - isnt it possible to get that from config?
from pyrpg.core.lua import lua_runtime # for lua functionality in console

########################################################
### Update Console Config Paths
########################################################
 
# Global background image
if cfg.CONSOLE.get('global').get('bck_image', None):
    cfg.CONSOLE.get('global').update({'bck_image' : paths.IMAGE_PATH / cfg.CONSOLE.get('global').get('bck_image')})

# Header background image
if cfg.CONSOLE.get('header').get('bck_image', None):
    cfg.CONSOLE.get('header').update({'bck_image' : paths.IMAGE_PATH / cfg.CONSOLE.get('header').get('bck_image')})

# Footer background image
if cfg.CONSOLE.get('footer').get('bck_image', None):
    cfg.CONSOLE.get('footer').update({'bck_image' : paths.IMAGE_PATH / cfg.CONSOLE.get('footer').get('bck_image')})

# Header font file
if cfg.CONSOLE.get('header').get('font_file', None):
    cfg.CONSOLE.get('header').update({'font_file' : paths.FONT_PATH / cfg.CONSOLE.get('header').get('font_file')})

# Output font file
if cfg.CONSOLE.get('output').get('font_file', None):
    cfg.CONSOLE.get('output').update({'font_file' : paths.FONT_PATH / cfg.CONSOLE.get('output').get('font_file')})

# Input font file
if cfg.CONSOLE.get('input').get('font_file', None):
    cfg.CONSOLE.get('input').update({'font_file' : paths.FONT_PATH / cfg.CONSOLE.get('input').get('font_file')})

# Footer font file
if cfg.CONSOLE.get('footer').get('font_file', None):
    cfg.CONSOLE.get('footer').update({'font_file' : paths.FONT_PATH / cfg.CONSOLE.get('footer').get('font_file')})

# Add console_script_path to the console config
cfg.CONSOLE.get('global').update({'script_path' : paths.CONSOLE_SCRIPT_PATH})

# Initiate console
game_console = utils.Console(
            importlib.import_module(cfg.CONSOLE.get('global').get('cli_module', 'pyrpg.core.engine')),
            lua_runtime,
            window.get_width(),
            cfg.CONSOLE
        )


def write(text):
    ''' Mandatory function used (not only) by the logger handler to write 
    directly onto the game console.
    '''
    game_console.write(text)
"""