__all__ = ['CollisionDeletionProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class CollisionDeletionProcessor(esper.Processor):

    __slots__ = ['remove_entity_fnc']

    def __init__(self, remove_entity_fnc):

        super().__init__()

        self.remove_entity_fnc = remove_entity_fnc

    def process(self, *args, **kwargs):

        for ent, (delete_on_collision, collision) in self.world.get_components(components.DeleteOnCollision, components.Collidable):

            # If entity has collided in this loop cycle
            if collision.has_collided:

                # Remove from the world
                self.remove_entity_fnc(ent)

