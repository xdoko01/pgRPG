__all__ = ['RemoveFlagHasStoppedMovementProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_stopped_movement import FlagHasStoppedMovement

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasStoppedMovementProcessor(Processor):
    ''' Removes FlagHasStoppedMovement flag after the cycle.

    Involved components:
        -   FlagHasStoppedMovement

    Related processors:
        -   PerformMovementProcessor
        -   PerformDestroyOnStoppedMovementProcessor

    What if this processor is disabled?

    Where the processor should be planned?
        -   after PerformDestroyOnStoppedMovementProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.movement_system.perform_movement_processor:PerformMovementProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the FlagHasCollided flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_component(FlagHasStoppedMovement):
            self.world.remove_component(ent, FlagHasStoppedMovement)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasStoppedMovement" was removed.')

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
