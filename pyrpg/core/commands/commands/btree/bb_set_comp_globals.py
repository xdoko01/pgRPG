''' Module implementing bb_set_globals_comp command for behavior tree

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

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_bb_set_comp_globals, alias=module_name)

def cmd_bb_set_comp_globals(*args, **kwargs):
    ''' Saves the reference to a component under given key on the global blackboard.

    Functionality:
    **************

    *Goal*
        - Save the component on the btree blackboard for later use by other commands.

    *Results*
        - `SUCCESS` - component successfully stored
        - `RUNNING` - component successfully stored and result='RUNNING'
        - `FAILURE` - component cannot be stored

    *Params*
        - `component` - component class definition in form of a string
        - `bb_key` - key under which the component should be stored on the blackboard
        - `entity` - entity as a owner of the component - either alias or reference to the blackboard

    *Steps*

    Example:
    ********
    {
        "type": "Behavior",
        "name": "Store Position Component",
        "cmd_process": [
            "btree.bb_set_comp_globals", 
            {
                "bb_key": "bb_target_damageable_comp", 
                "component": "new.damageable:Damageable",
                "entity": "player01"
                "bb_entity": "bb_target_entity"
            }
        ]
    }
    '''

    # BTree reference
    bb_globals = kwargs["brain"].blackboard._bb

    # Get the component class 
    comp_class = kwargs["ecs_mng"].get_comp_class_from_def(comp_class_def=kwargs["component"])

    # Get the entity - first from BB next from entity
    entity = bb_globals.get(kwargs.get("bb_entity"), kwargs["entity"])

    try:
        comp_obj = kwargs["world"].component_for_entity(entity, comp_class)
    except AttributeError:
        return 'FAILURE'
    else:
        # Store the component on the blackboard
        bb_globals.update({kwargs["bb_key"]: comp_obj})

        return kwargs.get("result", 'SUCCESS') # either RUNNING or SUCCESS