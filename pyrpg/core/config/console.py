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

import pprint
pprint.pprint(cfg.CONSOLE)

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