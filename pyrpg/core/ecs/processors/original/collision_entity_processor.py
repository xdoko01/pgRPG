__all__ = ['CollisionEntityProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.collidable import Collidable

# For creation of events
from pyrpg.core.events.event import Event

import pyrpg.core.config.config as config # for MOVE_SPEED

# TODO - this does not work well - collision of player and npc with brain does not work - player cannot colide but npc can walk into the player
# This is because first entity 1 is fixed and all related collisions with number 1 are deleted, so also NPCs collision events are deleted before they are processed
class CollisionEntityProcessor(Processor):
    ''' It is basically CollisionCorrectorProcessor but also generates events
    on collisions
    '''

    def __init__(self, entity_coll_event_queue, input_command_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_coll_event_queue = entity_coll_event_queue
        self.input_command_queue = input_command_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (position, collision) in self.world.get_components(Position, Collidable):

            ##### New collision process
            # 1. Iterate all collidable entities
            # 2. Iterate all entities with whom there was a collision
            # 3. Generate collision event
            # 4. Calculate the positions so that objects are not collided - do not use last position - this was causing stuck states

            for col_event_entity in collision.collision_events.copy():

                # Report that entity collision occured - generate event
                collision_event = Event('COLLISION', ent, col_event_entity, params={'entity1' : ent, 'entity2' : col_event_entity})
                self.entity_coll_event_queue.append(collision_event)

                # Calculate and update possition
                col_event_entity_pos = self.world.component_for_entity(col_event_entity, Position)
                col_event_entity_collidable = self.world.component_for_entity(col_event_entity, Collidable)

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

