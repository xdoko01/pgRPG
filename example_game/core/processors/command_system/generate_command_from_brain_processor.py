__all__ = ['GenerateCommandFromBrainProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.brain_ai import BrainAI

# Logger init
logger = logging.getLogger(__name__)

class GenerateCommandFromBrainProcessor(Processor):
    ''' Put command that is in the component's BrainAI (logic
    represented by any oc the CommandGenerators) and push it
    into the command queue.

    Involved components:
        -   BrainAI

    Related processors:
        -   GenerateCommandFromBTreeProcessor
        -   GenerateCommandFromBListProcessor
        -   GenerateCommandFromInputProcessor
        -   GenerateCommandFromFileProcessor
        -   PerformCommandProcessor

    What if this processor is disabled?
        -   commands stored in entity's brain are not processed

    Where the processor should be planned?
        -   after GenerateCommandFromInputProcessor
        -   before PerformCommandProcessor
    '''

    PREREQ = ['allOf',
        'new.command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor'
    ]

    def __init__(self, FNC_ADD_COMMAND, *args, **kwargs):
        ''' Init the processor.

        Parameters:
            :param add_command_fnc: Reference to the function that adds command to the command queue.
            :param add_command_fnc: reference to fnc
        '''
        super().__init__(*args, **kwargs)

        # Reference to function for adding to command queue
        self.add_command_fnc = FNC_ADD_COMMAND

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Puts the proper command to the command queue.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (brain) in self.world.get_component(BrainAI):

            cmd, _ = brain.generator.get_command() # CommandGenerator either returns (Command, is_first_call) or returns None - no command to process

            self.add_command_fnc(
                cmd=cmd,
                orig_entity_id=ent,
                generator=brain.generator # who needs to be notified that command has started and about the result of the command
            )

            logger.debug(f'({self.cycle}) - Entity {ent} - "{cmd=}" sent to the command manager - from brain.')


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
