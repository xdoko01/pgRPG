__all__ = ['PerformCommandProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Logger init
logger = logging.getLogger(__name__)

class PerformCommandProcessor(Processor):
    ''' Calls comand queue handler with additional parameters about
    input events (keys, events).
    '''

    PREREQ = [
    ]

    def __init__(self, FNC_GET_ENTITY_ID, FNC_PROCESS_COMMANDS):
        super().__init__()

        self.get_entity_from_alias_fnc = FNC_GET_ENTITY_ID
        self.game_commands_handler = FNC_PROCESS_COMMANDS

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Call external function that processes all commands
        '''
        self.cycle += 1

        # In order to pass pressed keys to commands (such as ENTER is pressed)
        keys = kwargs.get('keys', [])
        events = kwargs.get('events', [])

        # Call command handler - processing commands from the queue
        self.game_commands_handler(self.get_entity_from_alias_fnc, world=self.world, keys=keys, events=events)
        logger.debug(f'({self.cycle}) - Command handler executed.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
