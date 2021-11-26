__all__ = ['NewRemoveFlagIsAboutToBeTeleportedByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.new_flag_is_about_to_be_teleported_by import NewFlagIsAboutToBeTeleportedBy

# Logger init
logger = logging.getLogger(__name__)

class NewRemoveFlagIsAboutToBeTeleportedByProcessor(Processor):
    ''' Removes the flag that the item has been considered for teleportation
    at the end of the cycle.

    Involved components:
        -   NewFlagIsAboutToBeTeleportedBy

    Related processors:
        -   NewGenerateTeleportationProcessor
        -   NewPerformTeleportationProcessor
        -   NewRemoveFlagWasTeleportedByProcessor
        -   NewRemoveFlagHasTeleportedProcessor

    What if this processor is disabled?
        -   unexpected behavior during teleportation of the item

    Where the processor should be planned?
        -   after NewPerformTeleportationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.teleport_system.new_perform_teleportation_processor:NewPerformTeleportationProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for teleportation
        at the end of the cycle.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(NewFlagIsAboutToBeTeleportedBy):

            self.world.remove_component(ent, NewFlagIsAboutToBeTeleportedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagIsAboutToBeTeleportedBy" was removed.')

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

