__all__ = ['RemoveFlagHasTeleportedProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_has_teleported import FlagHasTeleported

# Logger init
logger = logging.getLogger(__name__)


class RemoveFlagHasTeleportedProcessor(Processor):
    ''' Removes the flag that teleport has teleported an entity.

    Involved components:
        -   FlagHasTeleported

    Related processors:
        -   GenerateTeleportationProcessor
        -   PerformTeleportationProcessor
        -   RemoveFlagIsAboutToBeTeleportedByProcessor
        -   RemoveFlagWasTeleportedByProcessor

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
        ''' Removes the flag that the item was picked.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(FlagHasTeleported):

            self.world.remove_component(ent, FlagHasTeleported)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagHasTeleported" was removed.')

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

