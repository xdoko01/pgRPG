__all__ = ['PerformDisarmWeaponProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.has_weapon import HasWeapon
from core.components.weapon_in_use import WeaponInUse
from core.components.flag_is_about_to_disarm_weapon import FlagIsAboutToDisarmWeapon
from core.components.flag_has_disarmed_weapon import FlagHasDisarmedWeapon
from core.components.flag_was_disarmed_as_weapon_by import FlagWasDisarmedAsWeaponBy
from core.components.render_data_from_parent import RenderDataFromParent
from core.components.flag_has_dropped import FlagHasDropped

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformDisarmWeaponProcessor(Processor):
    ''' Detects entities that are about to disarm weapon and performs
    the actual disarming, if the fighter is capable.

    Involved components:
        -   HasWeapon
        -   WeaponInUse
        -   FlagIsAboutToDisarmWeapon
        -   FlagHasDisarmedWeapon
        -   FlagWasDisarmedAsWeaponBy

    Related processors:
        -   GenerateDisarmWeaponProcessor
        -   RemoveFlagIsAboutToDisarmWeaponProcessor
        -   RemoveFlagWasDisarmedAsWeaponByProcessor
        -   RemoveFlagHasDisarmedWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being disarmed

    Where the processor should be planned?
        -   after GenerateDisarmWeaponProcessor
        -   before RemoveFlagIsAboutToDisarmWeaponProcessor
        -   before RemoveFlagWasDisarmedAsWeaponByProcessor
        -   before RemoveFlagHasDisarmedWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'allOf', 
            'arm_weapon_system.generate_disarm_weapon_processor:GenerateDisarmWeaponProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        '''Detects fighters that are about to disarm the weapon and performs
        the actual disarming, if the fighter is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have HasWeapon and FlagIsAboutToDisarmWeapon - those are candidates for successful disarming
        #for ent_fighter, (has_weapon, flag_is_about_to_disarm_weapon, weapon_in_use) in self.world.get_components(HasWeapon, FlagIsAboutToDisarmWeapon, WeaponInUse):
        for ent_fighter, (has_weapon, flag_is_about_to_disarm_weapon) in self.world.get_components(HasWeapon, FlagIsAboutToDisarmWeapon):

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
            # Remove the rendering data necessery to render weapon together with entity animations (no longer needed on disarmed weapon)
            # It is possible that this component was already removed by disarm ammo system - in case weapon and ammo pack are merged into one entity
            try:
                self.world.remove_component(flag_is_about_to_disarm_weapon.weapon, RenderDataFromParent)
                logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_disarm_weapon.weapon} - RenderDataFromParent  component was removed.')
            except KeyError:
               logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_disarm_weapon.weapon} - has no RenderDataFromParent  component. Continuing.')
            '''

            # Report that disarming a weapon occured - generate event
            arm_weapon_event = Event('WEAPON_DISARMED', flag_is_about_to_disarm_weapon.weapon, ent_fighter, params={'weapon' : flag_is_about_to_disarm_weapon.weapon, 'fighter' : ent_fighter})
            self.add_event_fnc(arm_weapon_event)

            # Assign FlagWasDisarmedAsWeaponBy component to the weapon entity
            self.world.add_component(flag_is_about_to_disarm_weapon.weapon, FlagWasDisarmedAsWeaponBy(fighter=ent_fighter))
            logger.debug(f'({self.cycle}) - Weapon {flag_is_about_to_disarm_weapon.weapon} ({flag_is_about_to_disarm_weapon.type}) was disarmed by entity {ent_fighter}.')

            # Assign FlagHasDisarmedWeapon component to the fighter entity
            self.world.add_component(ent_fighter, FlagHasDisarmedWeapon(weapon=flag_is_about_to_disarm_weapon.weapon))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} has disarmed weapon {flag_is_about_to_disarm_weapon.weapon} of type {flag_is_about_to_disarm_weapon.type}.')

            # Remove the disarmed weapon from HasWeapon component, if not already substituted by newly armed weapon
            if has_weapon.weapons[flag_is_about_to_disarm_weapon.type]["weapon"] == flag_is_about_to_disarm_weapon.weapon:
                
                # Remove weapon from weapons available for fight
                logger.debug(f'({self.cycle}) - Entity {ent_fighter} - Weapon in HasWeapon was set from {has_weapon.weapons[flag_is_about_to_disarm_weapon.type]["weapon"]} to None.')
                has_weapon.weapons[flag_is_about_to_disarm_weapon.type]["weapon"] = None

            '''
            # Remove the WeaponInUse component, if it is pointing do disarmed weapon
            if has_weapon.weapons[weapon_in_use.type]["weapon"] is None: # and weapon_in_use.type == flag_is_about_to_disarm_weapon.type and 
                self.world.remove_component(ent_fighter, WeaponInUse)
                logger.debug(f'({self.cycle}) - Entity {ent_fighter} - WeaponInUse component was removed.')
            '''

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

