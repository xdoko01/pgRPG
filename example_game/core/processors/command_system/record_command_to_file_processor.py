__all__ = ['RecordCommandToFileProcessor']

import logging
import json

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Logger init
logger = logging.getLogger(__name__)

class RecordCommandToFileProcessor(Processor):
    ''' Dumps the command queue and saves it into the defined file.
    '''

    PREREQ = ['allOf',
        'command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor'
    ]

    def __init__(self, FNC_GET_COMMANDS, file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Reference to command queue
        self.get_commands_fnc = FNC_GET_COMMANDS

        # File handler
        self.fh = open(file, 'w')

        # Counter of process cycles - initiate to 0 first cycle will be 1
        self.cycle_counter = 0


    def process(self, *args, **kwargs):
        ''' Store the whole queue to the file - every cycle on every line
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Increase cycle counter
        self.cycle_counter += 1

        # If there is something in the command queue, prepare dict and write it
        if self.get_commands_fnc():
            new_rec = { 'cycle' : self.cycle_counter, 'commands' : self.get_commands_fnc()}
            json.dump(new_rec, self.fh)
            self.fh.write('\n') # one cycle per row
            logger.debug(f'({self.cycle}) - Command queue stored.')

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
        # Close the file
        self.fh.close()
