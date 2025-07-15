__all__ = ['RemoveFlagIsAboutToPickEntityProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_is_about_to_pick_entity import FlagIsAboutToPickEntity

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToPickEntityProcessor(Processor):
    ''' Removes the flag that the item has been considered for picking
    at the end of the cycle.

    Involved components:
        -   FlagIsAboutToPickEntity

    Related processors:
        -   GeneratePickupProcessor
        -   PerformPickupProcessor
        -   RemoveFlagWasPickedByProcessor
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
        ''' Removes the flag that the item has been considered for picking
        at the end of the cycle.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagIsAboutToPickEntity):

            self.world.remove_component(ent, FlagIsAboutToPickEntity)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToPickEntity" was removed.')

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

