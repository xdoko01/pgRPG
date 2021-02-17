__all__ = ['ClearTemporaryEntityProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pygame	# for pygame.time.get_ticks()


class ClearTemporaryEntityProcessor(esper.Processor):
	''' Delete for example projectiles
	'''
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		
		# Get all temporary components
		for ent, temporary in self.world.get_component(components.Temporary):

			# Compare if the entity lived long enough
			if pygame.time.get_ticks() - temporary.creation_time > temporary.ttl:
				
				# Delete from container TODO - must be done generic
				container = self.world.try_component(ent, components.Container)
				
				if container:
					# Remove from the set of entities generated and kept on Factory level
					print(f'container.contained_in {container.contained_in}, container.contained_in.list_of_entities {container.contained_in.list_of_entities}')
					container.contained_in.remove_entity(ent) #Entity component
					
				
				# Remove from the world
				self.world.delete_entity(ent)
