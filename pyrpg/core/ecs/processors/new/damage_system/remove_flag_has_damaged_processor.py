__all__ = ['RemoveFlagHasDamagedProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_has_damaged import FlagHasDamaged

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasDamagedProcessor(Processor):
    ''' Removes FlagHasDamaged flag after the cycle.

    Involved components:
        -   FlagHasDamaged

    Related processors:
        -   GenerateDamageProcessor
        -   PerformDamageProcessor

    What if this processor is disabled?

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.damage_system:PerformDamageProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the FlagHasDamaged flag.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(FlagHasDamaged):

            self.world.remove_component(ent, FlagHasDamaged)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasDamaged" was removed.')

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
