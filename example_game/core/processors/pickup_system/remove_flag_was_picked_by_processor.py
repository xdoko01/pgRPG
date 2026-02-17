__all__ = ['RemoveFlagWasPickedByProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_picked_by import FlagWasPickedBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasPickedByProcessor(Processor):
    ''' Removes the flag that the item was picked.

    Involved components:
        -   FlagWasPickedBy

    Related processors:
        -   GeneratePickupProcessor
        -   PerformPickupProcessor
        -   RemoveFlagIsAboutToPickEntityProcessor
        -   RemoveFlagHasPickedProcessor

    What if this processor is disabled?
        -   unexpected behavior during picking of the item

    Where the processor should be planned?
        -   after PerformPickupProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'pickup_system.perform_pickup_processor:PerformPickupProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the item was picked.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagWasPickedBy):

            self.world.remove_component(ent, FlagWasPickedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasPickedBy" was removed.')

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

