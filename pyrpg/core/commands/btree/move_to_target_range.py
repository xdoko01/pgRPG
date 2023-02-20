''' Module implementing move_to_target_range command
'''

import logging

from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

# Logger init
logger = logging.getLogger(__name__)

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

def cmd_move_to_target_range(*args, **kwargs):
    '''
        *Goal*
            - Moves entity close to the target (defined by range) and faces the target
        *Results*
            - `SUCCESS` - target is in range
            - `RUNNING` - on the way to the target
            - `FAILURE` - cannot reach the target
        *Params*
            - `range` - how close to get to the target
            - `get_target_position_ms` - how often to ask about the targets new position, the shorter the time is the harder the opponent is.
            - `max_hunt_time_s` - how long to hunt the target, if longer, finish with the failure (in seconds)
            - `bb_target_pos_comp` - position component of the target as a name of the key on the BB
            - `bb_my_pos_comp` - position component of the entity as a name of the key on the BB
        *Steps*
        - Save the time of first call
        - Save the time of last update of the target position

        - Check if the `MoveToTargetRange` is running too long or target ceise to exist
            - if YES,
            - finish with `FAILURE`

        - Check if the distance is closed (you are in range)
            - if YES, 
            - `execute command` face the target
            - finish with `SUCCESS`
            - if NO, continue hunting the target
            - `execute command` move command
            - finish with `RUNNING`
    '''

    ''' We do not need to call all of these definitions on every tick, just use it whenre necessary in the code and that is it
    # Brain/BTree reference
    brain = kwargs.get("brain", None)

    # World reference
    world = kwargs["world"]

    # Who (entity) needs to move
    entity = kwargs.get["entity"]

    # Entity position component
    bb_my_pos_comp = brain.blackboard.get_value(key="bb_my_pos_comp")

    # Target position component
    bb_my_pos_comp = brain.blackboard.get_value(key="bb_target_pos_comp")

    # How close to get to the target
    range = kwargs.get("range", 500)

    # How often to get updates about the enemy position
    get_target_position_ms = kwargs.get("get_target_position_ms", 1000)

    # How long to hunt before leaving it be. None means forever
    max_hunt_time_s = kwargs.get("get_target_position_ms", None)

    # Get current time
    current_time = kwargs["current_time"]
    '''
    '''
    # When the unit is called for the first time, remember the entity and enemy position components, 
    # and the time when we obtained the position and store it into the brain.
    if brain.cmd_first_call:
        # Get the coordinate of the moving entity
        brain.var_4 = world.component_for_entity(entity, Position)
        brain.var_5 = world.component_for_entity(target_ent, Position)
        brain.var_3 = brain.cmd_first_call_time 
    '''

    '''
    Parameters that are alwyas passed by the command manager
    --------------------------------------------------------

    current_time = kwargs["current_time"]
    world = kwargs["world"]
    entity = kwargs["entity"]
    keys = kwargs["keys"]
    events = kwargs["events"]
    brain = kwargs["brain"]

    Parameters used on the global BTree blackboard
    ---------------------------------------------------

    Parameters used on the local Behavior blackboard
    ---------------------------------------------------

    last_target_pos_refresh_ts
    '''

    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # Get the blackboard for this particular command - i.e running behavior
    bb_locals = kwargs["brain"].blackboard.running_behavior.bb

    # Get the entity and the target Position components
    target_pos_comp = bb_globals.get(kwargs["target_pos_comp"])
    entity_pos_comp = bb_globals.get(kwargs["entity_pos_comp"])

    logger.debug(f'bb_globals: {bb_globals}, bb_locals: {bb_locals}, target_pos_comp: {target_pos_comp}, entity_pos_comp: {entity_pos_comp}')

    # If the entity is hunting for too long - finish with Failure
    logger.debug(f'duration: {kwargs["brain"].blackboard.running_behavior.duration}, max_hunt_time: {kwargs["max_hunt_time_s"] * 1000}')

    if kwargs["brain"].blackboard.running_behavior.duration > kwargs["max_hunt_time_s"] * 1000:
        return 'FAILURE'

    # Is it the time to change the direction based on
    logger.debug(f'time since last refresh: {kwargs["current_time"] - bb_locals.get("last_target_pos_refresh_ts", 0)}, get_target_position_ms: {kwargs.get("get_target_position_ms", 1000)}')

    if kwargs["current_time"] - bb_locals.get("last_target_pos_refresh_ts", 0) >= kwargs.get("get_target_position_ms", 1000):
        bb_locals["last_target_pos_refresh_ts"] = kwargs["current_time"]

        # Decide on which axis we will be closing the gap - close the smaller gap in order
        # to be able to shoot quicker.
        # Bigger gap on X-axis
        if abs(target_pos_comp.x - entity_pos_comp.x) > abs(target_pos_comp.y - entity_pos_comp.y):
            bb_locals["move_axis"] = 'X'
        else:
            bb_locals["move_axis"] = 'Y'

    # If the distance is closed on the Y axis, face the target and finish with SUCCESS
    if abs(target_pos_comp.y - entity_pos_comp.y) < 10 and abs(target_pos_comp.x - entity_pos_comp.x) < kwargs.get("range", 500):
        logger.debug(f'(target_pos_comp.y - entity_pos_comp.y)={(target_pos_comp.y - entity_pos_comp.y)}')
        logger.debug(f'(target_pos_comp.x - entity_pos_comp.x)={(target_pos_comp.x - entity_pos_comp.x)}')

        if target_pos_comp.x < entity_pos_comp.x:
            entity_pos_comp.set_direction('left')
        else:
            entity_pos_comp.set_direction('right')
        return 'SUCCESS'

    # If the distance is closed on the X axis, face the target and finish with SUCCESS
    elif abs(target_pos_comp.x - entity_pos_comp.x) < 10 and abs(target_pos_comp.y - entity_pos_comp.y) <  kwargs.get("range", 500):
        logger.debug(f'(target_pos_comp.x - entity_pos_comp.x)={(target_pos_comp.x - entity_pos_comp.x)}')
        logger.debug(f'(target_pos_comp.y - entity_pos_comp.y)={(target_pos_comp.y - entity_pos_comp.y)}')

        if target_pos_comp.y < entity_pos_comp.y:
            entity_pos_comp.set_direction('up')
        else:
            entity_pos_comp.set_direction('down')
        return 'SUCCESS'

    else:
        # If gap is big, continue
        if bb_locals["move_axis"] == 'X':
            perform_movement(
                world=kwargs["world"], 
                entity=kwargs["entity"], 
                moves=['left' if target_pos_comp.x - entity_pos_comp.x < 0 else 'right' if target_pos_comp.x - entity_pos_comp.x > 0 else 'right']
            )
        else:
            perform_movement(
                world=kwargs["world"], 
                entity=kwargs["entity"], 
                moves=['up' if target_pos_comp.y - entity_pos_comp.y < 0 else 'down' if target_pos_comp.y - entity_pos_comp.y > 0 else 'down']
            )

        return 'RUNNING'
