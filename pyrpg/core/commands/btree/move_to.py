''' Module implementing move_to command for behavior tree
'''
# For calculation of square root move_to
import math

# For used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

# For return statuses
from pyrpg.core.btrees.btree import TreeNode
status = TreeNode.Status

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_move_to, alias=module_name)

def perform_movement(world, entity, moves: list) -> None:
    '''Get existing or create new FlagDoMove component
    and append the required moves to it.'''
    try:
        # Get the FlagDoMove component from the entity
        flag_do_move = world.component_for_entity(entity, FlagDoMove)
        flag_do_move.add_moves(moves)

    except KeyError:
        flag_do_move = FlagDoMove(moves=moves)
        world.add_component(entity, flag_do_move)

def cmd_move_to(*args, **kwargs):
    ''' Move to certain x,y position on the current map.
    Returns exception until the destination is reached. So it needs to be
    redirected to itself in order to repeat this command until destination is reached. 

    TODO - change direction not immediatelly but after some time or number of steps
    '''

    # World reference
    world = kwargs.get("world")

    # Who (entity) needs to move
    entity = kwargs.get("entity")

    # BTree reference
    btree = kwargs.get("brain")

    # Get the target coordinates
    target = kwargs.get("bb_target")

    # Read the target from the bb
    tx, ty = btree.blackboard.get_value(key=target)

    # Get the coordinate of the entity and the target 
    position = world.component_for_entity(entity, Position)

    # If the distance is close, close the gap and end
    if math.sqrt( (tx - position.x)**2 + (ty - position.y)**2 ) < 10:
        position.x = tx
        position.y = ty

        return status.SUCCESS

    # If gap is big, continue
    else:

        # Create movement so to minimise the distance between entity and the target
        if abs(tx - position.x) > abs(ty - position.y):
            # Close on x-axis
            perform_movement(world=world, entity=entity, moves=['left' if tx - position.x < 0 else 'right' if tx - position.x > 0 else None])
        else:
            # Close on y-axis
            perform_movement(world=world, entity=entity, moves=['up' if ty - position.y < 0 else 'down' if ty - position.y > 0 else None])

        return status.RUNNING
