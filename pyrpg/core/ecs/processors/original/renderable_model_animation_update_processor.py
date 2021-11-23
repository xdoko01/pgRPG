__all__ = ['RenderableModelAnimationUpdateProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from .functions import filter_only_visible

class RenderableModelAnimationUpdateProcessor(esper.Processor):
	''' Shift the animation
		- only once on every displayed entity
	'''
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):

		# Remember updated entities - to prevent several updates on simgle entity
		already_updated = set()

		# Iterate all camaeras
		for cam, (camera) in self.world.get_component(components.Camera):
			
			# Get RenderableModels with Positions
			for ent, (position, renderable_model) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel)):
	
				# Call the update_frame function
				if ent not in already_updated:
					renderable_model.update_frame(position.dir_name)

				# Remember that entity was updated
				already_updated.add(ent)
