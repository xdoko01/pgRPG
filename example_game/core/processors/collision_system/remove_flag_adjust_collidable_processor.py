__all__ = ['RemoveFlagAdjustCollidableProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_adjust_collidable import FlagAdjustCollidable

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagAdjustCollidableProcessor(Processor):
    ''' Removes FlagAdjustCollision flag after the cycle.

    Involved components:
        -   FlagAdjustCollidable

    Related processors:
        -   GenerateCollisionsProcessor
        -   PerformAdjustCollidableProcessor

    What if this processor is disabled?
        -   collision zone is continuously changing

    Where the processor should be planned?
        -   after PerformAdjustCollidableProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        #'allOf', 'collision_system.perform_adjust_collidable_processor:PerformAdjustCollidableProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the FlagAdjustCollidable flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagAdjustCollidable):

            self.world.remove_component(ent, FlagAdjustCollidable)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagAdjustCollision" was removed.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
