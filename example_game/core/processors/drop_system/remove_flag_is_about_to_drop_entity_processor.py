__all__ = ['RemoveFlagIsAboutToDropEntityProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_is_about_to_drop_entity import FlagIsAboutToDropEntity

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToDropEntityProcessor(Processor):
    ''' Removes the flag that the item has been considered for dropping
    at the end of the cycle.

    Involved components:
        -   FlagIsAboutToDropEntity

    Related processors:
        -   PerformDropProcessor
        -   RemoveFlagWasDroppedByProcessor
        -   RemoveFlagHasDroppedProcessor

    What if this processor is disabled?
        -   unexpected behavior during dropping of the item

    Where the processor should be planned?
        -   after PerformDropProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'drop_system.perform_drop_processor:PerformDropProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for dropping
        at the end of the cycle.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagIsAboutToDropEntity):

            self.world.remove_component(ent, FlagIsAboutToDropEntity)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToDropEntity" was removed.')

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

