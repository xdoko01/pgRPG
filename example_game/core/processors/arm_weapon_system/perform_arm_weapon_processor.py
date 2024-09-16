__all__ = ['PerformArmWeaponProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.has_weapon import HasWeapon
from core.components.weapon_in_use import WeaponInUse
from core.components.flag_is_about_to_arm_weapon import FlagIsAboutToArmWeapon
from core.components.flag_has_armed_weapon import FlagHasArmedWeapon
from core.components.flag_was_armed_as_weapon_by import FlagWasArmedAsWeaponBy

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformArmWeaponProcessor(Processor):
    ''' Detects entities that are about to arm weapon and performs
    the actual arming, if the fighter is capable.

    Involved components:
        -   HasWeapon
        -   WeaponInUse
        -   FlagIsAboutToArmWeapon
        -   FlagHasArmedWeapon
        -   FlagWasArmedAsWeaponBy

    Related processors:
        -   GenerateArmWeaponProcessor
        -   RemoveFlagIsAboutToArmWeaponProcessor
        -   RemoveFlagWasArmedAsWeaponByProcessor
        -   RemoveFlagHasArmedWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being armed

    Where the processor should be planned?
        -   after GenerateArmWeaponProcessor
        -   before RemoveFlagIsAboutToArmWeaponProcessor
        -   before RemoveFlagWasArmedAsWeaponByProcessor
        -   before RemoveFlagHasArmedWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf', 'new.arm_weapon_system.generate_arm_weapon_processor:GenerateArmWeaponProcessor']

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects fighters that are about to arme the weapon and performs
        the actual arming, if the fighter is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have HasWeapon and FlagIsAboutToArmWeapon - those are candidates for successful arming
        for ent_fighter, (has_weapon, flag_is_about_to_arm_weapon) in self.world.get_components(HasWeapon, FlagIsAboutToArmWeapon):

            # Check that there is place for the weapon to be armed
            # If there is a place, put the reference to HasWeapon slot
            # If there is not a place, rewrite it anyway - all is in inventory so the old weapon will remain in the inventory. Later, we can force changing of
            # some weapon by simply assigning FlagIsAboutToArmWeapon to some fighter and this processor will change it
            try:
                has_weapon.weapons[flag_is_about_to_arm_weapon.type]["weapon"] = flag_is_about_to_arm_weapon.weapon
            except KeyError:
                logger.error(f'({self.cycle}) - Weapon {flag_is_about_to_arm_weapon.weapon} is of incorrect type {flag_is_about_to_arm_weapon.type}.')
                raise ValueError

            # Report that arming a weapon occured - generate event
            arm_weapon_event = Event('WEAPON_ARMED', flag_is_about_to_arm_weapon.weapon, ent_fighter, params={'weapon' : flag_is_about_to_arm_weapon.weapon, 'fighter' : ent_fighter})
            self.add_event_fnc(arm_weapon_event)

            # Assign FlagWasArmedAsWeaponBy component to the weapon entity
            self.world.add_component(flag_is_about_to_arm_weapon.weapon, FlagWasArmedAsWeaponBy(fighter=ent_fighter))
            logger.debug(f'({self.cycle}) - Weapon {flag_is_about_to_arm_weapon.weapon} ({flag_is_about_to_arm_weapon.type}) was armed by entity {ent_fighter}.')

            # Assign FlagHasArmedWeapon component to the fighter entity
            self.world.add_component(ent_fighter, FlagHasArmedWeapon(weapon=flag_is_about_to_arm_weapon.weapon))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} has armed weapon {flag_is_about_to_arm_weapon.weapon} of type {flag_is_about_to_arm_weapon.type}.')

            # Assign WeaponInUse component to the fighter entity ['type', 'action', 'idle_action']
            self.world.add_component(ent_fighter, WeaponInUse(type=flag_is_about_to_arm_weapon.type))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} is now using weapon {flag_is_about_to_arm_weapon.weapon} of type {flag_is_about_to_arm_weapon.type}.')

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

