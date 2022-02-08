''' Module implementing add_msg command
'''

import pyrpg.core.messages.messages as msg # To reference the message
import backup.core.engine as engine # To reference the message queue
import pygame

def cmd_add_msg(*args, **kwargs):
    '''
    '''

    # Get message parameters
    position = kwargs.get("position", (0, 0))
    text = kwargs.get("text", "none")
    ttl = kwargs.get("ttl", None) 

    # Add the message to the queue
    engine.message_queue.append(msg.Message(pos=position, text=text, ttl=ttl))

    # New message successfully added
    return 0