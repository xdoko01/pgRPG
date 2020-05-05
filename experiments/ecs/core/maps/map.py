import core.config.config as config

import pygame
from pytmx.util_pygame import load_pygame
from itertools import product

########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()

########################################################
### Module methods
########################################################

def images_rescale(images=[], scale=(64,64)):
	return [pygame.transform.scale(i, scale).convert() if i else None for i in images]

########################################################
### Map class
########################################################

class Map:

	def __init__(self, map_name):
		
		self.name = map_name

		#### TMX load map and properties

		# Load map
		self.tmxdata = load_pygame(config.MAP_PATH + map_name + '.tmx')

		# Rescale images
		self.tmxdata.images = images_rescale(self.tmxdata.images, (64,64))

		# Prepare animation meta-data
		self.anim_last_frame = {}
		for gid, _ in self.tmxdata.tile_properties.items():
			self.anim_last_frame.update({ gid : {'last_frame' : 0, 'last_time' : pygame.time.get_ticks()}})

		# Collision layer number
		self.collision_layer = 2

		# Map properties print(f'Width: {tmxdata.width} Height: {tmxdata.width} TileWidth: {tmxdata.tilewidth} TIleHeight: {tmxdata.tileheight}')
		# With and Height of the map in pixels
		self.width = self.tmxdata.width * 64
		self.height = self.tmxdata.height * 64

		#### Old properties

		#self.ground_layer = [
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		#	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		#]

		#self.wall_layer = self.collision_map = [
		#	[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,2,0,2,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,2,0,2,2,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
		#	[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		#]

		
		#self.visible_tile_layers = ['ground', 'wall']

		#ground_tile = pygame.image.load(config.IMAGE_PATH + "ground_tile.png").convert()
		#wall_tile = pygame.image.load(config.IMAGE_PATH + "wall_tile.png").convert()

		#self.tilewidth = len(self.ground_layer[0])
		#self.tileheight = len(self.ground_layer)

		#self.width = self.tilewidth * 64
		#self.height = self.tileheight * 64

		#self.tileset = {
		#	1 : ground_tile,
		#	2 : wall_tile
		#}
	
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
		x1 = int(x1 // config.TILE_RES)
		y1 = int(y1 // config.TILE_RES)
		x2 = int(x2 // config.TILE_RES)
		y2 = int(y2 // config.TILE_RES)

		for y, x in product(range(y1, y2 + 1), range(x1, x2 + 1)):
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
			if layer == 'ground':

				# Get GID of the tile on the position
				gid = self.tmxdata.get_tile_gid(map_x, map_y, 0)
				
				try:

					# Get the last frame
					last_frame = self.anim_last_frame.get(gid).get('last_frame')
					
					# Check the last time and current time
					delay = pygame.time.get_ticks() - self.anim_last_frame.get(gid).get('last_time')

					frames = self.tmxdata.get_tile_properties(map_x, map_y, 0).get('frames')

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

					return self.tmxdata.get_tile_image(map_x,map_y, 0)

				#return self.tileset.get(self.ground_layer[map_y][map_x], None)
		
			elif layer == 'wall':

				# Get GID of the tile on the position
				gid = self.tmxdata.get_tile_gid(map_x, map_y, 1)
				
				try:

					# Get the last frame
					last_frame = self.anim_last_frame.get(gid).get('last_frame')
					
					# Check the last time and current time
					delay = pygame.time.get_ticks() - self.anim_last_frame.get(gid).get('last_time')

					frames = self.tmxdata.get_tile_properties(map_x, map_y, 1).get('frames')

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

					return self.tmxdata.get_tile_image(map_x,map_y, 1)

				
				#return self.tmxdata.get_tile_image(map_x,map_y,1)

				#return self.tileset.get(self.wall_layer[map_y][map_x], None)
		except (IndexError, ValueError):
			# in cases that we are asking for out of map cells
			return None

	def check_collision(self, x, y):
		try:
			if self.tmxdata.get_tile_gid(x, y, self.collision_layer) !=0 :
				return True
			else:
				return False
		except ValueError:
			return True


