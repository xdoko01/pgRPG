"""Manage the in-game message log with time-to-live filtering.

Messages are added by processors and scripts, then retrieved each frame
with expired entries automatically pruned based on ``pygame.time.get_ticks``.

Module Globals:
    _message_queue: List of active Message instances.
"""

import logging
logger = logging.getLogger(__name__)

from pgrpg.core.messages.messages import Message
from pygame.time import get_ticks

_message_queue = []
logger.info(f'MessageManager initiated.')


def get_messages() -> list:
    """Return active messages, pruning any that have exceeded their TTL."""

    # Get current time to evaluate ttl of the message
    current_time = get_ticks()

    # Remove all the expired messages from the message queue
    global _message_queue
    _message_queue = [msg for msg in _message_queue if current_time - msg.created < msg.ttl]

    return _message_queue

def add_message(message: Message) -> None:
    """Append a new message to the queue.

    Args:
        message: A Message instance with text, created time, and TTL.
    """

    _message_queue.append(message)
    logger.info(f'Message "{message.text}" added.')

def clear_messages() -> None:
    """Remove all messages from the queue."""

    del _message_queue[:]
    logger.info(f'All messages cleared.')
