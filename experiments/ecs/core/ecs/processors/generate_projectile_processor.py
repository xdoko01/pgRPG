__all__ = ['GenerateProjectileProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

class GenerateProjectileProcessor(esper.Processor):
	''' Generate projectiles
		
		- planned before all collision processors
		- planned after command processor - Attack command
	'''

	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		''' TODO - is there any variable from the global world that we want to use here?
		'''

		# Get entities capable of producing projectiles - HasWeapon, on the last attack frame RenderableModel
		for ent, (has_weapon, renderable_model, position) in self.world.get_components(components.HasWeapon, components.RenderableModel, components.Position):
			
			# Check if Model is in the action status and last frame of the action is happening
			if renderable_model.action == has_weapon.get_weapon_action_anim() and renderable_model.is_action_frame:
				
				# Collidable is optional component - entities who are not collidable can generate projectiles
				collidable = self.world.try_component(ent, (components.Collidable))

				# Create an projectile
				has_weapon.create_projectile(ent, position, collidable)
