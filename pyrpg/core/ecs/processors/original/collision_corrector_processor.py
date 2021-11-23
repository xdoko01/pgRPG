__all__ = ['CollisionCorrectorProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class CollisionCorrectorProcessor(esper.Processor):
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		for ent, (collision, position) in self.world.get_components(components.Collidable, components.Position):
			
			# If some collision occured, the collision_event set is not empty
			if collision.collision_events:
				
				# Fix position for the entity that has moved
				position.x = position.lastx
				position.y = position.lasty

				# Clear all collisions
				collision.collision_events.clear()
