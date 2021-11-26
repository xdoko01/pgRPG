__all__ = ['NewPerformTeleportationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.new_teleportable import NewTeleportable
from pyrpg.core.ecs.components.new.new_flag_was_teleported_by import NewFlagWasTeleportedBy
from pyrpg.core.ecs.components.new.new_flag_has_teleported import NewFlagHasTeleported
from pyrpg.core.ecs.components.new.new_flag_is_about_to_be_teleported_by import NewFlagIsAboutToBeTeleportedBy

# For creation of events
from pyrpg.core.events.event import Event 

# Logger init
logger = logging.getLogger(__name__)

class NewPerformTeleportationProcessor(Processor):
    ''' Detects entities that are about to be teleported and performs
    the actual teleportation if the teleportee is capable.

    Involved components:
        -   Position
        -   NewTepeportable
        -   NewFlagWasTeleportedBy
        -   NewFlagHasTeleported
        -   NewFlagIsAboutToBeTeleportedBy

    Related processors:
        -   NewGenerateTeleportationProcessor
        -   NewRemoveFlagIsAboutToBeTeleportedByProcessor
        -   NewRemoveFlagWasTeleportedByProcessor
        -   NewRemoveFlagHasTeleportedProcessor

    What if this processor is disabled?
        -   entities are not being teleported up

    Where the processor should be planned?
        -   after NewGenerateTeleportationProcessor
        -   before NewRemoveFlagWasTeleportedByProcessor
        -   before NewRemoveFlagIsAboutToBeTeleportedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.teleport_system.new_generate_teleportation_processor:NewGenerateTeleportationProcessor'
    ]

    def __init__(self, add_event_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be teleported and performs
        the actual teleportation, if the picker is capable.
        '''
        self.cycle += 1

        # Get all entities that have Teleportable and NewFlagIsAboutToBeTeleportedBy - those are candidates for successful teleportation
        for ent_teleportee, (position, teleportable, flag_is_about_to_be_teleported_by) in self.world.get_components(Position, NewTeleportable, NewFlagIsAboutToBeTeleportedBy):

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

            # Assign NewFlagWasTeleportedBy component to the teleportee
            self.world.add_component(ent_teleportee, NewFlagWasTeleportedBy(teleport=flag_is_about_to_be_teleported_by.teleport))
            logger.debug(f'({self.cycle}) - Entity {ent_teleportee} was teleported by entity {flag_is_about_to_be_teleported_by.teleport}.')

            # Assign NewFlagHasTeleported component to the teleport entity
            self.world.add_component(flag_is_about_to_be_teleported_by.teleport, NewFlagHasTeleported(teleportee=ent_teleportee))
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

