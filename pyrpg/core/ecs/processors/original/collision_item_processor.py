__all__ = ['CollisionItemProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.camera import Camera
from pyrpg.core.ecs.components.original.pickable import Pickable
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.has_inventory import HasInventory

# For creation of events
from pyrpg.core.events.event import Event

class CollisionItemProcessor(Processor):
    def __init__(self, item_pickup_event_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_pickup_event_queue = item_pickup_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (item, collision) in self.world.get_components(Pickable, Collidable):

            # Process everything that collided with item
            for col_event_entity in collision.collision_events.copy():
                    
                    # If entity can collect items (has inventory)
                    if self.world.has_component(col_event_entity, HasInventory):
                        
                        # Get the HasItem component of the entity
                        col_event_entity_inventory = self.world.component_for_entity(col_event_entity, HasInventory) 
                        
                        # Get the Collidable component of the entity - in order to remove the collision
                        col_event_entity_coll = self.world.component_for_entity(col_event_entity, Collidable)

                        # Add the Item entity into the HasInventory,inventory list
                        col_event_entity_inventory.inventory.append(ent)

                        # Remove Position component from the item so that it is not displayable on the map - item is picked
                        self.world.remove_component(ent, Position) 

                        # Remove Camera component from the item so that the screen disappears - item is picked
                        try:
                            self.world.remove_component(ent, Camera) 
                        except KeyError:
                            pass

                        # Remove the col_event_entity from Item entity
                        collision.collision_events.remove(col_event_entity)

                        # Remove the col event related to item from the Entity
                        col_event_entity_coll.collision_events.remove(ent)

                        # Report that item was picked up - generate event
                        teleport_event = Event('ITEM_PICKUP', ent, col_event_entity, params={'item' : ent, 'picker' : col_event_entity})
                        self.item_pickup_event_queue.append(teleport_event)
