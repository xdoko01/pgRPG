__all__ = ['NewRemoveFlagIsAboutToArmAmmoProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagIsAboutToArmAmmoProcessor(esper.Processor):
    ''' Removes the flag that the entity has been considered for picking
    up of an ammo at the end of the cycle.

    Involved components:
        -   NewFlagIsAboutToArmAmmo

    Related processors:
        -   NewGenerateArmAmmoProcessor
        -   NewPerformArmAmmoProcessor
        -   NewRemoveFlagWasArmedAsAmmoByProcessor
        -   NewRemoveFlagHasArmedAmmoProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of an ammo

    Where the processor should be planned?
        -   after NewPerformArmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.arm_ammo_system.new_perform_arm_ammo_processor', 'NewPerformArmAmmoProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for arming
        an ammo at the end of the cycle.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagIsAboutToArmAmmo):

            self.world.remove_component(ent, components.NewFlagIsAboutToArmAmmo)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagIsAboutToArmAmmo" was removed.')


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

