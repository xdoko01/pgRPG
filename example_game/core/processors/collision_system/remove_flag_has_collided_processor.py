__all__ = ['RemoveFlagHasCollidedProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_collided import FlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasCollidedProcessor(Processor):
    ''' Removes FlagHasCollided flag after the cycle.

    Involved components:
        -   FlagHasCollided

    Related processors:
        -   NewGenerateCollisionsProcessor
        -   NewGenerateCollisionsFullProcessor

    What if this processor is disabled?
        -   entities are constantly colliding

    Where the processor should be planned?
        -   after NewGenerateCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        #'allOf','collision_system:GenerateCollisionsProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the FlagHasCollided flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagHasCollided):

            self.world.remove_component(ent, FlagHasCollided)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasCollided" was removed.')

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
