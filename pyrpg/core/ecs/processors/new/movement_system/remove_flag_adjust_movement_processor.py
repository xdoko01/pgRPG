__all__ = ['RemoveFlagAdjustMovementProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_adjust_movement import FlagAdjustMovement

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagAdjustMovementProcessor(Processor):
    ''' Removes FlagAdjustMovement flag after the cycle.

    Involved components:
        -   FlagAdjustMovement

    Related processors:
        -   PerformMovementProcessor
        -   PerformAdjustMovementProcessor

    What if this processor is disabled?
        -   movement of projectile is constantly changing

    Where the processor should be planned?
        -   after PerformAdjustMovementProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.movement_system.perform_adjust_movement_processor:PerformAdjustMovementProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the FlagHasCollided flag.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(FlagAdjustMovement):

            self.world.remove_component(ent, FlagAdjustMovement)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagAdjustMovement" was removed.')

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
