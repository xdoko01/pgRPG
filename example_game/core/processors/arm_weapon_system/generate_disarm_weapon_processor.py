__all__ = ['GenerateDisarmWeaponProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.weapon import Weapon
from core.components.has_weapon import HasWeapon
from core.components.flag_was_dropped_by import FlagWasDroppedBy
from core.components.flag_is_about_to_disarm_weapon import FlagIsAboutToDisarmWeapon

# Logger init
logger = logging.getLogger(__name__)

class GenerateDisarmWeaponProcessor(Processor):
    ''' Detects entities that act as weapon + have been dropped and assigns
    the FlagIsAboutToDisarmWeapon to all droppers.

    Involved components:
        -   Weapon
        -   FlagWasDroppedBy
        -   FlagIsAboutToDisarmWeapon

    Related processors:
        -   PerformDisarmWeaponProcessor
        -   RemoveFlagIsAboutToDisarmWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being disarmed

    Where the processor should be planned?
        -   after PerformDropProcessor
        -   before PerformDisarmWeaponProcessor
        -   before RemoveFlagIsAboutToDisarmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf', 'drop_system.perform_drop_processor:PerformDropProcessor']

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        '''  Detects entities that are weapons + have been picked  and assigns
        the FlagIsAboutToArmWeapon to their pickers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Used components
        weapon: Weapon 
        flag_was_dropped_by: FlagWasDroppedBy
        has_weapon: HasWeapon

        # Get all entities that have Weapon and FlagWasDroppedBy - those are candidates for disarming
        for ent_weapon, (weapon, flag_was_dropped_by) in self.world.get_components(Weapon, FlagWasDroppedBy):

            # Do not generate if the weapon is not armed
            has_weapon = self.world.try_component(flag_was_dropped_by.dropper, HasWeapon)
            if has_weapon.weapons[weapon.type]["weapon"] != ent_weapon: continue

            # Otherwise it is armed and can be disarmed
            self.world.add_component(flag_was_dropped_by.dropper, FlagIsAboutToDisarmWeapon(weapon=ent_weapon, type=weapon.type))
            logger.debug(f'({self.cycle}) - Entity {flag_was_dropped_by.dropper} is trying to disarm as weapon entity {ent_weapon}.')


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

