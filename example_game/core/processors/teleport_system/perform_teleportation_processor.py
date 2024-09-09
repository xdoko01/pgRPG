__all__ = ['PerformTeleportationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.teleportable import Teleportable
from pyrpg.core.ecs.components.new.flag_was_teleported_by import FlagWasTeleportedBy
from pyrpg.core.ecs.components.new.flag_has_teleported import FlagHasTeleported
from pyrpg.core.ecs.components.new.flag_is_about_to_be_teleported_by import FlagIsAboutToBeTeleportedBy

# For creation of events
from pyrpg.core.events.event import Event 

# Logger init
logger = logging.getLogger(__name__)

class PerformTeleportationProcessor(Processor):
    ''' Detects entities that are about to be teleported and performs
    the actual teleportation if the teleportee is capable.

    Involved components:
        -   Position
        -   NewTepeportable
        -   FlagWasTeleportedBy
        -   FlagHasTeleported
        -   FlagIsAboutToBeTeleportedBy

    Related processors:
        -   GenerateTeleportationProcessor
        -   RemoveFlagIsAboutToBeTeleportedByProcessor
        -   RemoveFlagWasTeleportedByProcessor
        -   RemoveFlagHasTeleportedProcessor

    What if this processor is disabled?
        -   entities are not being teleported up

    Where the processor should be planned?
        -   after GenerateTeleportationProcessor
        -   before RemoveFlagWasTeleportedByProcessor
        -   before RemoveFlagIsAboutToBeTeleportedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.teleport_system.generate_teleportation_processor:GenerateTeleportationProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be teleported and performs
        the actual teleportation, if the picker is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Teleportable and FlagIsAboutToBeTeleportedBy - those are candidates for successful teleportation
        for ent_teleportee, (position, teleportable, flag_is_about_to_be_teleported_by) in self.world.get_components(Position, Teleportable, FlagIsAboutToBeTeleportedBy):

            # Check that key required for the teleport matches the key in Teleportable component
            # If the key required by the teleport is not found then do not proceed with teleportation
            if flag_is_about_to_be_teleported_by.key not in teleportable.keys: continue

            # Change position of ent_teleportee
            position.x = flag_is_about_to_be_teleported_by.dest_x
            position.y = flag_is_about_to_be_teleported_by.dest_y
            position.map = flag_is_about_to_be_teleported_by.dest_map

            # Report that teleportation occured - generate event
            teleport_event = Event('TELEPORTATION', flag_is_about_to_be_teleported_by.teleport, ent_teleportee, params={'teleport' : flag_is_about_to_be_teleported_by.teleport, 'teleportee' : ent_teleportee})
            self.add_event_fnc(teleport_event)

            # Assign FlagWasTeleportedBy component to the teleportee
            self.world.add_component(ent_teleportee, FlagWasTeleportedBy(teleport=flag_is_about_to_be_teleported_by.teleport))
            logger.debug(f'({self.cycle}) - Entity {ent_teleportee} was teleported by entity {flag_is_about_to_be_teleported_by.teleport}.')

            # Assign FlagHasTeleported component to the teleport entity
            self.world.add_component(flag_is_about_to_be_teleported_by.teleport, FlagHasTeleported(teleportee=ent_teleportee))
            logger.debug(f'({self.cycle}) - Entity {flag_is_about_to_be_teleported_by.teleport} has teleported entity {ent_teleportee}.')

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

