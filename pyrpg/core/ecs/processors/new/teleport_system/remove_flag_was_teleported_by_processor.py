__all__ = ['RemoveFlagWasTeleportedByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_was_teleported_by import FlagWasTeleportedBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasTeleportedByProcessor(Processor):
    ''' Removes the flag that the entity was teleported.

    Involved components:
        -   FlagWasTeleportedBy

    Related processors:
        -   GenerateTeleportationProcessor
        -   PerformTeleportationProcessor
        -   RemoveFlagIsAboutToBeTeleportedByProcessor
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
        ''' Removes the flag that the entity was teleported.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(FlagWasTeleportedBy):
            self.world.remove_component(ent, FlagWasTeleportedBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasTeleportedBy" was removed.')

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

