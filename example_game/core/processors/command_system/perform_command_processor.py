__all__ = ['PerformCommandProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Logger init
logger = logging.getLogger(__name__)

class PerformCommandProcessor(Processor):
    ''' Calls comand queue handler with additional parameters about
    input events (keys, events).
    '''

    PREREQ = [
    ]

    #def __init__(self, FNC_GET_ENTITY_ID, FNC_PROCESS_COMMANDS, REF_ECS_MNG, *args, **kwargs):
    def __init__(self, FNC_PROCESS_COMMANDS, REF_ECS_MNG, *args, **kwargs):

        super().__init__(*args, **kwargs)

        #self.get_entity_from_alias_fnc = FNC_GET_ENTITY_ID
        self.game_commands_handler = FNC_PROCESS_COMMANDS
        self.ecs_mng = REF_ECS_MNG


    def process(self, *args, **kwargs):
        ''' Call external function that processes all commands
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # In order to pass pressed keys to commands (such as ENTER is pressed)
        keys = kwargs.get('keys', [])
        events = kwargs.get('events', [])

        # Call command handler - processing commands from the queue
        #self.game_commands_handler(self.get_entity_from_alias_fnc, world=self.world, ecs_mng=self.ecs_mng, keys=keys, events=events)
        self.game_commands_handler(ecs_mng=self.ecs_mng, keys=keys, events=events)

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
