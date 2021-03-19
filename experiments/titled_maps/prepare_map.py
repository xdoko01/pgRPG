import pygame
import json
from pytmx.util_pygame import load_pygame

'''
IN PYSCROLL
	- AnimationToken is a class containing information about animated cell
	- it contains data about
		- all the possitions x,y,l where the animation is present on the map
		- all the frames of the animation - frame is tuple consisting of image reg and duration
		- last_time when animation was updated
	
	- _animation_queue is list of AnimationTokens
	- process_animation_queue function
		- checks if it is time for the token to change the image to the next frame
		- takes all positions of the animated tile (x,y,l)
		... unreadable

'''

class Layer:

	def __init__(self, layer_dict):

		self.width = layer_dict.get('width')
		self.height = layer_dict.get('height')
		self.data = [layer_dict.get('data',[])[h*self.width:(h+1)*self.width] for h in range(self.height)]

class Map:

	def __init__(self, filepath):

		self.layers = []
		self.collision_layer = None
	
		# All used images are stored here - images['gid'] only once and nowhere else

		

		# List of animation objects - frames and last time
		#self.animations = { 50 : [(duration, gid reference),(duration, gid reference),(duration,gid reference)]}

		### 
		# 1/ Read all used images, convert and save into images under their GID
		# 2/ Read all the animation definition in self.animations - create objects contaning frames duration last time and actual index (private)
		# 4/ DISPLAY
		#	- method get-tile_images_by_rect
		#		-	first try to display from animations - check the frame time here
		#		-	if failed display from images (KeyError)
	
		##### Load tileset
		# All the map tiles must be stored
		

		##### Load map
		try:		
			with open(filepath, 'r') as map_file:
				json_map_data = map_file.read()
				map_data = json.loads(json_map_data)
		except FileNotFoundError:
			print(f"Map file {filepathfile} not found.")
			raise

		# Load map properties
		self.width = map_data.get('width')
		self.height = map_data.get('height')
		self.tilewidth = map_data.get('tilewidth')
		self.tileheight = map_data.get('tileheight')

		# Load layers
		for layer in map_data.get('layers'):
			if layer.get('visible', True):
				self.layers.append(Layer(layer))
			
			for property in layer.get('properties', []):
				if property.get('name', None) == 'collisionLayer' and property.get('value', False):
					self.collision_layer = Layer(layer)

		# Get all used tile numbers - tiles for which I need the data - and store them. Key is the id
		#
		self.images = {}



		self.used_tiles = set()
		for layer in self.layers:
			s = layer.data
			self.used_tiles.union(s)

# # #

pygame.init()
window = pygame.display.set_mode((850,850))

tmxdata = load_pygame('experiments/titled_maps/resources/maps/test_map.tmx')
tmxdata_dark_male = load_pygame('experiments/titled_maps/resources/maps/darkmale.tmx')

def images_rescale(images=[], scale=(64,64)):
	return [pygame.transform.scale(i, scale) if i else None for i in images]

tmxdata.images = images_rescale(tmxdata.images, (64,64))

print(tmxdata.images)

print(tmxdata.layers[2].data)

print(f'Width: {tmxdata.width} Height: {tmxdata.width} TileWidth: {tmxdata.tilewidth} TIleHeight: {tmxdata.tileheight}')

print(tmxdata.get_tile_image(1,1,1))
print(tmxdata.get_tile_gid(1,1,1)) # 9
print(tmxdata.get_tile_gid(1,1,1))

# get all the tiles with properties
print(tmxdata.tile_properties)

# animations with meta data
animations = {}
for gid, props in tmxdata.tile_properties.items():
	animations.update({ gid : 0})

print(animations)

print(tmxdata.get_tile_properties(1,1,0))

for layer in tmxdata.visible_tile_layers: print(layer)


print(tmxdata_dark_male.tile_properties)

running = True

while running:

	# Read the keys pressed, mouse, win resize etc.
	key_events = pygame.event.get()

	# Check for End Game
	for event in key_events:
		if event.type == pygame.QUIT:
			running = False

	for num, img in enumerate(tmxdata.images):
		if img:
			window.blit(img, ((num % 20) * 64, (num // 20) * 64))

	window.blit(tmxdata.get_tile_image_by_gid(9), (0, 0))

	pygame.display.flip()

pygame.quit()
