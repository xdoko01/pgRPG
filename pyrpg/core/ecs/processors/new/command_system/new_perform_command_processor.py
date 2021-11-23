__all__ = ['NewPerformCommandProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors

# Logger init
logger = logging.getLogger(__name__)


class NewPerformCommandProcessor(esper.Processor):
    ''' Calls comand queue handler with additional parameters about
    input events (keys, events).
    '''

    PREREQ = [
        ('new.command_system.new_generate_command_from_input_processor', 'NewGenerateCommandFromInputProcessor'), 
        ('new.command_system.new_generate_command_from_brain_processor', 'NewGenerateCommandFromBrainProcessor')
        ]

    def __init__(self, game_commands_handler, debug=False):
        super().__init__()

        self.game_commands_handler = game_commands_handler
        self.debug = debug

    def process(self, *args, **kwargs):
        ''' Call external function that processes all commands
        '''
        self.cycle += 1

        # In order to pass pressed keys to commands (such as ENTER is pressed)
        keys = kwargs.get('keys', [])
        events = kwargs.get('events', [])
        quests = kwargs.get('quests', {})

        # Call command handler - processing commands from the queue
        self.game_commands_handler(keys=keys, events=events, debug=self.debug)
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
