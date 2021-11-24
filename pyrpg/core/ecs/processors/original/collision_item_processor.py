__all__ = ['CollisionItemProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events


class CollisionItemProcessor(esper.Processor):
    def __init__(self, item_pickup_event_queue):
        super().__init__()
        self.item_pickup_event_queue = item_pickup_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        for ent, (item, collision) in self.world.get_components(components.Pickable, components.Collidable):

            # Process everything that collided with item
            for col_event_entity in collision.collision_events.copy():
                    
                    # If entity can collect items (has inventory)
                    if self.world.has_component(col_event_entity, components.HasInventory):
                        
                        # Get the HasItem component of the entity
                        col_event_entity_inventory = self.world.component_for_entity(col_event_entity, components.HasInventory) 
                        
                        # Get the Collidable component of the entity - in order to remove the collision
                        col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

                        # Add the Item entity into the HasInventory,inventory list
                        col_event_entity_inventory.inventory.append(ent)

                        # Remove Position component from the item so that it is not displayable on the map - item is picked
                        self.world.remove_component(ent, components.Position) 

                        # Remove Camera component from the item so that the screen disappears - item is picked
                        try:
                            self.world.remove_component(ent, components.Camera) 
                        except KeyError:
                            pass

                        # Remove the col_event_entity from Item entity
                        collision.collision_events.remove(col_event_entity)

                        # Remove the col event related to item from the Entity
                        col_event_entity_coll.collision_events.remove(ent)

                        # Report that item was picked up - generate event
                        teleport_event = event.Event('ITEM_PICKUP', ent, col_event_entity, params={'item' : ent, 'picker' : col_event_entity})
                        self.item_pickup_event_queue.append(teleport_event)
