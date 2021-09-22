__all__ = ['NewRemoveFlagHasArmedAmmoProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagHasArmedAmmoProcessor(esper.Processor):
    ''' Removes the flag that fighter has armed an entity.

    Involved components:
        -   NewFlagHasArmedAmmo

    Related processors:
        -   NewGenerateArmAmmoProcessor
        -   NewPerformArmAmmoProcessor
        -   NewRemoveFlagIsAboutToArmAmmoProcessor
        -   NewRemoveFlagWasArmedAsAmmoByProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of an ammo of the item

    Where the processor should be planned?
        -   after NewPerformArmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['NewPerformArmAmmoProcessor']


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item was picked.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagHasArmedAmmo):

            self.world.remove_component(ent, components.NewFlagHasArmedAmmo)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagHasArmedAmmo" was removed.')


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

