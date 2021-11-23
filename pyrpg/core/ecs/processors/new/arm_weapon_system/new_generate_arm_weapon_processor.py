__all__ = ['NewGenerateArmWeaponProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewGenerateArmWeaponProcessor(esper.Processor):
    ''' Detects entities that act as weapon + have been picked and assigns
    the NewFlagIsAboutToArmWeapon to all their colliders (potentional fighters).

    Involved components:
        -   Weapon
        -   NewFlagWasPickedBy
        -   NewFlagIsAboutToArmWeapon

    Related processors:
        -   NewPerformArmWeaponProcessor
        -   NewRemoveFlagIsAboutToArmWeaponProcessor

    What if this processor is disabled?
        -   weapons are not being armed

    Where the processor should be planned?
        -   after NewPerformPickupProcessor
        -   before NewPerformArmWeaponProcessor
        -   before NewRemoveFlagIsAboutToArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.pickup_system.new_perform_pickup_processor', 'NewPerformPickupProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()


    def process(self, *args, **kwargs):
        '''  Detects entities that are weapons + have been picked  and assigns
        the NewFlagIsAboutToArmWeapon to their pickers
        '''
        self.cycle += 1

        # Get all entities that have Weapon and NewFlagWasPickedBy - those are candidates for arming
        for ent_weapon, (weapon, flag_was_picked_by) in self.world.get_components(components.Weapon, components.NewFlagWasPickedBy):

            self.world.add_component(flag_was_picked_by.picker, components.NewFlagIsAboutToArmWeapon(weapon=ent_weapon, type=weapon.type))
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

