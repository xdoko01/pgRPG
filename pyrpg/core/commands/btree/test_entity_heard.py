''' Module implementing test_entity_heard command

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
        # Global blackboard
        bb_globals = kwargs["brain"].blackboard
'''
from math import radians, sin

from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

import pyrpg.core.ecs.processors.new.functions as flt   # Filter functions


def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_test_entity_heard, alias=module_name)

def cmd_test_entity_heard(*args, **kwargs):
    '''Tests if enemy is was heard by the entity.

    Functionality:
    **************

    *Goal*
        - Check if there is some other entity is heard by the entity

    *Results*
        - `SUCCESS` - Entity heard by the entity
        - `RUNNING` - n/a
        - `FAILURE` - No entity heard

    *Params*
        - `list_of_entities` - list of entity aliases. If emty, every entity can be heard.
        - `distance` - how far the other entity must be to be heard by entity
        - `in_bb_ent_pos_comp` - reference to position component of the entity (optional)
        - `out_bb_entity` - blackboard key under which to write the heard entity_id on the blackboard

    *Steps*
        - Prereq: Entity position component stored on the blackboard


    Example:
    ********
    {
        "type": "Behavior",
        "name": "Test Enemy Heard",
        "cmd_process": [
            "btree.test_entity_heard", 
            {
                "list_of_entities": ["player01"], 
                "distance": 300,
                "in_bb_ent_pos_comp": "bb_entity_pos_comp", # optional, if not present world is asked for it
                "out_bb_entity": "bb_enemy"
            }
        ]
    }
    '''

    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # List of enemies
    list_of_enemies = kwargs.get("list_of_entities", [])

    # Get the entity position - either get it from blackboard or get it directly from the world
    ent_pos_comp_key = kwargs.get("in_bb_ent_pos_comp")
    ent_pos_comp = bb_globals.get(ent_pos_comp_key) if ent_pos_comp_key else kwargs["world"].component_for_entity(kwargs["entity"], Position)

    # If the Position component does not exists - return failure
    if not ent_pos_comp: 
        return 'FAILURE'

    # Get map that is on the object in camera's focus
    map = kwargs["ecs_mng"]._game_functions['FNC_GET_MAP'](ent_pos_comp.map)

    sin_angle = sin(radians(kwargs["angle"] // 2))

    # Filter all entities that pass the filters - must be moving and not behind the wall
    for oth_ent, (oth_pos, _) in filter(
        lambda x: (
            flt.filter_only_specific_entity_ids(list_of_enemies, x) and    # we are interested only in entities in the list
            flt.filter_only_within_distance_from_ent(ent_pos_comp, kwargs["distance"], x) and   # within distance
            flt.filter_only_not_behind_wall(ent_pos_comp, map, x)   # not hidden behind the wall
        ), kwargs["world"].get_components(Position, FlagDoMove)
    ):

        # The first enemy that will pass all the filters is our choice
        bb_globals.update({kwargs["out_bb_entity"]: oth_ent})
        return 'SUCCESS'

    return 'FAILURE'
