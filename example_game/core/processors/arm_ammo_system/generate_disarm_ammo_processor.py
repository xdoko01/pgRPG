__all__ = ['GenerateDisarmAmmoProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.ammo_pack import AmmoPack
from core.components.has_weapon import HasWeapon
from core.components.flag_was_dropped_by import FlagWasDroppedBy
from core.components.flag_is_about_to_disarm_ammo import FlagIsAboutToDisarmAmmo

# Logger init
logger = logging.getLogger(__name__)

class GenerateDisarmAmmoProcessor(Processor):
    ''' Detects entities that act as ammo + have been dropped and assigns
    the FlagIsAboutToDisarmAmmo to all droppers.

    Involved components:
        -   AmmoPack
        -   FlagWasDroppedBy
        -   FlagIsAboutToDisarmAmmo

    Related processors:
        -   PerformDisarmAmmoProcessor
        -   RemoveFlagIsAboutToDisarmAmmoProcessor

    What if this processor is disabled?
        -   ammo is not being disarmed

    Where the processor should be planned?
        -   after PerformDropProcessor
        -   before PerformDisarmAmmoProcessor
        -   before RemoveFlagIsAboutToDisarmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf', 'drop_system.perform_drop_processor:PerformDropProcessor']

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        '''  Detects entities that are ammo + have been dropped  and assigns
        the FlagIsAboutToDisarmAmmo to their droppers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Used components
        ammo: AmmoPack 
        flag_was_dropped_by: FlagWasDroppedBy
        has_weapon: HasWeapon

        # Get all entities that have AmmoPack and FlagWasDroppedBy - those are candidates for disarming
        for ent_ammo, (ammo, flag_was_dropped_by) in self.world.get_components(AmmoPack, FlagWasDroppedBy):

            # Do not generate if the ammo is not armed
            has_weapon = self.world.try_component(flag_was_dropped_by.dropper, HasWeapon)
            if has_weapon.weapons[ammo.weapon]["generator"] != ent_ammo: continue

            # Otherwise ammo is armed and can be disarmed
            self.world.add_component(flag_was_dropped_by.dropper, FlagIsAboutToDisarmAmmo(ammo=ent_ammo, type=ammo.weapon))
            logger.debug(f'({self.cycle}) - Entity {flag_was_dropped_by.dropper} is trying to disarm as ammo entity {ent_ammo}.')


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

