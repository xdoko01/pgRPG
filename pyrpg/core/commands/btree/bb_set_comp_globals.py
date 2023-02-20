''' Module implementing bb_set_globals_comp command for behavior tree
'''

import logging

# For method get component_class
from pyrpg.core.managers.ecs_manager import get_component_class

# Logger init
logger = logging.getLogger(__name__)


def cmd_bb_set_comp_globals(*args, **kwargs):
    ''' Saves the reference to a component under
	given key on the global blackboard.
    '''

    # BTree reference
    bb_globals = kwargs["brain"].blackboard

    # Get the component class 
    comp_class = get_component_class(comp_type=kwargs["component"])

    # Get the result. Must be RUNNING if you want to plan it in cmd_init
    res = kwargs.get("result", 'SUCCESS')

    logger.debug(f'Getting component for entity {kwargs["entity"]}')
    # Get the component
    try:
        comp_obj = kwargs["world"].component_for_entity(kwargs["entity"], comp_class)
    except AttributeError:
        logger.debug(f'Entity does not have component "{comp_class}"')
        return 'FAILURE'
    else:
        # Store the component on the blackboard
        bb_globals.update({kwargs["bb_key"]: comp_obj})
        logger.debug(f'Storing component {comp_obj} for entity {kwargs["entity"]} to bb_globals under key {kwargs["bb_key"]}')

        return res # either RUNNING or SUCCESS