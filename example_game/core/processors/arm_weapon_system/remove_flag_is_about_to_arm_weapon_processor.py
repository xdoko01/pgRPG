__all__ = ['RemoveFlagIsAboutToArmWeaponProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_is_about_to_arm_weapon import FlagIsAboutToArmWeapon

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToArmWeaponProcessor(Processor):
    ''' Removes the flag that the entity has been considered for picking
    up of a weapon the end of the cycle.

    Involved components:
        -   FlagIsAboutToArmWeapon

    Related processors:
        -   GenerateArmWeaponProcessor
        -   PerformArmWeaponProcessor
        -   RemoveFlagWasArmedAsWeaponByProcessor
        -   RemoveFlagHasArmedWeaponProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of a weapon

    Where the processor should be planned?
        -   after PerformArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_weapon_system.perform_arm_weapon_processor:PerformArmWeaponProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for arming
        a weapon at the end of the cycle.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagIsAboutToArmWeapon):

            self.world.remove_component(ent, FlagIsAboutToArmWeapon)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToArmWeapon" was removed.')

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

