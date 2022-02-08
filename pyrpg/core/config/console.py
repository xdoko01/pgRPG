from importlib import import_module
from .paths import IMAGE_PATH, FONT_PATH, CONSOLE_SCRIPT_PATH
from .config import CONSOLE as CONSOLE_CONFIG

# Fix the relative paths so that they are directing into correct folders
if CONSOLE_CONFIG.get('global', {}).get('bck_image', None):
    CONSOLE_CONFIG.get('global').update({'bck_image' : IMAGE_PATH / CONSOLE_CONFIG.get('global').get('bck_image')})

if CONSOLE_CONFIG.get('header', {}).get('bck_image', None):
    CONSOLE_CONFIG.get('header').update({'bck_image' : IMAGE_PATH / CONSOLE_CONFIG.get('header').get('bck_image')})

if CONSOLE_CONFIG.get('footer', {}).get('bck_image', None):
    CONSOLE_CONFIG.get('footer').update({'bck_image' : IMAGE_PATH / CONSOLE_CONFIG.get('footer').get('bck_image')})

if CONSOLE_CONFIG.get('header', {}).get('font_file', None):
    CONSOLE_CONFIG.get('header').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('header').get('font_file')})

if CONSOLE_CONFIG.get('output', {}).get('font_file', None):
    CONSOLE_CONFIG.get('output').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('output').get('font_file')})

if CONSOLE_CONFIG.get('input', {}).get('font_file', None):
    CONSOLE_CONFIG.get('input').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('input').get('font_file')})

if CONSOLE_CONFIG.get('footer', {}).get('font_file', None):
    CONSOLE_CONFIG.get('footer').update({'font_file' : FONT_PATH / CONSOLE_CONFIG.get('footer').get('font_file')})

# Add console_script_path to the console config
CONSOLE_CONFIG.get('global').update({'script_path' : CONSOLE_SCRIPT_PATH})

# Reference to program module that will be called from within the console
CONSOLE_CLI_MODULE = import_module(CONSOLE_CONFIG.get('global').get('cli_module', 'pyrpg.main'))
