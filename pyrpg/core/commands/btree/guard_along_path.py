''' Module implementing move_to_target_range command
'''

import logging

from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

# Logger init
logger = logging.getLogger(__name__)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_guard_along_path, alias=module_name)

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

def cmd_guard_along_path(*args, **kwargs):
    '''
  *Goal*
    - Moves entity along the path specified by points until enemy is spoted
  *Results*
    - `SUCCESS` - enemy has been spotted
    - `RUNNING` - moving along the path
    - `FAILURE` - guarding way for too long
  *Params*
    - `enemy` - who should be considered as an enemy
    - `range` - how close must enemy get to be spotted
  *Steps*
   - Save enemy position component
   - Save entity position component


   - Check if the distance to enemy is short and facing the enemy
     - if YES, 
       - finish with `SUCCESS`
     - if NO,
       - finish with `RUNNING`
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

    entity_pos_comp
    path
    path_idx

    Parameters used on the local Behavior blackboard
    ---------------------------------------------------

    last_check_for_enemies_ts

    '''

    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # Get the blackboard for this particular command - i.e running behavior
    bb_locals = kwargs["brain"].blackboard.running_behavior.bb

    # Get the entity and the target Position components
    entity_pos_comp = bb_globals.get(kwargs["entity_pos_comp"])

    # Get the current point to which we are heading
    path = bb_globals["path"]
    path_point_idx = bb_globals["path_point_idx"]
    path_point = path[path_point_idx]

    # If the entity is hunting for too long - finish with Failure
    if kwargs["brain"].blackboard.running_behavior.duration > kwargs["max_guard_time_s"] * 1000:
        return 'FAILURE'

    # If it is time for the entity to check whether there is some enemy close
    if kwargs["current_time"] - bb_locals.get("last_check_for_enemies_ts", 0) >= kwargs.get("check_for_enemies_interval_ms", 1000):
        bb_locals["last_check_for_enemies_ts"] = kwargs["current_time"]

        # Check all entities
        for ent, (position, renderable) in kwargs["world"].get_components(Position, RenderableModel):
            #compare positions and return if spotted
            return 'SUCCESS'

    # If current point on the path for reached - move the idx on the blackboard
    path_point vs entity_pos_comp

    # Move towards the point
    ... TODO

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
