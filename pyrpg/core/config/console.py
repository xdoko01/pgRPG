from pyrpg.core.config.filepaths import FILEPATHS
from pyrpg.core.config import CONSOLE, show


# Fix the relative paths so that they are directing into correct folders
if CONSOLE.get('global', {}).get('bck_image', None): CONSOLE.get('global').update({'bck_image' : FILEPATHS["IMAGE_PATH"] / CONSOLE.get('global').get('bck_image')})
if CONSOLE.get('header', {}).get('bck_image', None): CONSOLE.get('header').update({'bck_image' : FILEPATHS["IMAGE_PATH"] / CONSOLE.get('header').get('bck_image')})
if CONSOLE.get('footer', {}).get('bck_image', None): CONSOLE.get('footer').update({'bck_image' : FILEPATHS["IMAGE_PATH"] / CONSOLE.get('footer').get('bck_image')})
if CONSOLE.get('header', {}).get('font_file', None): CONSOLE.get('header').update({'font_file' : FILEPATHS["FONT_PATH"] / CONSOLE.get('header').get('font_file')})
if CONSOLE.get('output', {}).get('font_file', None): CONSOLE.get('output').update({'font_file' :  FILEPATHS["FONT_PATH"] / CONSOLE.get('output').get('font_file')})
if CONSOLE.get('input', {}).get('font_file', None): CONSOLE.get('input').update({'font_file' : FILEPATHS["FONT_PATH"] / CONSOLE.get('input').get('font_file')})
if CONSOLE.get('footer', {}).get('font_file', None): CONSOLE.get('footer').update({'font_file' :  FILEPATHS["FONT_PATH"] / CONSOLE.get('footer').get('font_file')})

# Add console_script_path to the console config
CONSOLE.get('global').update({'script_path':  FILEPATHS["CONSOLE_SCRIPT_PATH"]})

# Reference to program module that will be called from within the console
from importlib import import_module
CONSOLE["CLI_MODULE"] = import_module(CONSOLE.get("global").get("cli_module", "pyrpg.main"))

show(CONSOLE)