__all__ = ['NewRemoveFlagIsAboutToArmWeaponProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagIsAboutToArmWeaponProcessor(esper.Processor):
    ''' Removes the flag that the entity has been considered for picking
    up of a weapon the end of the cycle.

    Involved components:
        -   NewFlagIsAboutToArmWeapon

    Related processors:
        -   NewGenerateArmWeaponProcessor
        -   NewPerformArmWeaponProcessor
        -   NewRemoveFlagWasArmedAsWeaponByProcessor
        -   NewRemoveFlagHasArmedWeaponProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of a weapon

    Where the processor should be planned?
        -   after NewPerformArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.arm_weapon_system.new_perform_arm_weapon_system', 'NewPerformArmWeaponProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for arming
        a weapon at the end of the cycle.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagIsAboutToArmWeapon):

            self.world.remove_component(ent, components.NewFlagIsAboutToArmWeapon)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagIsAboutToArmWeapon" was removed.')


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

