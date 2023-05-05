''' Module implementing remove_screen command
'''

import backup.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_remove_screen, alias=module_name)

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
