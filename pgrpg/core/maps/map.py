'''
For tests call python -m pgrpg.core.maps.map -v
'''
from pgrpg.core.config import GAME # for TILE_RES_PX
from pgrpg.core.config import FILEPATHS # MAP_PATH # MAP_PATH

import pygame
from pytmx.util_pygame import load_pygame
from itertools import product
from pathlib import Path

########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()

########################################################
### Module globals
########################################################


########################################################
### Module functions
########################################################

def images_rescale(images=[], scale=(64, 64)):
	return [pygame.transform.scale(i, scale) if i else None for i in images]

########################################################
### Map class
########################################################

class Map:

	def __init__(self, map_name):

		
		self.name = map_name

		#### TMX load map and properties

		# Load map
		self.tmxdata = load_pygame(FILEPATHS["MAP_PATH"] / str(map_name + '.tmx'))


		# Rescale images
		self.tmxdata.images = images_rescale(self.tmxdata.images, (GAME["TILE_RES_PX"], GAME["TILE_RES_PX"]))

		# Prepare animation meta-data
		self.anim_last_frame = {}
		for gid, _ in self.tmxdata.tile_properties.items():
			self.anim_last_frame.update({ gid : {'last_frame' : 0, 'last_time' : pygame.time.get_ticks()}})

		# Visible layers

		# Collision layer number - Tiled properties need to be 'collisionLayer=True'
		self.collision_layer = 2

		# Map properties print(f'Width: {tmxdata.width} Height: {tmxdata.width} TileWidth: {tmxdata.tilewidth} TIleHeight: {tmxdata.tileheight}')
		# With and Height of the map in pixels
		self.width = self.tmxdata.width * GAME["TILE_RES_PX"]
		self.height = self.tmxdata.height * GAME["TILE_RES_PX"]

		# Generate the graph for pathfinding on the given map
		self.path_graph = self.generate_path_graph()

		# Pre-render static (non-animated) tiles per layer for fast rendering.
		# anim_tile_positions: {layer_index: [(tile_x, tile_y), ...]}
		# static_surfaces:     {layer_index: pygame.Surface (full map size)}
		# Built once at load time; static_surfaces is blitted with a single
		# Surface.blit call per layer each frame instead of per-tile blits.
		self.anim_tile_positions = self._find_animated_tiles()
		self.static_surfaces = self._build_static_surfaces()

	def info(self):
		print(f'Tile dims: {self.tmxdata.width=}, {map.tmxdata.height=}')
		print(f'Pixel dims: {self.width=}, {map.height=}')
		print(f'All layers: {self.tmxdata.layers}')
		print(f'Visible Layers: {[l for l in self.tmxdata.visible_layers]}')

	def print_layer(self, layer):
		print(f'Layer name: {self.tmxdata.layers[layer].name}')
		print(f'Layer props: {self.tmxdata.layers[layer].visible=}, {self.tmxdata.layers[layer].properties=}')

		for y in range(map.tmxdata.height):
			print()
			for x in range(map.tmxdata.width):
				gid = map.tmxdata.get_tile_gid(x, y, layer)
				print(f'{" " if gid == 0 else chr((gid % 32)+64)}',end='')
		print()

	def print_layer_path(self, path, layer):
		print(f'Layer name: {self.tmxdata.layers[layer].name}')
		print(f'Layer path: {path}')
		
		for y in range(map.tmxdata.height):
			print()
			for x in range(map.tmxdata.width):
				gid = map.tmxdata.get_tile_gid(x, y, layer)
				if (x,y) in path:
					print('X', end='')
				else:
					print(f'{" " if gid == 0 else chr((gid % 32)+64)}', end='')
		print()


	def get_tile_images_by_rect(self, layer, rect):
		''' Get all the map tiles that are in the camera view as
		an iterator.

			:type rect: tuple ... rectancle of camera in pixel coordinates
		'''

		# Convert the camera rectancle tuple to variables
		# x1,y1 specifies top left corner in pixel coordinates
		# x2,y2 specifies botom right corner in pixel coordinates
		(x1, y1, x2, y2) = rect

		# Calculate the topleft and bottom-right tile map cell positions to display
		x1 = int(x1 // GAME["TILE_RES_PX"]) #0 -> 0
		y1 = int(y1 // GAME["TILE_RES_PX"]) #0 -> 0
		x2 = int(x2 // GAME["TILE_RES_PX"]) #640 -> 10+1 ... 10(real)
		y2 = int(y2 // GAME["TILE_RES_PX"]) #480 -> 8+1  ... 11(real)

		for y, x in product(range(y1, min(y2 + 1, self.tmxdata.height)), range(x1, min(x2 + 1, self.tmxdata.width))): # added min function so that small maps are not throwing errors
			tile = self.get_tile_image(x, y, layer)
			if tile:
				yield x, y, tile

		'''
		 			try:
                        # animated, so return the correct frame
                        yield x, y, l, at[(x, y, l)]
				        #self._animated_tile = dict()     # mapping of tile substitutions when animated


                    except KeyError:

                        # not animated, so return surface from data, if any
                        yield x, y, l, images[gid]
		'''

	def get_tile_image(self, map_x, map_y, layer) -> pygame.Surface:
		''' Return the Surface of the particular tile
		 try:
			# animated, so return the correct frame
			return self._animated_tile[(x, y, l)]

		except KeyError:

			# not animated, so return surface from data, if any
			return self._get_tile_image(x, y, l)

		'''

		# animation data are returned in this method
		#print(tmxdata.get_tile_properties(1,1,1))
		#{'id': 781, 'width': 32, 'height': 32, 'frames': [AnimationFrame(gid=9, duration=101), AnimationFrame(gid=37, duration=101), AnimationFrame(gid=38, duration=101), AnimationFrame(gid=39, duration=101), AnimationFrame(gid=40, duration=101), AnimationFrame(gid=41, duration=101), AnimationFrame(gid=42, duration=101), AnimationFrame(gid=43, duration=101)]}


		try:
			# Get GID of the tile on the position
			gid = self.tmxdata.get_tile_gid(map_x, map_y, layer)
			
			try:

				# Get the last frame
				last_frame = self.anim_last_frame.get(gid).get('last_frame')
				
				# Check the last time and current time
				delay = pygame.time.get_ticks() - self.anim_last_frame.get(gid).get('last_time')

				frames = self.tmxdata.get_tile_properties(map_x, map_y, layer).get('frames')

				if delay >= frames[last_frame].duration:

					# store the next frame and update the time
					next_frame = last_frame + 1 if last_frame < len(frames) - 1 else 0

					self.anim_last_frame.update({gid : {'last_frame' : next_frame, 'last_time' : pygame.time.get_ticks()}})
					
					# return animation
					return self.tmxdata.get_tile_image_by_gid(frames[next_frame].gid)

				else:

					# return animation
					return self.tmxdata.get_tile_image_by_gid(frames[last_frame].gid)

			except AttributeError:

				return self.tmxdata.get_tile_image(map_x, map_y, layer)

		except (IndexError, ValueError):
			# in cases that we are asking for out of map cells
			return None

	def check_collision(self, tile_x, tile_y) -> bool:
		try:
			return bool(self.tmxdata.get_tile_gid(tile_x, tile_y, self.collision_layer) != 0)
		except ValueError:
			return True

	def get_tiles_in_line(self, source_px: tuple, target_px: tuple) -> tuple:
		'''Yield the tiles between 2 points in px. Tiles coordinates are returned in
		lazy mode and in the raster specified by tile_res.

		Tiles include both starting and ending tiles.
		'''
		sign = lambda x: -1 if x < 0 else 1
		
		dx = target_px[0] - source_px[0]
		dy = target_px[1] - source_px[1]

		sx, sy = sign(dx), sign(dy)

		# Starting position
		x, y = source_px[0], source_px[1]

		if abs(dx) > abs(dy):
			x_incr = sx * GAME["TILE_RES_PX"]
			y_incr = x_incr * dy/dx

			while sx*x < sx*target_px[0]:
				#print(f'x:{x}, y:{y}, sx*x:{sx*x}, sx*target_px[0]:{sx*target_px[0]}')
				yield (x // GAME["TILE_RES_PX"], int(y // GAME["TILE_RES_PX"]))
				x = x + x_incr
				y = y + y_incr

		else:
			y_incr = sy * GAME["TILE_RES_PX"]
			x_incr = y_incr * dx/dy

			while sy*y < sy*target_px[1]:
				#print(f'x:{x}, y:{y}, sy*y:{sy*y}, sy*target_px[1]:{sy*target_px[1]}')
				yield (int(x // GAME["TILE_RES_PX"]), y // GAME["TILE_RES_PX"])
				x = x + x_incr
				y = y + y_incr

	def check_collision_in_line(self, source_px: tuple, target_px: tuple) -> bool:
		'''Check if on line between 2 points in pixels is some tile from the
		collision layer
		'''
		# Iterate every tile in line
		for tile in self.get_tiles_in_line(source_px, target_px):
	
			# If the tile is collidable end with True
			if self.check_collision(tile[0], tile[1]):
				return True
		
		# No tile in line is collidable
		return False
	
	def is_walkable(self, tile: tuple) -> bool:
		'''Is within map and is walkable (no obstacle)'''
		return (0 <= tile[0] <= self.tmxdata.width - 1) and (0 <= tile[1] <= self.tmxdata.height - 1) and self.tmxdata.get_tile_gid(tile[0], tile[1], self.collision_layer) == 0

	def generate_path_graph(
			self, 
			avail_moves: tuple=(
				(0,-1), #up
				(0,1), #down
				(-1,0), #left
				(1,0) #right
			)
		) -> dict:
		"""Generate the graph for pathfinding from the map data"""

		path_graph = dict()
		cost = 1 # all distance between nodes is set to 1

		# Iterate all tiles self.tmxdata.width - 1, self.tmxdata.height - 1
		for y in range(self.tmxdata.height):
			for x in range(self.tmxdata.width):
				# If the tile is walkable
				if self.tmxdata.get_tile_gid(x, y, self.collision_layer) == 0:
					neighbours = []
					for d in avail_moves:
						if self.is_walkable(tile=(x+d[0],y+d[1])):
							neighbours.append(((x+d[0],y+d[1]), cost))
					path_graph.update({(x,y): neighbours})		
	
		return path_graph

	def _find_animated_tiles(self) -> dict:
		"""Return {layer_index: [(tile_x, tile_y), ...]} for tiles that have animation frames.

		Called once at map load time. The result drives per-frame animated tile blitting
		so that static_surfaces can skip those positions.
		"""
		result = {}
		for layer in self.tmxdata.visible_tile_layers:
			positions = []
			for y in range(self.tmxdata.height):
				for x in range(self.tmxdata.width):
					if not self.tmxdata.get_tile_gid(x, y, layer):
						continue
					props = self.tmxdata.get_tile_properties(x, y, layer)
					if props and props.get('frames'):
						positions.append((x, y))
			if positions:
				result[layer] = positions
		return result

	def _build_static_surfaces(self) -> dict:
		"""Pre-render all non-animated tiles per visible layer to full-map Surfaces.

		Returns {layer_index: pygame.Surface} where each Surface has pixel dimensions
		(map_width_px, map_height_px) and contains every non-animated tile for that layer.
		Animated tile positions are left transparent so they can be overlaid each frame.

		Memory: num_visible_layers × map_width_px × map_height_px × 4 bytes (RGBA).
		"""
		tile_px = GAME["TILE_RES_PX"]
		surfaces = {}
		for layer in self.tmxdata.visible_tile_layers:
			surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
			anim_set = set(self.anim_tile_positions.get(layer, []))
			for y in range(self.tmxdata.height):
				for x in range(self.tmxdata.width):
					if (x, y) in anim_set:
						continue  # animated — rendered per-frame by the processor
					tile = self.tmxdata.get_tile_image(x, y, layer)
					if tile:
						surface.blit(tile, (x * tile_px, y * tile_px))
			# Convert to display pixel format so future blits bypass software alpha
			# blending. SRCALPHA is kept during construction for correct per-tile
			# compositing; convert_alpha() preserves per-pixel alpha while enabling
			# SDL's fast display-format blit path.
			surfaces[layer] = surface.convert_alpha()
		return surfaces

	def get_path_bfs(
			self,
			start: tuple, 
			end: tuple,
			inc_start: bool=False, 
			avail_moves: tuple=(
				(0,-1), #up
				(0,1), #down
				(-1,0), #left
				(1,0) #right
			)
		) -> list:

		print(f'FINDING PATH ... {start=}, {end=}')
		if start == end: return []

		visited = set()
		queue = []
		pre = dict()
		path = []

		# Record where I am
		queue.append(start)

		while queue:

			curr = queue.pop(0)

			# Check if I am on the end - finish
			if curr == end:
				# Print the path
				path.append(end)
				pre_path = pre[end]
				while pre_path != start:
					path.append(pre_path)
					pre_path = pre[pre_path]

				if inc_start: path.append(start)
				path.reverse() # from start to end
				return path


			else:
				# Mark as visited
				visited.add(curr)

				for move in avail_moves:
					next = (curr[0] + move[0], curr[1] + move[1])
					if self.is_walkable(next) and next not in visited and next not in queue:
						# Add into the queue
						queue.append(next)
						# Remember from which point you are continuing
						pre[next] = curr

		return [] # no path found

	def get_path_checkpoints(self, path:list) -> list:
		'''Extract only points from the path where
		direction is changed - checkpoints

		Path needs to include start point and end point.

		Point(x=0, y=1), (0,0) #start
		Point(x=1, y=1), (1,0) #keep - next is changed
		Point(x=1, y=2), (0,1)
		Point(x=1, y=3), (0,1)
		Point(x=1, y=4), (0,1)
		Point(x=1, y=5), (0,1)
		Point(x=1, y=6), (0,1)
		Point(x=1, y=7), (0,1)  #keep - next is changed
		Point(x=2, y=7), (1,0)
		Point(x=3, y=7), (1,0)
		Point(x=4, y=7), (1,0)
		Point(x=5, y=7), (1,0)
		Point(x=6, y=7), (1,0)
		Point(x=7, y=7), (1,0)  #keep - next is changed
		Point(x=7, y=6), (0,-1)
		Point(x=7, y=5), (0,-1)
		Point(x=7, y=4)  (0,-1) #end - always keep
		
			0    1,2 
			1    1,3 ... 0,1 #out
			2    1,4 ... 0,1 #out
			3    1,5 ... 0,1 #out
			4    1,6 ... 0,1 #out
			5    1,7 ... 0,1 #keep
			6    2,7 ... 1,0

		'''

		if len(path) < 2: return path
		#assert len(path) >= 2 # at least start and end

		movement = None
		checkpoints = []

		for i in range(len(path)-1):
			if (path[i+1][0] - path[i][0] , path[i+1][1] - path[i][1]) != movement:
				checkpoints.append(path[i])
				movement = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])

		# Always append end 
		checkpoints.append(path[-1])
		
		# Always remove start
		checkpoints.pop(0)

		return checkpoints


from dataclasses import dataclass

@dataclass
class MapMock:
	get_path_bfs = lambda self,start,end,inc_start=False,avail_moves=((0,0)): [(1,1),(2,2),(3,3)]
	get_path_checkpoints = lambda self, path: ((1,1),(2,2),(3,3))

if __name__ == '__main__':

	window = pygame.display.set_mode((640,480), 0, 24)
	
	map = Map(map_name='test_arena_sand')

	map.info()

	map.print_layer(0)
	map.print_layer(1)
	map.print_layer(2)

	path = map.get_path_bfs(start=(5,5), end=(50,50))
	path = map.get_path_bfs(start=(50,50), end=(5,5))

	map.print_layer_path(layer=2, path=path)
