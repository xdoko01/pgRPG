__all__ = ['RemoveFlagHasNoHealthProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_no_health import FlagHasNoHealth

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasNoHealthProcessor(Processor):
    ''' Removes FlagNoHealth flag after the cycle.

    Involved components:
        -   FlagHasNoHealth

    Related processors:
        -   GenerateDamageProcessor
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   sound efects upon dying are repeating

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        #'allOf', 'damage_system:PerformDamageProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the FlagNoHealth flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagHasNoHealth):

            self.world.remove_component(ent, FlagHasNoHealth)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasNoHealth" was removed.')

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
