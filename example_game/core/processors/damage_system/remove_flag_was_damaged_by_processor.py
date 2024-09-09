__all__ = ['RemoveFlagWasDamagedByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.flag_was_damaged_by import FlagWasDamagedBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasDamagedByProcessor(Processor):
    ''' Removes FlagWasDamagedBy flag after the cycle.

    Involved components:
        -   FlagWasDamagedBy

    Related processors:
        -   GenerateDamageProcessor
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   no score counting

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.damage_system:PerformDamageProcessor'
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

        for ent, (_) in self.world.get_components(FlagWasDamagedBy):

            self.world.remove_component(ent, FlagWasDamagedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasDamagedBy" was removed.')

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
