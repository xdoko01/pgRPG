''' Module implementing toggle_control command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_toggle_control(*args, **kwargs):
    ''' Disable/enable any user input for given entity - used in cinematics so that 
    the user cannot break it with movements.

    Example (0,	commands.cmd_toggle_input, {"enable" : False})
    - above disables user input on entity
    '''

    # Get entity whose brain we need to freeze from cmd parameters
    entity = kwargs.get("entity", None)

    # Get on/off control information - default is enabled
    toggle = kwargs.get("enable", True)

    # Get Cotrollable component for this entity - if it has one
    try:
        control = engine.world.component_for_entity(entity, components.Controllable)

        # Disable the brain
        control.enabled = toggle

        # Successful finished
        return 0

    except KeyError:
        return -1
