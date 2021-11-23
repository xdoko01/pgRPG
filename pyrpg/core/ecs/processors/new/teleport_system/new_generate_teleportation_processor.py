__all__ = ['NewGenerateTeleportationProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewGenerateTeleportationProcessor(esper.Processor):
    ''' Detects entities that act as teleport + have collided and assignes
    the NewFlagIsAboutToBeTeleportedBy to all their colliders.

    Involved components:
        -   Teleport
        -   NewFlagHasCollided
        -   NewFlagIsAboutToBeTeleportedBy

    Related processors:
        -   NewPerformTeleportationProcessor
        -   NewRemoveFlagIsAboutToBeTeleportedByProcessor

    What if this processor is disabled?
        -   entities are not being teleported

    Where the processor should be planned?
        -   after NewGenerateEntityCollisionsProcessor
        -   before NewPerformTeleportationProcessor
        -   before NewRemoveFlagIsAboutToBeTeleportedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.collision_system.new_generate_entity_collisions_processor', 'NewGenerateEntityCollisionsProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()


    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assignes
        the NewFlagIsAboutToPickEntity to their pickers
        '''
        self.cycle += 1


        # Get all entities that have Pickable and NewFlagHasCollided - those are candidates for pickup
        for ent_teleport, (teleport, flag_has_collided) in self.world.get_components(components.Teleport, components.NewFlagHasCollided):

            # Assign the NewFlagIsAboutToBeTeleportedBy to ALL entities that collided with teleport entity ent_teleport
            for ent_teleportee, _, _, _ in flag_has_collided.collisions:

                self.world.add_component(ent_teleportee, components.NewFlagIsAboutToBeTeleportedBy(teleport=ent_teleport, dest_x=teleport.dest_x, dest_y=teleport.dest_y, dest_map=teleport.dest_map, key=teleport.key))
                logger.debug(f'({self.cycle}) - Entity {ent_teleport} is trying to teleport entity {ent_teleportee}.')


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

