''' Module implementin togle_brain command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_toggle_brain(*args, **kwargs):
    ''' Stop/Start brain of given entity for the purposes of global game
    processor.

    This command should not have usually exception handling defined.
    Exception is thrown when component does not have Brain entity.

    '''

    # Get entity whose brain we need to freeze from cmd parameters
    entity = kwargs.get("entity", None)
    toggle = kwargs.get("enable", True)


    # Get brain component for this entity - if it has one
    try:
        brain = engine.world.component_for_entity(entity, components.Brain)

        # Disable the brain
        brain.enabled = toggle

        # Successful finished
        return 0

    except KeyError:
        return -1
