__all__ = ['RemoveFlagHasDisarmedAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_disarmed_ammo import FlagHasDisarmedAmmo

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasDisarmedAmmoProcessor(Processor):
    ''' Removes the flag that fighter has disarmed an entity/ammo.

    Involved components:
        -   FlagHasDisarmedAmmo

    Related processors:
        -   GenerateDisarmAmmoProcessor
        -   PerformDisarmAmmoProcessor
        -   RemoveFlagIsAboutToDisarmAmmoProcessor
        -   RemoveFlagWasDisarmedAsAmmoByProcessor

    What if this processor is disabled?
        -   unexpected behavior during disarming of an ammo 

    Where the processor should be planned?
        -   after PerformDisarmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_ammo_system.perform_disarm_ammo_processor:PerformDisarmAmmoProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the ammo was disarmed.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagHasDisarmedAmmo):

            self.world.remove_component(ent, FlagHasDisarmedAmmo)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasDisarmedAmmo" was removed.')

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

