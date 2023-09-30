''' Module implementing move_to_bb_position command

    Parameters that are alwyas passed by the command manager
    ********************************************************

        current_time = kwargs["current_time"]
        world = kwargs["world"]
        ecs_mng = kwargs["ecs_mng"]
        entity = kwargs["entity"]
        keys = kwargs["keys"]
        events = kwargs["events"]
        brain = kwargs["brain"]

    Parameters available for the behavior node
    ******************************************

        # Time when the running behavior was first visited - init
        init_time = kwargs["brain"].blackboard.running_behavior.init_time

        # How long is the behavior node running
        duration = kwargs["brain"].blackboard.running_behavior.duration

        # How many times the behavior was executed
        ticks_count = kwargs["brain"].blackboard.running_behavior.ticks_count

        # Local running behavior blackboard
        bb_locals = kwargs["brain"].blackboard.running_behavior.bb

    Parameters available for the whole behavior tree
    ************************************************

        bb_globals = kwargs["brain"].blackboard
'''
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_move_to_bb_position, alias=module_name)

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

def cmd_move_to_bb_position(*args, **kwargs):
    ''' Moves entity to the position stored on the blackboard.

    Functionality:
    **************

    *Goal*
        - Move entity to the position specified on the blackboard

    *Results*
        - `SUCCESS` - Position has been reached
        - `RUNNING` - Movement in progress
        - `FAILURE` - Moving to the position takes too long or entity position component cease to exists (entity destroyed)

    *Params*
        - `bb_point` - reference to the point on the blackboard
        - `max_move_time_s` - maximum time for moving to the point. If exceeded, return FAILURE
        - `change_of_direction_ms` - how long to keep moving one direction before changing it

    *Steps*

        - Prereq: Entity position component stored on the blackboard

        - Check, if target point is reached
          - if YES,
            - finish with `SUCCESS`

        - Check, if duration is out of max_move_time_s
          - if YES,
            - finish with `FAILURE`
        
        - CHeck if position component exists
          - if NO,
            - finish with Failure

        - Check, if it is time to change direction
          - if YES,
            - change direction
          - if NO,
            - continue direction

    Example:
    ********
    {
        "type": "Behavior",
        "name": "Move to BB Position",
        "cmd_process": [
            "btree.move_to_bb_position", 
            {
                "bb_point": "bb_point", 
                "bb_entity_pos_comp": "bb_entity_pos_comp",
                "max_move_time_s": 1000,
                "change_of_direction_ms": 750
            }
        ]
    }
    '''

    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # Get the behavior node reference for statistics
    behavior_node = kwargs["brain"].blackboard.running_behavior

    # Current time
    current_time = kwargs["current_time"]

    # Check, if we are not moving to the point for too long
    if behavior_node.duration > kwargs.get("max_move_time_s", 60) * 1000:
        return 'FAILURE'

    # Get the entity position
    entity_pos_comp = bb_globals.get(kwargs["bb_entity_pos_comp"])
    
    # If the Position component does not exists - return failure
    if not entity_pos_comp: 
        return 'FAILURE'

    # Get the current point to which we are heading
    point = bb_globals.get(kwargs["bb_point"])
    x, y = point

    # Check, if the distance is closed finish with SUCCESS
    if abs(y - entity_pos_comp.y) < 10 and abs(x - entity_pos_comp.x) < 10:
        return 'SUCCESS'

    # Check, if it is time to change the direction
    if current_time - behavior_node.bb.get("last_change_of_direction_ts", 0) >= kwargs.get("change_of_direction_ms", 500):
        behavior_node.bb["last_change_of_direction_ts"] = current_time

        # Decide on which axis we will be closing the gap - close the smaller gap
        if abs(x - entity_pos_comp.x) > abs(y - entity_pos_comp.y):
            behavior_node.bb["move_axis"] = 'X'
        else:
            behavior_node.bb["move_axis"] = 'Y'

    # Continue movement
    if behavior_node.bb["move_axis"] == 'X':
        perform_movement(
            world=kwargs["world"], 
            entity=kwargs["entity"], 
            moves=['left' if x - entity_pos_comp.x < 0 else 'right' if x - entity_pos_comp.x > 0 else 'right']
        )
    else:
        perform_movement(
            world=kwargs["world"], 
            entity=kwargs["entity"], 
            moves=['up' if y - entity_pos_comp.y < 0 else 'down' if y - entity_pos_comp.y > 0 else 'down']
        )

    return 'RUNNING'