''' Module implementing attack command

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
from pyrpg.core.ecs.components.new.flag_do_attack import FlagDoAttack

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_attack_full, alias=module_name)

def cmd_attack_full(*args, **kwargs):
    ''' Add FlagDoAttack to the entity so long to fill the full attack animation cycle

    Functionality:
    **************

    *Goal*
        - Use weapon on the current position/direction for given time period

    *Results*
        - `SUCCESS` - time `attack_time_ms` is over
        - `RUNNING` - attack in progress
        - `FAILURE` - no more ammo or entity destroyed or target destroyed

    *Params*
        - `attack_time_ms` - how long to generate the attack commands
        - `target_damageable_comp` - Damageable component of the target on the blackboard
        - `entity_damageable_comp` - Damageable component of the entity on the blackboard

    *Steps*
        - Prereq: Save target health component
        - Prereq: Save entity health component

        - Check, if entity/target destroyed
          - if YES,
            - finish with `FAILURE`

        - Check, if within `attack_duration_ms`
          - if YES,
            - assign `FlagHasAttacked` component to entity
            - finish with `RUNNING`
          - if NO,
            - finish with `SUCCESS`

    Example:
    ********
    {
        "type": "Behavior",
        "name": "Attack the target",
        "cmd_process": [
            "btree.attack_full", 
            {
                "target_damageable_comp": "bb_target_damageable_comp", 
                "entity_damageable_comp": "bb_entity_damageable_comp",
                "attack_time_ms": 750
            }
        ]
    }
    '''
    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # Get the behavior node
    behavior_node = kwargs["brain"].blackboard.running_behavior

    # Get the entity and the target Position components
    target_damageable_comp = bb_globals.get(kwargs["target_damageable_comp"])
    entity_damageable_comp = bb_globals.get(kwargs["entity_damageable_comp"])

    if target_damageable_comp.health <=0 or entity_damageable_comp.health <= 0:
        return 'FAILURE'

    if behavior_node.duration >= kwargs.get("attack_time_ms", 500):
        # Unit has been executed long enough - continue without exception
        return 'SUCCESS'
    else:
        # There is still time to execute - return exception
        kwargs["world"].add_component(kwargs["entity"], FlagDoAttack())
        return 'RUNNING'
