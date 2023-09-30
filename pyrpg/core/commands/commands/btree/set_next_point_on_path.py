''' Module implementing set_next_point_on_path command

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
    register(fnc=cmd_set_next_point_on_path, alias=module_name)

def cmd_set_next_point_on_path(*args, **kwargs):
    '''Sets the next point in path on the blackboard.

    Functionality:
    **************

    *Goal*
        - Set the next point on the path

    *Results*
        - `SUCCESS` - next point set
        - `RUNNING` - nope, this is always immediate
        - `FAILURE` - no next point, path is at the end

    *Params*
        - `bb_path_points` - path dictionary on the blackboard
        - `bb_path_index` - index of the current path point
        - `bb_path_next_point` - output point on the blackboard
        - `cycle` - if start from the first point once path is at the end

    *Steps*
    - Check the current point and move to the next one
    - Write it to bb_path_next_point

    Example:
    ********
    {
        "type": "Behavior",
        "name": "Set Next point on path",
        "cmd_process": [
            "btree.set_next_point_on_path", 
            {
                "bb_path_points": "bb_path_points", 
                "bb_path_index": "bb_path_index"
                "bb_path_next_point": "bb_point",
                "cycle": true
            }
        ]
    }
    '''

    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # Get the current point, increase idx and write new point on bb
    path_points = bb_globals.get(kwargs["bb_path_points"])
    path_index = bb_globals.get(kwargs["bb_path_index"])

    if path_index is None:
        path_index = 0
    elif path_index == len(path_points) - 1:
        if kwargs["cycle"]:
            path_index = 0
        else:
            return 'FAILURE' # end of path
    else:
        path_index += 1


    #point = path["points"][path["curr"]]

    bb_globals.update({kwargs["bb_path_index"]: path_index})
    bb_globals.update({kwargs["bb_path_next_point"]: path_points[path_index]})

    return 'SUCCESS'
