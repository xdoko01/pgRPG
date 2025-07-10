__all__ = ['PerformAdjustDamagingProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.damaging import Damaging
from core.components.flag_adjust_damaging import FlagAdjustDamaging

# Logger init
logger = logging.getLogger(__name__)

class PerformAdjustDamagingProcessor(Processor):
    ''' Updates Damaging component based on FlagAdjustDamaging
    component.

    Involved components:
        -   FlagAdjustDamaging
        -   Damaging

    Related processors:
        -   RemoveFlagAdjustDamagingProcessor

    What if this processor is disabled?
        -   score will be not calculated on the parent

    Where the processor should be planned?
        -   before RemoveFlagAdjustDamagingProcessor
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformAdjustDamagingProcessor processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Process entities having Damaging component.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (damaging, flag_adjust_damaging) in self.world.get_components(Damaging, FlagAdjustDamaging):

            # Update parent
            logger.debug(f'({self.cycle}) - Entity {ent} - original parent: {damaging.parent}')
            damaging.parent = flag_adjust_damaging.parent
            logger.debug(f'({self.cycle}) - Entity {ent} - new parent: {damaging.parent}')

            # Update damage
            logger.debug(f'({self.cycle}) - Entity {ent} - original damage: {damaging.damage}')
            logger.debug(f'({self.cycle}) - Entity {ent} - requested change in damage: {flag_adjust_damaging.damage_fnc}')
            for f in flag_adjust_damaging.damage_fnc: damaging.damage = f(damaging.damage)
            logger.debug(f'({self.cycle}) - Entity {ent} - new damage: {damaging.damage}')


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
