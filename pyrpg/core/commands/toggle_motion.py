''' Module implementing toggle_motion command
'''

import pyrpg.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_toggle_motion(*args, **kwargs):
    '''
    '''

    # Get entity whose motion we need to freeze from cmd parameters
    entity = kwargs.get("entity", None)
    toggle = kwargs.get("enable", True)


    # Get motion component for this entity - if it has one
    try:
        motion = engine.world.component_for_entity(entity, components.Motion)

        # Disable the motion
        motion.enabled = toggle

        # Successful finished
        return 0

    except KeyError:
        return -1
