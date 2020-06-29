''' Module implementing disable_collision command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_disable_collision(*args, **kwargs):
    ''' Simple remove Collidable component from the entity
    '''
    
    # Get entity to disable collisions
    entity = kwargs.get('entity', None)

    # Get Collidable component for the entity
    try:
        engine.world.remove_component(entity, components.Collidable)

        # Successfully finished
        return 0

    except KeyError:
        # Entity does not have Collidable component
        return -1