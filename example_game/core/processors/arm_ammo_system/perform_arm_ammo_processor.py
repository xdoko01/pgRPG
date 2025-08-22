__all__ = ['PerformArmAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.has_weapon import HasWeapon
from core.components.has_inventory import HasInventory
from core.components.flag_was_armed_as_ammo_by import FlagWasArmedAsAmmoBy
from core.components.flag_is_about_to_arm_ammo import FlagIsAboutToArmAmmo
from core.components.flag_is_about_to_disarm_ammo import FlagIsAboutToDisarmAmmo
from core.components.flag_has_armed_ammo import FlagHasArmedAmmo
from core.components.weapon_in_use import WeaponInUse

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformArmAmmoProcessor(Processor):
    ''' Detects entities that are about to arm ammo and performs
    the actual arming, if the fighter is capable.

    Involved components:
        -   HasWeapon
        -   FlagIsAboutToArmAmmo
        -   FlagHasArmedAmmo
        -   FlagWasArmedAsAmmoBy

    Related processors:
        -   GenerateArmAmmoProcessor
        -   RemoveFlagIsAboutToArmAmmoProcessor
        -   RemoveFlagWasArmedAsAmmoByProcessor
        -   RemoveFlagHasArmedAmmoProcessor

    What if this processor is disabled?
        -   ammos are not being armed

    Where the processor should be planned?
        -   after GenerateArmAmmoProcessor
        -   before RemoveFlagIsAboutToArmAmmoProcessor
        -   before RemoveFlagWasArmedAsAmmoByProcessor
        -   before RemoveFlagHasArmedAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_ammo_system.generate_arm_ammo_processor:GenerateArmAmmoProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        '''  Detects fighters that are about to arm the ammo and performs
        the actual arming, if the fighter is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have HasWeapon and RemoveFlagIsAboutToArmWeaponProcessor - those are candidates for successful arming
        for ent_fighter, (has_weapon, has_inventory, flag_is_about_to_arm_ammo, weapon_in_use) in self.world.get_components_opt(HasWeapon, HasInventory, FlagIsAboutToArmAmmo, optional=WeaponInUse):

            # First disarm currently used ammo
            ammo_in_use_entity_id = has_weapon.weapons[weapon_in_use.type]["generator"] if weapon_in_use is not None else None

            logger.debug(f'({self.cycle}) - Currently used ammo before arming a new one {ammo_in_use_entity_id=}.')

            
            if ammo_in_use_entity_id is not None:
                    self.world.add_component(ent_fighter, FlagIsAboutToDisarmAmmo(ammo=ammo_in_use_entity_id, type=weapon_in_use.type))
                    logger.debug(f'({self.cycle}) - component FlagIsAboutToDisarmAmmo created with params {ammo_in_use_entity_id=}, {weapon_in_use.type=}.')

            # Always arm the ammo
            try:
                has_weapon.weapons[flag_is_about_to_arm_ammo.weapon]["generator"] = flag_is_about_to_arm_ammo.ammo
            except KeyError:
                logger.error(f'({self.cycle}) - Ammo for {flag_is_about_to_arm_ammo.weapon} is of incorrect type "{flag_is_about_to_arm_ammo.weapon}".')
                raise ValueError

            # Report that arming a weapon occured - generate event
            arm_ammo_event = Event('AMMO_PACK_ARMED', flag_is_about_to_arm_ammo.ammo, ent_fighter, params={'ammo': flag_is_about_to_arm_ammo.ammo, 'fighter': ent_fighter})
            self.add_event_fnc(arm_ammo_event)

            # Assign FlagWasArmedAsAmmoBy component to the ammo entity
            self.world.add_component(flag_is_about_to_arm_ammo.ammo, FlagWasArmedAsAmmoBy(fighter=ent_fighter))
            logger.debug(f'({self.cycle}) - Ammo {flag_is_about_to_arm_ammo.ammo} ({flag_is_about_to_arm_ammo.weapon}, {flag_is_about_to_arm_ammo.type}) was armed by entity {ent_fighter}.')

            # Assign FlagHasArmedAmmo component to the fighter entity
            self.world.add_component(ent_fighter, FlagHasArmedAmmo(ammo=flag_is_about_to_arm_ammo.ammo))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} has armed ammo {flag_is_about_to_arm_ammo.ammo} of type "{flag_is_about_to_arm_ammo.weapon} - {flag_is_about_to_arm_ammo.type}".')

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

