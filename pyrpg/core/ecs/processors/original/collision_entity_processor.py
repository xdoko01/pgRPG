__all__ = ['CollisionEntityProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events

import pyrpg.core.config.config as config # for MOVE_SPEED


# TODO - this does not work well - collision of player and npc with brain does not work - player cannot colide but npc can walk into the player
# This is because first entity 1 is fixed and all related collisions with number 1 are deleted, so also NPCs collision events are deleted before they are processed
class CollisionEntityProcessor(esper.Processor):
    ''' It is basically CollisionCorrectorProcessor but also generates events
    on collisions
    '''

    def __init__(self, entity_coll_event_queue, input_command_queue):
        super().__init__()
        self.entity_coll_event_queue = entity_coll_event_queue
        self.input_command_queue = input_command_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        for ent, (position, collision) in self.world.get_components(components.Position, components.Collidable):

            ##### New collision process
            # 1. Iterate all collidable entities
            # 2. Iterate all entities with whom there was a collision
            # 3. Generate collision event
            # 4. Calculate the positions so that objects are not collided - do not use last position - this was causing stuck states

            for col_event_entity in collision.collision_events.copy():

                # Report that entity collision occured - generate event
                collision_event = event.Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
                self.entity_coll_event_queue.append(collision_event)

                # Calculate and update possition
                col_event_entity_pos = self.world.component_for_entity(col_event_entity, components.Position)
                col_event_entity_collidable = self.world.component_for_entity(col_event_entity, components.Collidable)

                # collision on X axis (distance is lower then coll area)
                if abs(col_event_entity_pos.x - position.x) < (col_event_entity_collidable.x + collision.x):
                    # Call move 
                    if position.x < col_event_entity_pos.x: 
                        self.input_command_queue.append(('move', {"entity" : ent, "dx" : -config.MOVE_SPEED}))
                        self.input_command_queue.append(('move', {"entity" : col_event_entity, "dx" : config.MOVE_SPEED}))
                    else:
                        self.input_command_queue.append(('move', {"entity" : ent, "dx" : config.MOVE_SPEED}))
                        self.input_command_queue.append(('move', {"entity" : col_event_entity, "dx" : -config.MOVE_SPEED}))
                    
                    # position.x = position.lastx
                    # col_event_entity_pos.x = col_event_entity_pos.lastx

                # collision on Y axis (distance is lower then coll area)
                if abs(col_event_entity_pos.y - position.y) <= (col_event_entity_collidable.y + collision.y) + 10:
                    # Call move 
                    if position.y < col_event_entity_pos.y: 
                        self.input_command_queue.append(('move', {"entity" : ent, "dy" : -config.MOVE_SPEED}))
                        self.input_command_queue.append(('move', {"entity" : col_event_entity, "dy" : config.MOVE_SPEED}))
                    else:
                        self.input_command_queue.append(('move', {"entity" : ent, "dy" : config.MOVE_SPEED}))
                        self.input_command_queue.append(('move', {"entity" : col_event_entity, "dy" : -config.MOVE_SPEED}))
                    
                    
                    # try to use last position for both
                    #position.y = position.lasty
                    #col_event_entity_pos.y = col_event_entity_pos.lasty

                # Remove the col_event_entity from  entity
                collision.collision_events.remove(col_event_entity)


            ''' Old process
            # If some collision occured, the collision_event set is not empty
            if collision.collision_events:
                
                # Fix position for the entity that has moved
                position.x = position.lastx
                position.y = position.lasty

            # Process everything that collided with entity ent
            for col_event_entity in collision.collision_events.copy():

                # Report that entity collision occured - generate event
                collision_event = Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
                self.entity_coll_event_queue.append(collision_event)

                # Fix position for the entity that has moved
                #position.x = position.lastx
                #position.y = position.lasty

                ##### All below is for removal of collision event from the entities
                # Get the Collidable component of the entity - in order to remove the collision
                
                # Below commented as it caused that NPCs were walking into player
                #col_event_entity_coll = self.world.component_for_entity(col_event_entity, components.Collidable)

                # Remove the col event related to item from the Entity
                # Below commented as it caused that NPCs were walking into player
                #col_event_entity_coll.collision_events.remove(ent)

                # Remove the col_event_entity from  entity
                collision.collision_events.remove(col_event_entity)
            '''
