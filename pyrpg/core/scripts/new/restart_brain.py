'''
Can be run from the console by putting following command

XXXX
'''

from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.ecs.components import BrainAI
from pyrpg.functions.str_utils import translate_str


def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_restart_brain, alias=module_name)
    # Optional names for the script
    register(fnc=script_restart_brain, alias='restart_brain')

def script_restart_brain(event, *args, **kwargs):
    ''' Script that loads aa new quest

    '''

    entity_id = kwargs['entity']

    # get brain component for the entity
    brain = ECSManager.try_component(entity=entity_id, component=BrainAI)

    # start brain from scratch
    brain.generator.restart_brain()

    # Return success
    return 0
