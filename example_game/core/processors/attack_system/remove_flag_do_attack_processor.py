__all__ = ['RemoveFlagDoAttackProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_do_attack import FlagDoAttack

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagDoAttackProcessor(Processor):
    ''' Removes the flag that fighter has attacked.

    Involved components:
        -   FlagDoAttack

    Related processors:

    What if this processor is disabled?
        -   entity attacks always regardless on input

    Where the processor should be planned?
        -   after PerformCommandProcessor
        -   after PerformActionAnimationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        #'allOf', 'command_system.perform_command_processor:PerformCommandProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity has attacked.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagDoAttack):

            self.world.remove_component(ent, FlagDoAttack)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagDoAttack" was removed.')

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

