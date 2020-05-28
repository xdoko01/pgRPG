__all__ = ['RenderDebugProcessor']

import pygame	# for pygame.time, pygame.font and pygame.Color
import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

from .functions import filter_only_visible # for filtering only entities with position on the cameras

class RenderDebugProcessor(esper.Processor):
	''' Information displayed only on visible entities
	using the filter_only_visible function.

	'''

	def __init__(self, window):

		super().__init__()
		self.window = window
		self.font = pygame.font.Font(None, 14)

	def process(self, *args, **kwargs):

		# Get information about required debug information
		debug = kwargs.get('debug', {})

		# Show debug information on all cameras
		for _, (cam_cam) in self.world.get_component(components.Camera):

			for debug_entity, (pos_comp, deb_comp, coll_debug) in filter(lambda x: filter_only_visible(cam_cam, x), self.world.get_components(components.Position, components.Debug, components.Collidable)):
				# Print collision area
				if debug.get('show_collision', False):
					try:
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((pos_comp.x - coll_debug.x,pos_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

			# Show debug information only for displayable entities with Debug flag - only for visible entities
			for debug_entity, (pos_comp, deb_comp, render_comp) in filter(lambda x: filter_only_visible(cam_cam, x), self.world.get_components(components.Position, components.Debug, components.RenderableModel)):

				# Print health
				if debug.get('show_health', False):
					try:
						damageable_debug = self.world.component_for_entity(debug_entity, components.Damageable)
						text = f'Health: {damageable_debug.health}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 60))))
					except KeyError:
						pass

				# Print status
				if debug.get('show_state', False):
					try:
						state_debug = self.world.component_for_entity(debug_entity, components.RenderableModel)
						text = f'State: {state_debug.action}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 50))))
					except KeyError:
						pass

				# Print weapons
				if debug.get('show_weapons', False):
					try:
						weapons_debug = self.world.component_for_entity(debug_entity, components.HasWeapon)
						text = f'Weapon in use: {weapons_debug.get_weapon_in_use()}. All: {weapons_debug.weapons}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 40))))
					except KeyError:
						pass

				# Print wearables
				if debug.get('show_wearables', False):
					try:
						wearables_debug = self.world.component_for_entity(debug_entity, components.CanWear)
						text = f'Wearables: {wearables_debug.wearables}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 30))))
					except KeyError:
						pass

				# Print inventory
				if debug.get('show_inventory', False):
					try:
						inventory_debug = self.world.component_for_entity(debug_entity, components.HasInventory)
						text = f'Inventory: {inventory_debug.inventory}'
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 20))))
					except KeyError:
						pass

				# Print labels
				if debug.get('show_labels', False):
					try:
						label_debug = self.world.component_for_entity(debug_entity, components.Labeled)
						text = str(debug_entity) + ', ' + str(label_debug.id) + ', ' + str(label_debug.name)
						pos = deb_comp.font.render(text, True, pygame.Color('black'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y - 10))))
					except KeyError:
						pass

				
				# Print position
				if debug.get('show_position', False):
					try:
						pos_debug = self.world.component_for_entity(debug_entity, components.Position)
						text = 'Pos: (' + str(int(pos_debug.x)) + ', ' + str(int(pos_debug.y)) + ')' + str(pos_comp.dir_name)
						pos = deb_comp.font.render(text, True, pygame.Color('white'))
						cam_cam.screen.blit(pos, cam_cam.apply(render_comp.topleft((pos_comp.x, pos_comp.y))))
					except KeyError:
						pass

				# Print brain
				if debug.get('show_brain', False):
					try:
						brain_debug = self.world.component_for_entity(debug_entity, components.Brain)
						for cmd_idx, cmd_txt in enumerate(brain_debug.commands):
							color = pygame.Color('red') if cmd_idx == brain_debug.current_cmd_idx else pygame.Color('white')
							cmd = deb_comp.font.render(str(cmd_idx) + ' -> ' + str(cmd_txt), True, color)
							cam_cam.screen.blit(cmd, cam_cam.apply(render_comp.topleft((pos_comp.x, 10 + pos_comp.y + (cmd_idx * 10)))))
					except KeyError:
						pass

				# Print collision area
				if debug.get('show_collision', False):
					try:
						coll_debug = self.world.component_for_entity(debug_entity, components.Collidable)
						pygame.draw.rect(cam_cam.screen, pygame.Color('blue'), pygame.Rect(cam_cam.apply((pos_comp.x - coll_debug.x,pos_comp.y - coll_debug.y)), (2 * coll_debug.x, 2 *coll_debug.y)),1)
					except KeyError:
						pass

				# Print direction of entity
				if debug.get('show_direction', False):
					try:
						pygame.draw.line(cam_cam.screen, pygame.Color('red'), 
							cam_cam.apply((pos_comp.x, pos_comp.y)),
							cam_cam.apply((pos_comp.x + pos_comp.direction[0] * 20, pos_comp.y + pos_comp.direction[1] * 20)),
							2)
					except KeyError:
						pass

			if debug.get('show_map_screen_area', False):
				map_display_area = self.font.render(str(cam_cam.map_screen_rect), True, pygame.Color('white'))
				cam_cam.screen.blit(map_display_area, (0,0))

			# Blit the camera screen on the main game window
			self.window.blit(cam_cam.screen, (cam_cam.screen_pos_x, cam_cam.screen_pos_y))

	def pre_save(self):
		''' Prepare processor for serialization by disabling links to 
		non-serializable components (window).
		'''
		self.window = None
		self.font = None


	def post_load(self, window):
		''' Reconfigure the processor after de-serialization by attaching
		the reference to window again.
		'''
		self.window = window
		self.font = pygame.font.Font(None, 14)
