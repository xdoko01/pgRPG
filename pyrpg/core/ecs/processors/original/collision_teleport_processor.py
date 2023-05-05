__all__ = ['CollisionTeleportProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.teleport import Teleport
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.teleportable import Teleportable
from pyrpg.core.ecs.components.original.has_inventory import HasInventory

# For creation of events
from pyrpg.core.events.event import Event

class CollisionTeleportProcessor(Processor):
    def __init__(self, teleport_event_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.teleport_event_queue = teleport_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (teleport, collision) in self.world.get_components(Teleport, Collidable):

            # Process everything that collided with teleport
            for col_event_entity in collision.collision_events.copy():
                    
                    # If entity is Teleportable and has position
                    if self.world.has_components(col_event_entity, Teleportable, Position, Collidable):
                        
                        # Get the Position, Collidable and HasInventory component of the teleportee entity
                        col_event_entity_pos = self.world.component_for_entity(col_event_entity, Position) 
                        col_event_entity_coll = self.world.component_for_entity(col_event_entity, Collidable)
                        try:
                            col_event_entity_inventory = self.world.component_for_entity(col_event_entity, HasInventory)
                            
                            # Does the teleportee have the key in the inventory?
                            # Either no key is required by the teleport or key is in teleportees inventory
                            teleportee_has_key = teleport.key is None or teleport.key in col_event_entity_inventory.inventory

                        except KeyError:
                            teleportee_has_key = teleport.key is None

                        # Do the teleportation of the teleportee - only if it has the key (by default no key necessary)
                        if teleportee_has_key:
                            col_event_entity_pos.x = teleport.dest_x
                            col_event_entity_pos.y = teleport.dest_y
                            col_event_entity_pos.map = teleport.dest_map 

                            # Report that teleportation occured - generate event
                            teleport_event = Event('TELEPORTATION', ent, col_event_entity, params={'teleport' : ent, 'teleportee' : col_event_entity})
                            self.teleport_event_queue.append(teleport_event)

                        # Remove the col_event_entity from Teleport
                        collision.collision_events.remove(col_event_entity)

                        # Remove the col event related to teleport from the Entity
                        col_event_entity_coll.collision_events.remove(ent)
