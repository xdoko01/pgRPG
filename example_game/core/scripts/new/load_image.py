'''
Can be run from the console by putting following command

XXXX
'''
import pygame
from pyrpg.main import main
from pyrpg.core.config.filepaths import FILEPATHS # for IMAGE_PATH

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_load_image, alias=module_name)
    # Optional names for the script
    register(fnc=script_load_image, alias='load_image')

def script_load_image(event, *args, **kwargs):
    ''' Script that displays an image
    '''

    image_file = kwargs.get('image_file')

    # Do not show progress information and do not clear anything
    main.gui_manager.blit_image(image=pygame.image.load(FILEPATHS["IMAGE_PATH"] / image_file))

    # Return success
    return 0
