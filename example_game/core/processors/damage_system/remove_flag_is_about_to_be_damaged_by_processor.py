__all__ = ['RemoveFlagIsAboutToBeDamagedByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_is_about_to_be_damaged_by import FlagIsAboutToBeDamagedBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToBeDamagedByProcessor(Processor):
    ''' Removes FlagIsAboutToBeDamagedBy flag after the cycle.

    Involved components:
        -   FlagIsAboutToBeDamagedBy

    Related processors:
        -   GenerateDamageProcessor
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   damage continues

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'damage_system:GenerateDamageProcessor'
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

        for ent, (_) in self.world.get_components(FlagIsAboutToBeDamagedBy):

            self.world.remove_component(ent, FlagIsAboutToBeDamagedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToBeDamagedBy" was removed.')

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
