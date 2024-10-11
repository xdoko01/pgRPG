'''
Can be run from the console by putting following command

XXXX
'''

from pyrpg import main
from core.components.brain_ai import BrainAI
from pyrpg.functions.str_utils import translate_str


def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_set_bb_value, alias=module_name)
    # Optional names for the script
    register(fnc=script_set_bb_value, alias='set_bb_value')

def script_set_bb_value(event, *args, **kwargs):
    ''' Script that updates blackboard of the Brain of given entity
    '''

    entity_id = kwargs['entity']
    bb_key = kwargs['bb_key']
    bb_value = kwargs['bb_value']
    only_if_not_set = kwargs.get('only_if_not_set', False)

    # translate entity_id, bb_value that can be from the event params
    bb_value = translate_str(for_trans=bb_value, trans_dict=event.params, prefix='%')
    entity_id = int(translate_str(for_trans=entity_id, trans_dict=event.params, prefix='%'))

    # get brain component for the entity if exists
    brain = main.engine.ecs_manager.try_component(entity=entity_id, component=BrainAI)

    # based on only_if_not_set parameter set the value on the blackboard
    if not brain: return 0
    if brain.generator.bb.globals.get(bb_key) is not None and only_if_not_set: return 0

    brain.generator.bb.globals.add(bb_key, int(bb_value))

    # Return success
    return 0
