__all__ = ['NewPerformTeleportationProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events

# Logger init
logger = logging.getLogger(__name__)


class NewPerformTeleportationProcessor(esper.Processor):
    ''' Detects entities that are about to be teleported and performs
    the actual teleportation if the teleportee is capable.

    Involved components:
        -   Teleportee
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
    PREREQ = ['NewGenerateTeleportationProcessor']


    def __init__(self, add_event_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc

    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be teleported and performs
        the actual teleportation, if the picker is capable.
        '''
        self.cycle += 1

        # Get all entities that have Teleportable and NewFlagIsAboutToBeTeleportedBy - those are candidates for successful teleportation
        for ent_teleportee, (position, teleportable, flag_is_about_to_be_teleported_by) in self.world.get_components(components.Position, components.NewTeleportable, components.NewFlagIsAboutToBeTeleportedBy):

            # Check that key required for the teleport matches the key in Teleportable component
            # If the key required by the teleport is not found then do not proceed with teleportation
            if flag_is_about_to_be_teleported_by.key not in teleportable.keys: continue

            # Change position of ent_teleportee
            position.x = flag_is_about_to_be_teleported_by.dest_x
            position.y = flag_is_about_to_be_teleported_by.dest_y
            position.map = flag_is_about_to_be_teleported_by.dest_map

            # Report that teleportation occured - generate event
            teleport_event = event.Event('TELEPORTATION', flag_is_about_to_be_teleported_by.teleport, ent_teleportee, params={'teleport' : flag_is_about_to_be_teleported_by.teleport, 'teleportee' : ent_teleportee})
            self.add_event_fnc(teleport_event)

            # Assign NewFlagWasTeleportedBy component to the teleportee
            self.world.add_component(ent_teleportee, components.NewFlagWasTeleportedBy(teleport=flag_is_about_to_be_teleported_by.teleport))
            logger.debug(f'({self.cycle}) - Entity {ent_teleportee} was teleported by entity {flag_is_about_to_be_teleported_by.teleport}.')

            # Assign NewFlagHasTeleported component to the teleport entity
            self.world.add_component(flag_is_about_to_be_teleported_by.teleport, components.NewFlagHasTeleported(teleportee=ent_teleportee))
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

