'''
Can be run from the console by putting following command

XXXX
'''

import pgrpg.core.ecs.components as components
import pgrpg.core.main as main


def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_disable_teleport, alias=module_name)
    # Optional names for the script
    register(fnc=script_disable_teleport, alias='disable_teleport')


def script_disable_teleport(event=None, *args, **kwargs):
    ''' Remove the teleport possibilities from the teleport
    '''

    main.engine.ecs_manager.remove_component(
        event.generator_obj,
        components.Collidable
    )

    # Return success
    return 0
