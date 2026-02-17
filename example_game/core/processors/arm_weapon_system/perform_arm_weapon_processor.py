__all__ = ['PerformArmWeaponProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.has_weapon import HasWeapon
from core.components.weapon_in_use import WeaponInUse
from core.components.flag_is_about_to_arm_weapon import FlagIsAboutToArmWeapon
from core.components.flag_has_armed_weapon import FlagHasArmedWeapon
from core.components.flag_was_armed_as_weapon_by import FlagWasArmedAsWeaponBy
from core.components.flag_is_about_to_disarm_weapon import FlagIsAboutToDisarmWeapon
from core.components.flag_set_weapon_into_use import FlagSetWeaponIntoUse

# For creation of events
from pgrpg.core.events.event import Event

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
        -   FlagSetWeaponInUse

    Related processors:
        -   GenerateArmWeaponProcessor
        -   PerformSetWeaponInUseProcessor
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
    PREREQ = [
        'OR', 
            'arm_weapon_system.generate_arm_weapon_processor:GenerateArmWeaponProcessor', 
            'TRUE' # above processor for automatic arming of weapon is optional anc can be substituted by manual arm_weapon command
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        '''  Detects fighters that are about to arme the weapon and performs
        the actual arming, if the fighter is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have HasWeapon and FlagIsAboutToArmWeapon - those are candidates for successful arming
        for ent_fighter, (has_weapon, flag_is_about_to_arm_weapon, weapon_in_use) in self.world.get_components_opt(HasWeapon, FlagIsAboutToArmWeapon, optional=WeaponInUse):

            '''
            # First disarm currently used weapon
            weapon_in_use_entity_id = has_weapon.weapons[weapon_in_use.type]["weapon"] if weapon_in_use is not None else None

            logger.debug(f'({self.cycle}) - Currently used weapon before arming a new one {weapon_in_use_entity_id=}.')

            if weapon_in_use_entity_id is not None:
                    self.world.add_component(ent_fighter, FlagIsAboutToDisarmWeapon(weapon=weapon_in_use_entity_id, type=weapon_in_use.type))
                    logger.debug(f'({self.cycle}) - component FlagIsAboutToDisarmWeapon created with params {weapon_in_use_entity_id=}, {weapon_in_use.type=}.')
            '''
            ########
            # Automatically set the Weapon for usage
            ########

            # Set containing entity IDs that are currently armed on the position - as input into FlagSetWeaponIntoUse
            prev_armed_weapon_ammo_dict = has_weapon.weapons[weapon_in_use.type] if weapon_in_use is not None else dict()
            prev_armed_entity_ids = set(filter(lambda x: x is not None, prev_armed_weapon_ammo_dict.values()))

            # Automatically set the armed weapon for usage 
            self.world.add_component(ent_fighter, FlagSetWeaponIntoUse(type=flag_is_about_to_arm_weapon.type, prev_ent_ids=prev_armed_entity_ids))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} has set weapon {flag_is_about_to_arm_weapon.weapon} of type {flag_is_about_to_arm_weapon.type} in use.')

            ########
            # Disarm the weapon that is occupying the slot for the new weapon
            ########

            # Get entity_id of the currently armed weapon of the type that we are trying to arm
            armed_weapon_entity_id = has_weapon.weapons[flag_is_about_to_arm_weapon.type]["weapon"]
            logger.debug(f'({self.cycle}) - Currently armed weapon in the slot {flag_is_about_to_arm_weapon.type} before arming a new one {armed_weapon_entity_id=}.')

            # If trying to arm the weapon that is already armed, skip it and do nothing
            if armed_weapon_entity_id == flag_is_about_to_arm_weapon.weapon: 
                logger.debug(f'({self.cycle}) - Trying to arm the weapon that is already armed. {armed_weapon_entity_id=}. Skipping arming')
                continue

            # Disarm currently armed weapon occupying the position for the new weapon
            if armed_weapon_entity_id is not None :
                    self.world.add_component(ent_fighter, FlagIsAboutToDisarmWeapon(weapon=armed_weapon_entity_id, type=flag_is_about_to_arm_weapon.type))
                    logger.debug(f'({self.cycle}) - Component FlagIsAboutToDisarmWeapon created with params {armed_weapon_entity_id=}, {flag_is_about_to_arm_weapon.type=}.')

            ########
            # Arm the new weapon
            ########

            try:
                has_weapon.weapons[flag_is_about_to_arm_weapon.type]["weapon"] = flag_is_about_to_arm_weapon.weapon
                logger.debug(f'({self.cycle}) - HasWeapon component: {has_weapon.weapons}.')
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

            '''
            # Assign WeaponInUse component to the fighter entity ['type', 'action', 'idle_action']
            self.world.add_component(ent_fighter, WeaponInUse(type=flag_is_about_to_arm_weapon.type))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} is now using weapon {flag_is_about_to_arm_weapon.weapon} of type {flag_is_about_to_arm_weapon.type}. WeaponInUse assigned')
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

