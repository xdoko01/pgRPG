''' Module implementing move_to command
'''

from pyrpg.core.ecs.components.new.position import Position # To work with components in commands (remove search add ...)
from .new_move_add import cmd_new_move_add
import math # for calculation of square root move_to

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_new_move_to, alias=module_name)

def cmd_new_move_to(*args, **kwargs):
    ''' Move to certain x,y position on the current map.
    Returns exception until the destination is reached. So it needs to be
    redirected to itself in order to repeat this command until destination is reached. 

    TODO - change direction not immediatelly but after some time or number of steps
    '''

    # World reference
    world = kwargs.get("world")

    # Who (entity) needs to move
    entity = kwargs.get("entity")

    # Get the target coordinates
    tx = kwargs.get("x", None)
    ty = kwargs.get("y", None)

    # Get the coordinate of the entity and the target 
    position = world.component_for_entity(entity, Position)

    sign = lambda x: 1 if x>0 else (-1 if x<0 else 0)

    # If the distance is close, close the gap and end
    if math.sqrt( (tx - position.x)**2 + (ty - position.y)**2 ) < 10:
        position.x = tx
        position.y = ty

        return 0

    # If gap is big, continue
    else:
        # Create movement so to minimise the distance between entity and the target
        if abs(tx - position.x) > abs(ty - position.y):
            # Close on x-axis
            cmd_new_move_add(world=world, entity=entity, moves=['left' if tx - position.x < 0 else 'right' if tx - position.x > 0 else None])
        else:
            # Close on y-axis
            cmd_new_move_add(world=world, entity=entity, moves=['up' if ty - position.y < 0 else 'down' if ty - position.y > 0 else None])

        return -1
