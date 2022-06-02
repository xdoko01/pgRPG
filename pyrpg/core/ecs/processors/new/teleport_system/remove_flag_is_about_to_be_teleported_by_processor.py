__all__ = ['RemoveFlagIsAboutToBeTeleportedByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_is_about_to_be_teleported_by import FlagIsAboutToBeTeleportedBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToBeTeleportedByProcessor(Processor):
    ''' Removes the flag that the item has been considered for teleportation
    at the end of the cycle.

    Involved components:
        -   FlagIsAboutToBeTeleportedBy

    Related processors:
        -   GenerateTeleportationProcessor
        -   PerformTeleportationProcessor
        -   RemoveFlagWasTeleportedByProcessor
        -   RemoveFlagHasTeleportedProcessor

    What if this processor is disabled?
        -   unexpected behavior during teleportation of the item

    Where the processor should be planned?
        -   after PerformTeleportationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.teleport_system.perform_teleportation_processor:PerformTeleportationProcessor'
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

        for ent, (_) in self.world.get_components(FlagIsAboutToBeTeleportedBy):

            self.world.remove_component(ent, FlagIsAboutToBeTeleportedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToBeTeleportedBy" was removed.')

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

