import backup.core.engine as engine
import pyrpg.core.ecs.components as components
import pyrpg.core.ecs.processors as processors

import pygame
import random

def script_shake_screen(event=None, *args, **kwargs):
    ''' Shake the screen
    '''

    camera = engine.world.component_for_entity(event.other_obj, components.Camera)
    original_cam_pos_x, camera.screen_pos_y = camera.screen_pos_x, camera.screen_pos_y

    for i in range(30):
        camera.screen_pos_x = camera.screen_pos_x + random.randint(-5, 5)
        camera.screen_pos_y = camera.screen_pos_y + random.randint(-5, 5)
        # Render the world
        engine.world.get_processor(processors.RenderWorldProcessor).process()
        # Blit the world
        pygame.display.update()
        # Wait to make it more visible
        pygame.time.wait(50)

    # Put the screen back
    camera.screen_pos_x, camera.screen_pos_y = original_cam_pos_x, camera.screen_pos_y

    # Return success
    return 0