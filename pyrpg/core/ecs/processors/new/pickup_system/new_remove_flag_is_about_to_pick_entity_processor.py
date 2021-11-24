__all__ = ['NewRemoveFlagIsAboutToPickEntityProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagIsAboutToPickEntityProcessor(esper.Processor):
    ''' Removes the flag that the item has been considered for picking
    at the end of the cycle.

    Involved components:
        -   NewFlagIsAboutToPickEntity

    Related processors:
        -   NewGeneratePickupProcessor
        -   NewPerformPickupProcessor
        -   NewRemoveFlagWasPickedByProcessor
        -   NewRemoveFlagHasPickedProcessor

    What if this processor is disabled?
        -   unexpected behavior during picking of the item

    Where the processor should be planned?
        -   after NewPerformPickupProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.pickup_system.new_perform_pickup_processor', 'NewPerformPickupProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for picking
        at the end of the cycle.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagIsAboutToPickEntity):

            self.world.remove_component(ent, components.NewFlagIsAboutToPickEntity)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagIsAboutToPickEntity" was removed.')


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

