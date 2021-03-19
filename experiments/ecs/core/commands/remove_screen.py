''' Module implementing remove_screen command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_remove_screen(*args, **kwargs):
    ''' Input
        - entity from which I want to remove the screen
        - screen parameters
    '''

    # Get entity of for the new screen
    focus_ent = kwargs.get("entity", None)

    # Try to Remove the camera
    try:

        engine.world.remove_component(focus_ent, components.Camera())

        # Successfully removed
        return 0

    except KeyError:

        # entity or component does not exist
        return -1
