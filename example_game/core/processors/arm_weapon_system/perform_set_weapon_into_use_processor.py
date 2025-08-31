__all__ = ['PerformSetWeaponIntoUseProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.weapon_in_use import WeaponInUse
from core.components.has_weapon import HasWeapon
from core.components.render_data_from_parent import RenderDataFromParent
from core.components.flag_set_weapon_into_use import FlagSetWeaponIntoUse
from core.components.flag_has_disarmed_weapon import FlagHasDisarmedWeapon
from core.components.flag_has_disarmed_ammo import FlagHasDisarmedAmmo

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformSetWeaponIntoUseProcessor(Processor):
    ''' Detects weapons that have been armed and set them in use.

    Involved components:
        -   WeaponInUse
        -   Weapon
        -   FlagWasArmedAsWeaponBy

    Related processors:
        -   PerformArmWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being armed for usage

    Where the processor should be planned?
        -   after PerformArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'allOf', 
            'arm_weapon_system.perform_arm_weapon_processor:PerformArmWeaponProcessor'
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

        '''
            # Put the weapon out of usage
            self.world.add_component(ent_fighter, FlagSetWeaponOutOfUse(type=flag_is_about_to_arm_weapon.type, prev_ent_ids=prev_armed_entity_ids))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} has set weapon {flag_is_about_to_arm_weapon.weapon} of type {flag_is_about_to_arm_weapon.type} in use.')
        ''' 

        # Disarmed ammo should not have RenderDataFromParent component
        for ent_fighter, (has_weapon, flag_has_disarmed_ammo) in self.world.get_components(HasWeapon, FlagHasDisarmedAmmo):

            # Remove RenderDataFromParent
            try:
                self.world.remove_component(flag_has_disarmed_ammo.ammo, RenderDataFromParent)
                logger.debug(f'({self.cycle}) - Entity {flag_has_disarmed_ammo.ammo=} - RenderDataFromParent component was removed (ammo).')
            except KeyError:
                logger.debug(f'({self.cycle}) - Entity {flag_has_disarmed_ammo.ammo=} - has no RenderDataFromParent component to remove (ammo).')

        # Check if there is any weapon in the slot, if not, remove the weapon in use
        for ent_fighter, (has_weapon, weapon_in_use, flag_has_disarmed_weapon) in self.world.get_components(HasWeapon, WeaponInUse, FlagHasDisarmedWeapon):

            # Remove the WeaponInUse component, if it is pointing do disarmed weapon
            if has_weapon.weapons[weapon_in_use.type]["weapon"] is None: # and weapon_in_use.type == flag_is_about_to_disarm_weapon.type and 
                
                # Remove RenderDataFromParent from ammo
                try:
                    self.world.remove_component(has_weapon.weapons[weapon_in_use.type]["generator"], RenderDataFromParent)
                    logger.debug(f'({self.cycle}) - Entity {has_weapon.weapons[weapon_in_use.type]["generator"]=} - RenderDataFromParent component was removed (ammo).')
                except KeyError:
                    logger.debug(f'({self.cycle}) - Entity {has_weapon.weapons[weapon_in_use.type]["generator"]=} - has no RenderDataFromParent component to remove (ammo).')

                self.world.remove_component(ent_fighter, WeaponInUse)
                logger.debug(f'({self.cycle}) - Entity {ent_fighter} - WeaponInUse component was removed.')
            
            # Remove RenderDataFromParent from weapon
            try:
                self.world.remove_component(flag_has_disarmed_weapon.weapon, RenderDataFromParent)
                logger.debug(f'({self.cycle}) - Entity {flag_has_disarmed_weapon.weapon=} - RenderDataFromParent component was removed (weapon).')
            except KeyError:
                logger.debug(f'({self.cycle}) - Entity {flag_has_disarmed_weapon.weapon=} - has no RenderDataFromParent component to remove (weapon).')


        for ent_fighter, (_, flag_set_weapon_into_use) in self.world.get_components(HasWeapon, FlagSetWeaponIntoUse):

            '''
            # Get the currently used weapon and ammo
            curr_weapon_in_use_entity_id = has_weapon.weapons[weapon_in_use.type]['weapon'] if weapon_in_use is not None else None
            curr_ammo_in_use_entity_id = has_weapon.weapons[weapon_in_use.type]['generator'] if weapon_in_use is not None else None
            '''
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} - entities for removal of RenderDataFromParent are {flag_set_weapon_into_use.prev_ent_ids}.')

            for ent_for_removal in flag_set_weapon_into_use.prev_ent_ids:
                # Remove the RenderDataFromParent form the weapon and ammo that is currently in use to prevent some texture problems
                try:
                    self.world.remove_component(ent_for_removal, RenderDataFromParent)
                    logger.debug(f'({self.cycle}) - Entity {ent_for_removal} - RenderDataFromParent component was removed (weapon).')
                except KeyError:
                    logger.debug(f'({self.cycle}) - Entity {ent_for_removal=} - has no RenderDataFromParent component to remove.')


            '''
            if curr_weapon_in_use_entity_id is not None: 
                self.world.remove_component(curr_weapon_in_use_entity_id, RenderDataFromParent)
                logger.debug(f'({self.cycle}) - Entity {curr_weapon_in_use_entity_id} - RenderDataFromParent  component was removed.')

            if curr_ammo_in_use_entity_id is not None: 
                self.world.remove_component(curr_ammo_in_use_entity_id, RenderDataFromParent)
                logger.debug(f'({self.cycle}) - Entity {curr_ammo_in_use_entity_id} - RenderDataFromParent  component was removed.')
            '''

            # Assign WeaponInUse component to the fighter entity ['type', 'action', 'idle_action']
            self.world.add_component(ent_fighter, WeaponInUse(type=flag_set_weapon_into_use.type))
            logger.debug(f'({self.cycle}) - Entity {ent_fighter} is now using weapon type {flag_set_weapon_into_use.type}. WeaponInUse assigned')

            # Report that arming a weapon occured - generate event
            use_weapon_event = Event('WEAPON_SET_INTO_USE', None, ent_fighter, params={'type': flag_set_weapon_into_use.type, 'fighter': ent_fighter})
            self.add_event_fnc(use_weapon_event)
            logger.debug(f'({self.cycle}) - Event {use_weapon_event} created with parameters {use_weapon_event.params}')

            # Remove FlagSetWeaponIntoUse component from the fighter entity
            self.world.remove_component(ent_fighter, FlagSetWeaponIntoUse)


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

