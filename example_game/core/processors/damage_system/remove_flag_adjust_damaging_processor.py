__all__ = ['RemoveFlagAdjustDamagingProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_adjust_damaging import FlagAdjustDamaging

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagAdjustDamagingProcessor(Processor):
    ''' Removes FlagAdjustDamaging flag after the cycle.

    Involved components:
        -   FlagAdjustDamaging

    Related processors:
        -   PerformAdjustDamagingProcessor

    What if this processor is disabled?

    Where the processor should be planned?
        -   after PerformAdjustDamagingProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'damage_system:PerformAdjustDamagingProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the FlagAdjustDamaging flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagAdjustDamaging):

            self.world.remove_component(ent, FlagAdjustDamaging)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagAdjustDamaging" was removed.')

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
