''' Module implementing move_to command
'''

import backup.core.engine as engine # To reference the world 
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.motion import Motion
from .move import cmd_move
import math # for calculation of square root move_to


def cmd_move_to(*args, **kwargs):
    ''' Move to certain x,y position on the current map.
    Returns exception until the destination is reached. So it needs to be
    redirected to itself in order to repeat this command until destination is reached. 

    TODO - change direction not immediatelly but after some time or number of steps
    '''

    # Who (entity) needs to move
    entity = kwargs.get("entity")

    # Get the target coordinates
    tx = kwargs.get("x", None)
    ty = kwargs.get("y", None)

    # Get the coordinate of the entity and the target 
    position = engine.world.component_for_entity(entity, Position)
    motion = engine.world.component_for_entity(entity, Motion)

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
            cmd_move(entity=entity, dx=sign(tx - position.x) * 120)
        else:
            # Close on y-axis
            cmd_move(entity=entity, dy=sign(ty - position.y) * 120)			

        return -1
