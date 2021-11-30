__all__ = ['GenerateArmWeaponProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.weapon import Weapon
from pyrpg.core.ecs.components.new.flag_was_picked_by import FlagWasPickedBy
from pyrpg.core.ecs.components.new.flag_is_about_to_arm_weapon import FlagIsAboutToArmWeapon

# Logger init
logger = logging.getLogger(__name__)

class GenerateArmWeaponProcessor(Processor):
    ''' Detects entities that act as weapon + have been picked and assigns
    the FlagIsAboutToArmWeapon to all their colliders (potentional fighters).

    Involved components:
        -   Weapon
        -   FlagWasPickedBy
        -   FlagIsAboutToArmWeapon

    Related processors:
        -   PerformArmWeaponProcessor
        -   RemoveFlagIsAboutToArmWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being armed

    Where the processor should be planned?
        -   after PerformPickupProcessor
        -   before PerformArmWeaponProcessor
        -   before RemoveFlagIsAboutToArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.pickup_system.perform_pickup_processor', 'PerformPickupProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are weapons + have been picked  and assigns
        the FlagIsAboutToArmWeapon to their pickers
        '''
        self.cycle += 1

        # Get all entities that have Weapon and FlagWasPickedBy - those are candidates for arming
        for ent_weapon, (weapon, flag_was_picked_by) in self.world.get_components(Weapon, FlagWasPickedBy):

            self.world.add_component(flag_was_picked_by.picker, FlagIsAboutToArmWeapon(weapon=ent_weapon, type=weapon.type))
            logger.debug(f'({self.cycle}) - Entity {flag_was_picked_by.picker} is trying to arm as weapon entity {ent_weapon}.')

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

