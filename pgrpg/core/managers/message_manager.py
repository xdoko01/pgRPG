# Create logger
import logging
logger = logging.getLogger(__name__)

from pgrpg.core.messages.messages import Message
from pygame.time import get_ticks

_message_queue = []
logger.info(f'MessageManager initiated.')


def get_messages() -> list:
    '''Selects and returns messages for display.'''

    # Get current time to evaluate ttl of the message
    current_time = get_ticks()

    # Remove all the expired messages from the message queue
    global _message_queue
    _message_queue = [msg for msg in _message_queue if current_time - msg.created < msg.ttl]

    return _message_queue

def add_message(message: Message) -> None:
    '''Adds new game message to the queue.'''

    _message_queue.append(message)
    logger.info(f'Message "{message.text}" added.')

def clear_messages() -> None:
    '''Clears the message queue.'''

    del _message_queue[:]
    logger.info(f'All messages cleared.')
