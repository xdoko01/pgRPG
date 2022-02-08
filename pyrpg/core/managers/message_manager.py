import pygame
import logging

from pyrpg.core.messages.messages import Message

# Create logger
logger = logging.getLogger(__name__)

class MessageManager():

    def __init__(self) -> None:

        self._message_queue = []
        logger.info(f'MessageManager initiated.')

    def get_messages(self) -> list:
        '''Selects and returns messages for display.'''

        # Get current time to evaluate ttl of the message
        current_time = pygame.time.get_ticks()

        # Remove all the expired messages from the message queue
        self._message_queue = [msg for msg in self._message_queue if current_time - msg.created < msg.ttl]

        return self._message_queue

    def add_message(self, message: Message) -> None:
        '''Adds new game message to the queue.'''

        self._message_queue.append(message)
        logger.info(f'Message "{message.text}" added.')

    def clear_messages(self) -> None:
        '''Clears the message queue.'''

        del self._message_queue[:]
        logger.info(f'All messages cleared.')
