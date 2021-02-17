__all__ = ['CollisionDeletionProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

class CollisionDeletionProcessor(esper.Processor):
	def __init__(self):

		super().__init__()

	def process(self, *args, **kwargs):

		for ent, (delete_on_collision, collision) in self.world.get_components(components.DeleteOnCollision, components.Collidable):

			# If entity has collided in this loop cycle
			if collision.has_collided:

				# Delete from container TODO - must be done generic
				container = self.world.try_component(ent, components.Container)
				
				if container:
					# Remove from the set of projectiles
					print(f'container.contained_in {container.contained_in}, container.contained_in.projectiles {container.contained_in.list_of_entities}')
					container.contained_in.remove_entity(ent) #HasWeapon component
					
				
				# Remove from the world
				self.world.delete_entity(ent)

