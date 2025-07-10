__all__ = ['GenerateDestroyOnStoppedMovementProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_stopped_movement import FlagHasStoppedMovement
from core.components.is_destroyed import IsDestroyed
from core.components.movable import Movable
from core.components.destroy_on_no_movement import DestroyOnNoMovement

# Logger init
logger = logging.getLogger(__name__)

class GenerateDestroyOnStoppedMovementProcessor(Processor):
    ''' Marks entity as IsDestroyed if it has moved and stopped.

    Involved components:
        -   FlagHasStoppedMovement
        -   IsDestroyed
        -   Movable

    Related processors:
        -   PerformMovementProcessor

    What if this processor is disabled?
        -   projectile is not destroyed when stopped

    Where the processor should be planned?
        -   after PerformMovementProcessor
        -   before PerformDestroyEntitiesProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'movement_system.perform_movement_processor:PerformMovementProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Generates the IsDestroyed component.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_has_stopped_movement, movable, destroy_on_no_movement) in self.world.get_components(FlagHasStoppedMovement, Movable, DestroyOnNoMovement):

            self.world.add_component(ent, IsDestroyed(ttl=destroy_on_no_movement.ttl))
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "IsDestroyed" was added.')

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
