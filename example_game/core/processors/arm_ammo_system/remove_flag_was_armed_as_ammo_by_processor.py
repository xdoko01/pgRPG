__all__ = ['RemoveFlagWasArmedAsAmmoByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_armed_as_ammo_by import FlagWasArmedAsAmmoBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasArmedAsAmmoByProcessor(Processor):
    ''' Removes the flag that the entity was armed as an ammo.

    Involved components:
        -   FlagWasArmedAsAmmoBy

    Related processors:
        -   GenerateArmAmmoProcessor
        -   PerformArmAmmoProcessor
        -   RemoveFlagIsAboutToArmAmmoProcessor
        -   RemoveFlagHasArmedAmmoProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of an ammo

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
        ''' Removes the flag that the entity was armed as an ammo.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagWasArmedAsAmmoBy):

            self.world.remove_component(ent, FlagWasArmedAsAmmoBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasArmedAsAmmoBy" was removed.')

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

