__all__ = ['RenderDebugProcessor']

import pygame	# for pygame.time, pygame.font and pygame.Color
import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

from core.config.fonts import GAME_DEBUG_FONT # for the debug font

from .functions import filter_only_visible # for filtering only entities with position on the cameras

from pprint import pformat # Nice formating of dictionaries for debug output


class RenderDebugProcessor(esper.Processor):
	''' Information displayed only on visible entities
	using the filter_only_visible function.

	'''

	def __init__(self, window):

		super().__init__()

		self.window = window

	def process(self, *args, **kwargs):
		''' Dictionary containing Debug settings is passed to
		process function on purpose (more efficient would be to have it
		loaded on init). In order to change the debug information
		dynamically while the game runs.
		'''

		# Get information about required debug information
		debug = kwargs.get('debug', {})

		# Show debug information on all cameras
		for _, (cam_cam) in self.world.get_component(components.Camera):

			# Show debug information to all entities with Position and Debug component
			#for debug_entity, (pos_comp, deb_comp, coll_debug) in filter(lambda x: filter_only_visible(cam_cam, x), self.world.get_components(components.Position, components.Debug, components.Collidable)):
			for debug_entity, (pos_comp, deb_comp) in filter(lambda x: filter_only_visible(cam_cam, x), self.world.get_components(components.Position, components.Debug)):

				# Here all the debug information are gathered
				debug_text = ''

				# Mark collision area
				if debug.get('show_collision', False):
					try:
						coll_debug = self.world.component_for_entity(debug_entity, components.Collidable)
						pygame.draw.rect(
							cam_cam.screen,
							pygame.Color('blue'),
							pygame.Rect(
								cam_cam.apply((pos_comp.x - coll_debug.x, pos_comp.y - coll_debug.y)), 
								(2 * coll_debug.x, 2 * coll_debug.y)
								),
							1)
					except KeyError:
						pass

				# Mark direction of an entity
				if debug.get('show_direction', False):
					try:
						pygame.draw.line(
							cam_cam.screen,
							pygame.Color('red'), 
							cam_cam.apply((pos_comp.x, pos_comp.y)),
							cam_cam.apply((pos_comp.x + pos_comp.direction[0] * 20, pos_comp.y + pos_comp.direction[1] * 20)),
							1)
					except KeyError:
						pass

				# Show entity labels
				if debug.get('show_labels', False):
					try:
						label_debug = self.world.component_for_entity(debug_entity, components.Labeled)
						debug_text += f'{debug_entity}, {label_debug.id}, {label_debug.name}\n'
					except KeyError:
						pass

				# Show position info
				if debug.get('show_position', False):
					try:
						pos_debug = self.world.component_for_entity(debug_entity, components.Position)
						debug_text += f'Pos:({int(pos_debug.x)}, {int(pos_debug.y)})\nDir: {pos_comp.dir_name}\n'
					except KeyError:
						pass

				# Show model status info
				if debug.get('show_state', False):
					try:
						state_debug = self.world.component_for_entity(debug_entity, components.RenderableModel)
						debug_text += f'State: {state_debug.action}\n'
					except KeyError:
						pass

				# Show health info
				if debug.get('show_health', False):
					try:
						damageable_debug = self.world.component_for_entity(debug_entity, components.Damageable)
						debug_text += f'Health: {damageable_debug.health}\n'
					except KeyError:
						pass

				# Show inventory info
				if debug.get('show_inventory', False):
					try:
						inventory_debug = self.world.component_for_entity(debug_entity, components.HasInventory)
						debug_text += f'Inventory: {pformat(inventory_debug.inventory)}\n'
					except KeyError:
						pass

				# Show wearables info
				if debug.get('show_wearables', False):
					try:
						wearables_debug = self.world.component_for_entity(debug_entity, components.CanWear)
						debug_text += f'Wearables:\n{pformat(wearables_debug.wearables, width=50)}\n'
					except KeyError:
						pass

				# Show weapons info
				if debug.get('show_weapons', False):
					try:
						weapons_debug = self.world.component_for_entity(debug_entity, components.HasWeapon)
						debug_text += f'Weapon in use: {weapons_debug.get_weapon_in_use()}\nAll weapons:\n{pformat(weapons_debug.weapons, width=50)}\n'
					except KeyError:
						pass

				
				# Blit debug text info gathered above - except brain process
				text_surf = GAME_DEBUG_FONT.render(debug_text) # Text to Surface
				cam_cam.screen.blit(
					text_surf,
					cam_cam.apply(
						(pos_comp.x - text_surf.get_width() // 2, pos_comp.y - text_surf.get_height())
						)
					)

				
				# Show brain processing
				if debug.get('show_brain', False):
					try:
						brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
						for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
							color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
							cmd_surf = GAME_DEBUG_FONT.render(f'{cmd_idx} -> {cmd_txt}', color=color)
							cam_cam.screen.blit(
								cmd_surf, 
								cam_cam.apply(
									(pos_comp.x, pos_comp.y + (cmd_idx * GAME_DEBUG_FONT._get_text_height()))
									)
								)
					except KeyError:
						pass
				

			# Show the area of the displayed map
			if debug.get('show_map_screen_area', False):
				map_display_area = GAME_DEBUG_FONT.render(f'({int(cam_cam.map_screen_rect[0])}, {int(cam_cam.map_screen_rect[1])})', color=pygame.Color('white'))
				cam_cam.screen.blit(map_display_area, (0,0))

			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window).
		'''
		self.window = None


	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window

