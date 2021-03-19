import core.engine as engine
import core.messages.messages as msg
import pygame

def script_add_msg(event=None, *args, **kwargs):
    ''' Add new game message into the message queue
    '''

    # Get message parameters
    position = kwargs.get("position", None)
    text = kwargs.get("text", "none")
    ttl = kwargs.get("ttl", None)

    # Add the message to the queue
    engine.message_queue.append(msg.Message(pos=position, text=text, ttl=ttl))

    #Return success
    return 0