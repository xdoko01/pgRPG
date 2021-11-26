__all__ = ['CollisionCorrectorProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.position import Position

class CollisionCorrectorProcessor(Processor):
    def __init__(self):
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        for ent, (collision, position) in self.world.get_components(Collidable, Position):
            
            # If some collision occured, the collision_event set is not empty
            if collision.collision_events:
                
                # Fix position for the entity that has moved
                position.x = position.lastx
                position.y = position.lasty

                # Clear all collisions
                collision.collision_events.clear()
