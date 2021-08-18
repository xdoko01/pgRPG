''' Module implementing modify_brain command
'''

import pyrpg.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)


def cmd_new_modify_brain(*args, **kwargs):
    ''' Resets and Adds new commands to the entity's brain.
    '''

    # Get the entity
    entity = kwargs.get("entity")

   # Get the brain of the entity
    try:
        brain = engine.world.component_for_entity(entity, components.Brain)

        # Stop the brain
        brain.enabled = False

        # Delete and reset the brain with the new commands
        brain.reset(kwargs.get("commands", []))

        # Everything worked fine
        return 0

    except KeyError:
        # Entity has no brain
        return -1

