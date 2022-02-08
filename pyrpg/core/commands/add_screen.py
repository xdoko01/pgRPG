''' Module implementing add_screen command
'''

import backup.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_add_screen(*args, **kwargs):
    ''' Input
        - entity to which I want to add the screen
        - screen parameters
    '''

    # Get entity of for the new screen
    focus_ent = kwargs.get("entity", None)

    # Get the Camera 
    screen_pos_x = kwargs.get("screen_pos_x", 0)
    screen_pos_y = kwargs.get("screen_pos_y", 0)
    screen_width = kwargs.get("screen_width", 300)
    screen_height = kwargs.get("screen_height", 300)

    # Create the camera
    engine.world.add_component(focus_ent, components.Camera(screen_pos_x=screen_pos_x, screen_pos_y=screen_pos_y, screen_width=screen_width, screen_height=screen_height))

    # New camera successfully created
    return 0
