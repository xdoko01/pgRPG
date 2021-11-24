__all__ = ['NewPerformArmAmmoProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events

# Logger init
logger = logging.getLogger(__name__)


class NewPerformArmAmmoProcessor(esper.Processor):
    ''' Detects entities that are about to arm ammo and performs
    the actual arming, if the fighter is capable.

    Involved components:
        -   HasWeapon
        -   NewFlagIsAboutToArmAmmo
        -   NewFlagHasArmedAmmo
        -   NewFlagWasArmedAsAmmoBy

    Related processors:
        -   NewGenerateArmAmmoProcessor
        -   NewRemoveFlagIsAboutToArmAmmoProcessor
        -   NewRemoveFlagWasArmedAsAmmoByProcessor
        -   NewRemoveFlagHasArmedAmmoProcessor

    What if this processor is disabled?
        -   ammos are not being armed

    Where the processor should be planned?
        -   after NewGenerateArmAmmoProcessor
        -   before NewRemoveFlagIsAboutToArmAmmoProcessor
        -   before NewRemoveFlagWasArmedAsAmmoByProcessor
        -   before NewRemoveFlagHasArmedAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.arm_ammo_system.new_generate_arm_ammo_processor', 'NewGenerateArmAmmoProcessor')
        ]


    def __init__(self, add_event_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects fighters that are about to arm the ammo and performs
        the actual arming, if the fighter is capable.
        '''
        self.cycle += 1

        # Get all entities that have HasWeapon and NewRemoveFlagIsAboutToArmWeaponProcessor - those are candidates for successful arming
        for ent_fighter, (has_weapon, has_inventory, flag_is_about_to_arm_ammo) in self.world.get_components(components.HasWeapon, components.NewHasInventory, components.NewFlagIsAboutToArmAmmo):

            try:
                # Always arm the ammo
                has_weapon.weapons[flag_is_about_to_arm_ammo.weapon]["generator"] = flag_is_about_to_arm_ammo.ammo
            except KeyError:
                logger.error(f'({self.cycle}) - Ammo for {flag_is_about_to_arm_ammo.weapon} is of incorrect type "{flag_is_about_to_arm_ammo.weapon}".')
                raise ValueError

            # Report that arming a weapon occured - generate event
            arm_ammo_event = event.Event('AMMO_PACK_ARMED', flag_is_about_to_arm_ammo.ammo, ent_fighter, params={'ammo_pack' : flag_is_about_to_arm_ammo.ammo, 'picker' : ent_fighter})
            self.add_event_fnc(arm_ammo_event)

            # Assign NewFlagWasArmedAsAmmoBy component to the ammo entity
            self.world.add_component(flag_is_about_to_arm_ammo.ammo, components.NewFlagWasArmedAsAmmoBy(fighter=ent_fighter))
            logger.debug(f'({self.cycle}) - Ammo {flag_is_about_to_arm_ammo.ammo} ({flag_is_about_to_arm_ammo.weapon}, {flag_is_about_to_arm_ammo.type}) was armed by entity {ent_fighter}.')

            # Assign NewFlagHasArmedAmmo component to the fighter entity
            self.world.add_component(ent_fighter, components.NewFlagHasArmedAmmo(ammo=flag_is_about_to_arm_ammo.ammo))
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

