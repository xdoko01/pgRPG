__all__ = ['PerformArmAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.has_weapon import HasWeapon
from pyrpg.core.ecs.components.new.has_inventory import HasInventory
from pyrpg.core.ecs.components.new.flag_was_armed_as_ammo_by import FlagWasArmedAsAmmoBy
from pyrpg.core.ecs.components.new.flag_is_about_to_arm_ammo import FlagIsAboutToArmAmmo
from pyrpg.core.ecs.components.new.flag_has_armed_ammo import FlagHasArmedAmmo

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
        'new.arm_ammo_system.generate_arm_ammo_processor:GenerateArmAmmoProcessor'
    ]

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
        '''  Detects fighters that are about to arm the ammo and performs
        the actual arming, if the fighter is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have HasWeapon and RemoveFlagIsAboutToArmWeaponProcessor - those are candidates for successful arming
        for ent_fighter, (has_weapon, has_inventory, flag_is_about_to_arm_ammo) in self.world.get_components(HasWeapon, HasInventory, FlagIsAboutToArmAmmo):

            try:
                # Always arm the ammo
                has_weapon.weapons[flag_is_about_to_arm_ammo.weapon]["generator"] = flag_is_about_to_arm_ammo.ammo
            except KeyError:
                logger.error(f'({self.cycle}) - Ammo for {flag_is_about_to_arm_ammo.weapon} is of incorrect type "{flag_is_about_to_arm_ammo.weapon}".')
                raise ValueError

            # Report that arming a weapon occured - generate event
            arm_ammo_event = Event('AMMO_PACK_ARMED', flag_is_about_to_arm_ammo.ammo, ent_fighter, params={'ammo_pack' : flag_is_about_to_arm_ammo.ammo, 'picker' : ent_fighter})
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

