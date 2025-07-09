'''
Can be run from the console by putting following command

XXXX
'''

import core.components as components
import core.processors as processors

import pygame
import random
import pyrpg.core.main as main

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_shake_screen, alias=module_name)
    # Optional names for the script
    register(fnc=script_shake_screen, alias='shake_screen')


def script_shake_screen(event=None, *args, **kwargs):
    ''' Shake the screen
    '''

    camera = main.engine.ecs_manager.component_for_entity(event.other_obj, components.Camera)
    original_cam_pos_x, camera.screen_pos_y = camera.screen_pos_x, camera.screen_pos_y

    for i in range(30):
        camera.screen_pos_x = camera.screen_pos_x + random.randint(-5, 5)
        camera.screen_pos_y = camera.screen_pos_y + random.randint(-5, 5)
        # Render the world
        main.engine.ecs_manager._world.get_processor(processors.RenderWorldProcessor).process()
        # Blit the world
        pygame.display.update()
        # Wait to make it more visible
        pygame.time.wait(50)

    # Put the screen back
    camera.screen_pos_x, camera.screen_pos_y = original_cam_pos_x, camera.screen_pos_y

    # Return success
    return 0