__all__ = ['NewRemoveFlagWasPickedByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.new_flag_was_picked_by import NewFlagWasPickedBy

# Logger init
logger = logging.getLogger(__name__)

class NewRemoveFlagWasPickedByProcessor(Processor):
    ''' Removes the flag that the item was picked.

    Involved components:
        -   NewFlagWasPickedBy

    Related processors:
        -   NewGeneratePickupProcessor
        -   NewPerformPickupProcessor
        -   NewRemoveFlagIsAboutToPickEntityProcessor
        -   NewRemoveFlagHasPickedProcessor

    What if this processor is disabled?
        -   unexpected behavior during picking of the item

    Where the processor should be planned?
        -   after NewPerformPickupProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.pickup_system.new_perform_pickup_processor:NewPerformPickupProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item was picked.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(NewFlagWasPickedBy):

            self.world.remove_component(ent, NewFlagWasPickedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagWasPickedBy" was removed.')

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

