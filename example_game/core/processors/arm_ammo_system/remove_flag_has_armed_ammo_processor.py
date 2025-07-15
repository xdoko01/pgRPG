__all__ = ['RemoveFlagHasArmedAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_armed_ammo import FlagHasArmedAmmo

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagHasArmedAmmoProcessor(Processor):
    ''' Removes the flag that fighter has armed an entity.

    Involved components:
        -   FlagHasArmedAmmo

    Related processors:
        -   GenerateArmAmmoProcessor
        -   PerformArmAmmoProcessor
        -   RemoveFlagIsAboutToArmAmmoProcessor
        -   RemoveFlagWasArmedAsAmmoByProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of an ammo of the item

    Where the processor should be planned?
        -   after PerformArmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_ammo_system.perform_arm_ammo_processor:PerformArmAmmoProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the item was picked.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagHasArmedAmmo):

            self.world.remove_component(ent, FlagHasArmedAmmo)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasArmedAmmo" was removed.')

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

