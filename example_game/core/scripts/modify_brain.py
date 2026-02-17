'''
Can be run from the console by putting following command

XXXX
'''

import pgrpg.core.ecs.components as components
import pgrpg.core.main as main


def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_modify_brain, alias=module_name)
    # Optional names for the script
    register(fnc=script_modify_brain, alias='modify_brain')


def script_modify_brain(event=None, *args, **kwargs):
    ''' Called from scene as an reaction to event fulfilled
    conditions.
    '''

    # Get the entity whose brain I will be working with
    entity = main.engine.ecs_manager.get_entity_id(
        entity_alias=kwargs.get("entity", None)
    )

    # Get the brain of the entity
    try:
        brain = main.engine.ecs_manager.component_for_entity(
            entity,
            components.Brain
        )

        # Stop the brain
        brain.enabled = False

        # Delete and reset the brain with the new commands
        brain.reset(kwargs.get("commands", []))

        # Everything worked fine
        return 0

    except KeyError:
        # Entity has no brain
        return -1
