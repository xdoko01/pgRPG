''' Module implementing bb_set_comps_global command for behavior tree

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
    register(fnc=cmd_bb_set_comps_globals, alias=module_name)

def cmd_bb_set_comps_globals(*args, **kwargs):
    ''' Saves the reference to a components under given keys on the global blackboard.
    Unlike bb_set_comp_globals is capable to store multiple components in one call.

    Functionality:
    **************

    *Goal*
        - Save the components on the btree blackboard for later use by other commands.

    *Results*
        - `SUCCESS` - all components successfully stored
        - `RUNNING` - all components successfully stored and result='RUNNING'
        - `FAILURE` - some component cannot be stored

    *Params*
        - `components` - list of dictionaries, each dictionary specifies component by 
                        entity (either alias or reference to the blackboard - first from BB next from entity),
                        comp and key under which it should be stored on BB.

    *Steps*
        - N/A

    Example:
    ********
    {
        "type": "Behavior",
        "name": "Store Position and Movable Components",
        "cmd_process": [
            "btree.bb_set_comps_globals", 
            {
                "components": [
                    {
                        "entity": "player01",
                        "component": "new.position:Position",
                        "bb_key": bb_player_pos_comp
                    },
                    {
                        "bb_entity": "bb_target_entity", // entity from blackboard
                        "component": "new.movable:Movable",
                        "bb_key": bb_player_mov_comp
                    }
                ]
            }
        ]
    }
    '''

    # BTree reference
    bb_globals = kwargs["brain"].blackboard._bb

    # ECS manager reference
    ecs_mng = kwargs["ecs_mng"]

    # ECS world reference
    world = kwargs["world"]

    # Saved keys
    saved_keys = []

    # Cycle throug components
    for component_def in kwargs["components"]:

        # Get the component class 
        comp_class = ecs_mng.get_comp_class_from_def(comp_class_def=component_def["component"])

        # Get the entity - first from BB next from entity and if not defined  from the owner of a brain
        entity = bb_globals.get(component_def.get("bb_entity"), component_def.get("entity", kwargs["entity"]))

        # Get the component for the entity
        try:
            comp_obj = world.component_for_entity(entity, comp_class)
        except AttributeError:
            # In case some component does not exist, clear the blackboard of all already created keys
            for saved_key in saved_keys: bb_globals.pop(saved_key)
            return 'FAILURE'
        else:
            # Store the component on the blackboard
            bb_globals.update({component_def["bb_key"]: comp_obj})
            saved_keys.append(component_def["bb_key"])

    return kwargs.get("result", 'SUCCESS') # either RUNNING or SUCCESS