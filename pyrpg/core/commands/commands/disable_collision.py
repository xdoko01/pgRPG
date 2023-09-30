''' Module implementing disable_collision command
'''

import backup.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_disable_collision, alias=module_name)

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