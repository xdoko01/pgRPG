__all__ = ['GenerateTeleportationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.teleport import Teleport
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided
from pyrpg.core.ecs.components.new.flag_is_about_to_be_teleported_by import FlagIsAboutToBeTeleportedBy

# Logger init
logger = logging.getLogger(__name__)

class GenerateTeleportationProcessor(Processor):
    ''' Detects entities that act as teleport + have collided and assignes
    the FlagIsAboutToBeTeleportedBy to all their colliders.

    Involved components:
        -   Teleport
        -   FlagHasCollided
        -   FlagIsAboutToBeTeleportedBy

    Related processors:
        -   PerformTeleportationProcessor
        -   RemoveFlagIsAboutToBeTeleportedByProcessor

    What if this processor is disabled?
        -   entities are not being teleported

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
        -   before PerformTeleportationProcessor
        -   before RemoveFlagIsAboutToBeTeleportedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.collision_system.generate_collisions_processor:GenerateCollisionsProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assignes
        the FlagIsAboutToPickEntity to their pickers
        '''
        self.cycle += 1

        # Get all entities that have Pickable and FlagHasCollided - those are candidates for pickup
        for ent_teleport, (teleport, flag_has_collided) in self.world.get_components(Teleport, FlagHasCollided):

            # Assign the FlagIsAboutToBeTeleportedBy to ALL entities that collided with teleport entity ent_teleport
            #for ent_teleportee, _, _, _ in flag_has_collided.collisions:
             for collision in flag_has_collided.collisions:
                self.world.add_component(collision.entity, FlagIsAboutToBeTeleportedBy(teleport=ent_teleport, dest_x=teleport.dest_x, dest_y=teleport.dest_y, dest_map=teleport.dest_map, key=teleport.key))
                logger.debug(f'({self.cycle}) - Entity {ent_teleport} is trying to teleport entity {collision.entity}.')

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

