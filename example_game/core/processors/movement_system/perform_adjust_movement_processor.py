__all__ = ['PerformAdjustMovementProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.movable import Movable
from core.components.flag_adjust_movement import FlagAdjustMovement

# Logger init
logger = logging.getLogger(__name__)

class PerformAdjustMovementProcessor(Processor):
    ''' Updates Movable component based on FlagAdjustMovement
    component (movement).

    Involved components:
        -   FlagAdjustMovement
        -   Movable

    Related processors:
        -   RemoveFlagAdjustMovementProcessor

    What if this processor is disabled?
        -   movements of the projectile is not modified

    Where the processor should be planned?
        -   before RemoveFlagAdjustMovementProcessor
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformAdjustMovementProcessor processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Process entities having Motion and Position components. Basically,
        add motion diffs to the position represented by Position component.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (movable, flag_adjust_movement) in self.world.get_components(Movable, FlagAdjustMovement):

            # Update velocity
            logger.debug(f'({self.cycle}) - Entity {ent} - original movable velocity: {movable.velocity}')
            logger.debug(f'({self.cycle}) - Entity {ent} - requested additions to the velocity: {flag_adjust_movement.velocity_fnc}')
            for f in flag_adjust_movement.velocity_fnc: movable.velocity = f(movable.velocity)
            logger.debug(f'({self.cycle}) - Entity {ent} - new movable velocity: {movable.velocity}')

            # Update acceleration
            logger.debug(f'({self.cycle}) - Entity {ent} - original movable accelerate: {movable.accelerate}')
            logger.debug(f'({self.cycle}) - Entity {ent} - requested additions to the accelerate: {flag_adjust_movement.accelerate_fnc}')
            for f in flag_adjust_movement.accelerate_fnc: movable.accelerate = f(movable.accelerate)
            logger.debug(f'({self.cycle}) - Entity {ent} - new movable accelerate: {movable.accelerate}')

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
