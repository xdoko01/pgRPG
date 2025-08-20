'''
Can be run from the console by putting following command

XXXX
'''

import pyrpg.core.messages.messages as msg
import pyrpg.core.main as main

from pyrpg.functions.str_utils import translate_str
from pyrpg.functions import translate


def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_add_msg, alias=module_name)
    # Optional names for the script
    register(fnc=script_add_msg, alias='add_msg')


def script_add_msg(event=None, *args, **kwargs):
    ''' Add a game message into the message queue
    '''

    # Get message parameters
    position = kwargs.get("position", None)
    text = kwargs.get("text", "none")
    ttl = kwargs.get("ttl", None)

    # Substitute words starting by % with values from event dict
    if event is not None:

        # Translate the event parameters from entity_id to entity alias
        trans_event_params = translate(trans_dict=main.engine.ecs_manager._entity_to_alias, value=event.params)

        # Substitute the event parameters with translated event values
        text = translate_str(for_trans=text, trans_dict=trans_event_params, prefix='%')

    # Add the message to the queue
    main.engine.message_manager.add_message(message=msg.Message(pos=position, text=text, ttl=ttl))

    # Return success
    return 0
