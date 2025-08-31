__all__ = ['PerformDisarmAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.has_weapon import HasWeapon
from core.components.weapon_in_use import WeaponInUse
from core.components.flag_is_about_to_disarm_ammo import FlagIsAboutToDisarmAmmo
from core.components.flag_has_disarmed_ammo import FlagHasDisarmedAmmo
from core.components.flag_was_disarmed_as_ammo_by import FlagWasDisarmedAsAmmoBy
from core.components.render_data_from_parent import RenderDataFromParent

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformDisarmAmmoProcessor(Processor):
    ''' Detects entities that are about to disarm ammo and performs
    the actual disarming, if the fighter is capable.

    Involved components:
        -   HasWeapon
        -   WeaponInUse
        -   FlagIsAboutToDisarmAmmo
        -   FlagHasDisarmedAmmo
        -   FlagWasDisarmedAsAmmoBy

    Related processors:
        -   GenerateDisarmAmmoProcessor
        -   RemoveFlagIsAboutToDisarmWeaponProcessor
        -   RemoveFlagWasDisarmedAsWeaponByProcessor
        -   RemoveFlagHasDisarmedWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being disarmed

    Where the processor should be planned?
        -   after GenerateDisarmAmmoProcessor
        -   before RemoveFlagIsAboutToDisarmAmmoProcessor
        -   before RemoveFlagWasDisarmedAsAmmoByProcessor
        -   before RemoveFlagHasDisarmedAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'allOf', 
            'arm_ammo_system.generate_disarm_ammo_processor:GenerateDisarmAmmoProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        '''Detects fighters that are about to disarm the ammo and performs
        the actual disarming, if the fighter is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have HasWeapon and FlagIsAboutToDisarmAmmo - those are candidates for successful disarming
        for ent_fighter, (has_weapon, flag_is_about_to_disarm_ammo) in self.world.get_components(HasWeapon, FlagIsAboutToDisarmAmmo):

            logger.debug(f'({self.cycle}) - Entity {ent_fighter} is trying to disarm the ammo.')

            """
            ARM WEAPON
             - mark currently used weapon for disarming (WeaponInUse)
             - arm new weapon in both HasWeapon and WeaponInUse
            DISARM WEAPON
             - 2 cases
              - AFRER ARMING a new weapon - !!!new weapon already can be armed in HasWeapon and WeaponInUse!!! - by FlagHasArmedWeapon component
                - set the disarm and render flags on the disarmed weapon
              - AFTER DROPPING of armed weapon - !!! if result of dropping the old weapon is still in use in HasWeapon and WeaponInUse!!!
                - set the disarm and render flags on the disarmed weapon
                - remove from HasWeapon
                - remove weaponInUse
             """

            '''
            # Remove the rendering data necessary to render ammo together with entity animations (no longer needed on disarmed weapon)
            # It is possible that this component was already removed by disarm weapon system - in case weapon and ammo pack are merged into one entity
            try:
                self.world.remove_component(flag_is_about_to_disarm_ammo.ammo, RenderDataFromParent)
                logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_disarm_ammo.ammo} - RenderDataFromParent  component was removed.')
            except KeyError:
                logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_disarm_ammo.ammo} - has no RenderDataFromParent  component. Continuing.')
            '''
            
            # Report that disarming an ammo occured - generate event
            arm_ammo_event = Event('AMMO_PACK_DISARMED', flag_is_about_to_disarm_ammo.ammo, ent_fighter, params={'ammo' : flag_is_about_to_disarm_ammo.ammo, 'fighter' : ent_fighter})
            self.add_event_fnc(arm_ammo_event)

            # Assign FlagWasDisarmedAsAmmoBy component to the ammo entity
            self.world.add_component(flag_is_about_to_disarm_ammo.ammo, FlagWasDisarmedAsAmmoBy(fighter=ent_fighter))
            logger.debug(f'({self.cycle}) - Ammo {flag_is_about_to_disarm_ammo.ammo} ({flag_is_about_to_disarm_ammo.type}) was disarmed by entity {ent_fighter}.')

            # Assign FlagHasDisarmedAmmo component to the fighter entity
            self.world.add_component(ent_fighter, FlagHasDisarmedAmmo(ammo=flag_is_about_to_disarm_ammo.ammo))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} has disarmed ammo {flag_is_about_to_disarm_ammo.ammo} of type {flag_is_about_to_disarm_ammo.type}.')

            # Remove the disarmed ammo from HasWeapon component, if not already substituted by newly armed weapon
            if has_weapon.weapons[flag_is_about_to_disarm_ammo.type]["generator"] == flag_is_about_to_disarm_ammo.ammo:
                
                # Remove ammo 
                logger.debug(f'({self.cycle}) - Entity {ent_fighter} - AmmoPack in HasWeapon was set from {has_weapon.weapons[flag_is_about_to_disarm_ammo.type]["generator"]} to None.')
                has_weapon.weapons[flag_is_about_to_disarm_ammo.type]["generator"] = None


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

