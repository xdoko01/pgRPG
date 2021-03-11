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

				# Remove from the world
				self.world.delete_entity(ent)
