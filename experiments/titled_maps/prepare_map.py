import json

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
		self.animations = { 50 : [(duration, gid reference),(duration, gid reference),(duration,gid reference)]}

		### 
		# 1/ Read all used images, convert and save into images under their GID
		# 2/ Read all the animation definition in self.animations - create objects contaning frames duration last time and actual index (private)
		# 4/ DISPLAY
			- method get-tile_images_by_rect
				-	first try to display from animations - check the frame time here
				-	if failed display from images (KeyError)
	
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



sample_map = Map('experiments/titled_maps/resources/maps/test_map.json')
print(sample_map.layers)
print(sample_map.collision_layer.data)
print(sample_map.used_tiles)