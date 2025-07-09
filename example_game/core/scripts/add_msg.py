'''
Can be run from the console by putting following command

XXXX
'''

import pyrpg.core.messages.messages as msg
import pyrpg.core.main as main

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_add_msg, alias=module_name)
    # Optional names for the script
    register(fnc=script_add_msg, alias='add_msg')

def script_add_msg(event=None, *args, **kwargs):
    ''' Add new game message into the message queue
    '''

    # Get message parameters
    position = kwargs.get("position", None)
    text = kwargs.get("text", "none")
    ttl = kwargs.get("ttl", None)

    # Add the message to the queue
    main.engine.message_queue.append(msg.Message(pos=position, text=text, ttl=ttl))

    #Return success
    return 0