''' Module implementing check_enemies_around command

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
from pyrpg.core.ecs.components.new.position import Position

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_check_enemies_around, alias=module_name)

def cmd_check_enemies_around(*args, **kwargs):
    ''' Moves entity to the position stored on the blackboard.

    Functionality:
    **************

    *Goal*
        - Check if there is some enemy around the entity

    *Results*
        - `SUCCESS` - Enemy identified around the entity
        - `RUNNING` - n/a
        - `FAILURE` - No enemy is around

    *Params*
        - `list_of_enemies` - list of enemy aliases who should be considered as an enemy. If emty, everyone is considered as an enemy
        - `radius` - how far the enemy must be to be spotted by entity
        - `bb_entity_pos_comp` - reference to position component of the entity
        - `bb_enemy` - blackboard key under which to record the enemy on the blackboard


    *Steps*

        - Prereq: Entity position component stored on the blackboard


    Example:
    ********
    {
        "type": "Behavior",
        "name": "Move to BB Position",
        "cmd_process": [
            "btree.check_enemies_around", 
            {
                "list_of_enemies": ["player01"], 
                "radius": 250,
                "bb_entity_pos_comp": "bb_entity_pos_comp",
                "bb_enemy": "bb_enemy"
            }
        ]
    }
    '''

    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # List of enemies
    list_of_enemies = kwargs.get("list_of_enemies", [])

    # Get the entity position
    entity_pos_comp = bb_globals.get(kwargs["bb_entity_pos_comp"])

    # If the Position component does not exists - return failure
    if not entity_pos_comp: 
        return 'FAILURE'

    # Check every position of every entity
    for enemy, (position) in kwargs["world"].get_component(Position):


        # Do not check yourself
        if enemy == kwargs["entity"]: continue

        # Skip entities that are not enlisted as enemies
        if list_of_enemies and enemy not in list_of_enemies: continue

        # Check all others for being an enemy
        if (position.x - entity_pos_comp.x) < kwargs["radius"] and (position.y - entity_pos_comp.y) < kwargs["radius"]:

            if (entity_pos_comp.dir_name == 'left' and position.x <= entity_pos_comp.x) or \
               (entity_pos_comp.dir_name == 'right' and position.x >= entity_pos_comp.x) or \
               (entity_pos_comp.dir_name == 'up' and position.y <= entity_pos_comp.y) or \
               (entity_pos_comp.dir_name == 'down' and position.y >= entity_pos_comp.y):
                
                bb_globals.update({kwargs["bb_enemy"]: enemy})

                print(f'Returning success for enemy "{enemy}"')
                return 'SUCCESS'

    return 'FAILURE'
