__all__ = ['CollisionWearableProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events


class CollisionWearableProcessor(esper.Processor):
    def __init__(self, wearable_event_queue):
        super().__init__()
        self.wearable_event_queue = wearable_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        for ent, (item, collision) in self.world.get_components(components.Wearable, components.Collidable):

            # Process everything that collided with wearable entity
            for col_event_entity in collision.collision_events.copy():
                    
                    # If entity (that have collided with wearable) can wear items (CanWear)
                    if self.world.has_component(col_event_entity, components.CanWear):
                        
                        # Get the CanWear component of the entity that picked up Wearable
                        col_event_entity_can_wear = self.world.component_for_entity(col_event_entity, components.CanWear) 
                        
                        # Get the Collidable component of the entity that picked up Wearable - in order to remove the collision
                        col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

                        # Add wearable to the CanWear wearables - only in case that the slot for Wearable is available
                        if not col_event_entity_can_wear.wearables.get(item.bodypart, None):
                            col_event_entity_can_wear.wearables.update({item.bodypart : ent})

                            try:
                                # Remove Position component from the wearable so that it is not displayable on the map - wearable is picked
                                self.world.remove_component(ent, components.Position) 
                                # Remove Camera component from the wearable so that the screen disappears - wearable is picked
                                self.world.remove_component(ent, components.Camera) 
                            except KeyError:
                                pass

                            # Remove the col_event_entity from CanWear entity
                            collision.collision_events.remove(col_event_entity)

                            # Remove the col event related to item from the Wearable
                            col_event_entity_coll.collision_events.remove(ent)

                            # Report that item was weared - generate event
                            wear_event = event.Event('WEARABLE_WEARED', ent, col_event_entity, params={'wearable' : ent, 'picker' : col_event_entity})
                            self.wearable_event_queue.append(wear_event)
