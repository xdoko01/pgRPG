__all__ = ['CollisionDeletionProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.delete_on_collision import DeleteOnCollision
from pyrpg.core.ecs.components.original.collidable import Collidable

class CollisionDeletionProcessor(Processor):

    __slots__ = ['remove_entity_fnc']

    def __init__(self, remove_entity_fnc):

        super().__init__()

        self.remove_entity_fnc = remove_entity_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        for ent, (delete_on_collision, collision) in self.world.get_components(DeleteOnCollision, Collidable):

            # If entity has collided in this loop cycle
            if collision.has_collided:

                # Remove from the world
                self.remove_entity_fnc(ent)

