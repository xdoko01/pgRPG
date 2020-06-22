__all__ = ['RenderableModelAnimationActionProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

from .functions import filter_only_visible

class RenderableModelAnimationActionProcessor2(esper.Processor):
	''' Change the action of renderable model in order to display
	correct action animation.

	co takhle prepsat to jako erastotenovo sito
		- a potom porovnat performance
		- novej procesor
			- for RenderableModel -> IDLE
			- for RenderableModel, HasWeapon -> ACTION ANIM, IDLE ANIM
			- for RenderableModel, Motion -> WALK
		- potom aktualizovat frame
			- for RenderableModel, Position - pouze ty na kamerach novy filter filter_only_visible(all_cameras, x)
				- update_frame() ... bez argumentu
	'''
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		
		changed_ent = set()
		
		for ent, (renderable_model, motion) in self.world.get_components(components.RenderableModel, components.Motion):
			if motion.has_moved:
				renderable_model.set_action('walk')
				changed_ent.add(ent)
		
		for ent, (renderable_model, has_weapon) in self.world.get_components(components.RenderableModel, components.HasWeapon):
			if has_weapon.has_attacked and has_weapon.weapon and ent not in changed_ent:
				renderable_model.set_action(has_weapon.get_weapon_action_anim())
				has_weapon.has_attacked = False
				changed_ent.add(ent)

			elif has_weapon.weapon and ent not in changed_ent:
				renderable_model.set_action(has_weapon.get_weapon_idle_anim())
				changed_ent.add(ent)

		for ent, renderable_model in self.world.get_component(components.RenderableModel):	
			if ent not in changed_ent:
				renderable_model.set_action('idle')




class RenderableModelAnimationActionProcessor(esper.Processor):
	''' Change the action of renderable model in order to display
	correct action animation.

	co takhle prepsat to jako erastotenovo sito
		- a potom porovnat performance
		- novej procesor
			- for RenderableModel -> IDLE
			- for RenderableModel, HasWeapon -> ACTION ANIM, IDLE ANIM
			- for RenderableModel, Motion -> WALK
		- potom aktualizovat frame
			- for RenderableModel, Position - pouze ty na kamerach novy filter filter_only_visible(all_cameras, x)
				- update_frame() ... bez argumentu
	'''
	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):

		# Remember updated entities - to prevent several updates on simgle entity
		already_updated = set()

		# Iterate all camaeras
		for cam, (camera) in self.world.get_component(components.Camera):

			# Get all states
			for ent, (position, renderable_model) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel)):
				
				# try to get motion, has_weapon - returns None if not present
				motion = self.world.try_component(ent, components.Motion)
				has_weapon = self.world.try_component(ent, components.HasWeapon)
				is_dead = self.world.try_component(ent, components.IsDead)

				if is_dead:
					renderable_model.set_action('die')
					
					# Direction must be down because only down direction is animated for the dead animation
					position.set_direction('down')

				elif motion and motion.has_moved:
					
					# If entity has moved, action is set to 'walk'
					renderable_model.set_action('walk')
				
				elif has_weapon and has_weapon.weapon_in_use and has_weapon.has_attacked:
					
					# If entity has weapon and the weapon has attacked, set action to proper value
					renderable_model.set_action(has_weapon.get_weapon_action_anim())
					
					# Reset the attack - in case attack key is released animation of attack is no longer displayed
					has_weapon.has_attacked = False

				elif has_weapon and has_weapon.weapon_in_use:
					
					# If entity has weapon but is not attacking, display idle weapon animation
					renderable_model.set_action(has_weapon.get_weapon_idle_anim())
				
				else:
					# Has no weapon, is not moving,
					renderable_model.set_action('idle')

				# Remember that entity was updated
				already_updated.add(ent)

