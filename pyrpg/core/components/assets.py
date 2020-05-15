''' pyrpg/pyrpg/core/components/assets.py 

Asset class manages effective usage of memory by creating and maintaining always only
one instance for every model. Model represents graphical data of some game entity
such as enemies, map titles etc.

Other objects in the game might request creation of some particular object (for
example new enemy). They are doing so by calling Assets class method. If graphical
representtion of enemy (model) is already created, method returns pointer to this object
(model) with no need to creating a new one in the memory. If such model does not exists
in the memory yet, it is created and stored in the list of all assets for further use.

Model has following properties:

		model_name		...	Name of the model 
		collision_area	...	Rectancular area used for collision detection
		texture_offset	...	Used for calibration of texture on the screen
		texture_data 	...	Contains individual animation tile frames
		texture_length 	... Contains lenght of animation of actions
		texture_dynamic	...	Indicates if action is auto-animated or not
		texture_file	... File defining the model's graphical data
		(obsolete) supported_states ... not needed as the states are keys in texture 
							related dictionaries.

Structure of files that store model information

One model is represented by several files. File model.json, texture.json and texture.png.

- model.json 	...	contains information about path to texture.json, information about 
					collision area of the model, information about particular images that
					should be rendered for particular model actions (such as walk, die, 
					etc.). File can contain reference to other model (parent) from which
					the data are taken first and then overridden by child data.

		Example of model.json file 

		{ 
		  "prototype"	   : "key",				# Load data from prototype first	
		  "model_name"     : "Grey key",
		  
		  "texture_data"   : {
		    "default"     : [					# Name of the action 
												  (overload from prototype)
		      {
		        "duration":0,					# Time in ms to display tileId
		        "tileid":0						# Tile from texture.png to display
		      },
		      {
		        "duration":0,
		        "tileid":1
		      },
		      {       
		        "duration":0,
		        "tileid":3
		      }
		    ]
		  }
		}

		Example of prototype_model.json file

		{
		  "prototype"	   : "item"				# Load data from yet another 
		  										  prototype first

		  "texture_offset" : [0, 0],			# Offset calibration overload 
		  										  from prototype

		  "collision_area" : [0.25, 0.25],		# Collision area overload 
		  										  from prototype

		  "model_name"     : "Key",				# Name overload from prototype
		  
		  "texture_data"   : {					# Data related to texture_file 
		  										  from prototype
		    "default"     : [
		      {
		        "duration":0,
		        "tileid":0
		      }
		    ]
		  }
		}

		Example of prototype_prototype_model.json file

		{
		  "texture_file"   : "textures/keys.json",	# Texture file is taken from 
		  											  here (prototype)

		  "texture_offset" : [0, 0],				# Offset calibration of the 
		  											  texture on the screen

		  "collision_area" : [0, 0],				# Collision area for collision 
		  											  detection

		  "model_name"     : "Item"		  
		}

- texture.json  ...	contains information about texture.png file necessary to read 
					thegraphical file correctly. File is generated from Tiled 
					software automatically upon import of picture with tiles. It 
					contains information necessary for successful parsing of the 
					graphical file - in order to identify and load the correct tile from
					the picture file

		Example of texture.json file

		{ 
		  "backgroundcolor":"#000000",
		  "columns":4,
		  "image":"assets/textures/keys.png",
		  "imageheight":32,
		  "imagewidth":128,
		  "margin":0,
		  "name":"keys",
		  "spacing":0,
		  "tilecount":4,
		  "tiledversion":"1.2.4",
		  "tileheight":32,
		  "tilewidth":32,
		  "transparentcolor":"#000000",
		  "type":"tileset",
		  "version":1.2
		}

- texture.png 	... actual file containing graphical representation of the file. Before the file can be 
					used, it needs to be processed by Tiled software in order to generate texture.json 
					file that is necessary for prsing of the picture.

'''

import json # necessary to parse json files
import pygame # necessary for extraction of tiles from image file
import ctypes # to show number of references to an instance
import functools # for cache decorator

# load and store config dict as cfg.config
# here necessary for loading tile resolution and paths
#import pyrpg.constants.config as cfg 


class TileModel:
	""" 
	Stores tile texture and other information about the model. Model
	is assigned to the entity (for example MapEntity) and represents
	graphical features - graphical animation, collision areas, display
	properties.
	Models are stored in Asset class dictionary in order not to duplicate
	the same model in the memory several times - i.e. multiple entities
	share the same model. For example all skeleton characters will share 
	only one skeleton model. (Flyweight design pattern)
	"""

	def __init__(self, path, json_file):
		"""
		Method creates all model properties and calls private
		_load_model method that fills the properties with data
		"""

		self.model_name = None
		self.collision_area = None
		self.texture_offset = None
		self.texture_data = None
		self.texture_length = None
		self.texture_dynamic = None
		self.texture_file = None

		self._load_model(path, json_file)

	def _load_model(self, path, json_file, child_ref=None):
		"""
		Method that parses json files, extracts the data about
		the model and saves them to instance variables.
		Parsing is done recursivelly in case json file contains
		prototype key.
		"""

		# Read the model.json		
		try:		
			with open(path + json_file, 'r') as model_file:
				json_model_data = model_file.read()
				model_data = json.loads(json_model_data)
		except FileNotFoundError:
			print(f"Model file {path + json_file} not found.")
			raise

		# Store texture_file path. If not found it remains None.
		# This must be done before recursive call !
		self.texture_file = str(model_data.get('texture_file', None))

		# Check if model must use prototype for its creation
		prototype = str(model_data.get('prototype', ''))

		# If prototype found call recursivelly method on json containing data about 
		# the prototype. At the same time pass reference to the original model
		# so that information get from prototype can be stored also on the original
		# model.
		if prototype: self._load_model(path, prototype + '.json', child_ref=self)

		# Store all the model data except textures and prototype. If on original
		# model, store it on the original. If deep in recursion, store it on the
		# child_ref reference.
		for meta_key, meta_value in model_data.items():
			if meta_key not in ['texture_data', 'prototype']: setattr(child_ref if child_ref != None else self, meta_key, meta_value)

		# If currently processed json file contains data about textures, process 
		# them. Otherwise, skip them.
		if model_data.get('texture_data', {}):

			# Open the file with definition of texture tiles. If current json file
			# does not contain path to the texture file then check if predecesors
			# had this information stored already. That is why it was important to
			# store texture_file before going to the recursion.
			try:	
				with open(path + model_data.get('texture_file',(child_ref if child_ref != None else self).texture_file), 'r') as tex_file:
					json_tex_data = tex_file.read()
					tex_data = json.loads(json_tex_data)	
			except FileNotFoundError:
				print(f"Texture info file {path + model_data.get('texture_file', '')} not found.")
				raise

			# Continue with opening actual file with textures based on information
			# stored in texture file.
			try:
				#image = pygame.image.load(cfg.config.get('paths').get('model_path', '') + tex_data.get('image', '')).convert()
				image = pygame.image.load(tex_data.get('image', '')).convert()
			except AttributeError:
				print(f"Unexpected error while processing graphics file {tex_data.get('image', '')} not found.")
				raise

			# Set color for transparent key
			image.set_colorkey(pygame.Color(tex_data.get('transparentcolor', '#000000')))

			# Read the picture data from texture file
			image_width = tex_data.get('imagewidth', 0)
			image_height = tex_data.get('imageheight', 0)
			tile_width = tex_data.get('tilewidth', 0)
			tile_height = tex_data.get('tileheight', 0)	

			# Initiate dicts storing texture data
			(child_ref if child_ref != None else self).texture_data = {}
			(child_ref if child_ref != None else self).texture_length = {}
			(child_ref if child_ref != None else self).texture_dynamic = {}

			# Loop to load requested textures
			for action_key, action_value in model_data.get('texture_data', {}).items():

				frames = []

				# Variable used to determine if the tile is auto-animated or static
				dynamic = False

				for frame_dict in action_value:

					frame = {}
					
					#if frame_dict.get('duration', 0) > 0: dynamic = True
					dynamic = True if frame_dict.get('duration', 0) > 0 else dynamic

					frame.update({ 'duration' : frame_dict.get('duration', 0)})

					# Prepare the tile texture - rectangle from the image
					rect = ((int(frame_dict.get('tileid', 0)) % (image_width // tile_width)) * tile_width, 
							(int(frame_dict.get('tileid', 0)) // (image_width // tile_width)) * tile_height, 
							tile_width, tile_height)
							
					# Save the tile image converted to TILE_RESOLUTION of the game (64x64)
					#frame.update({ 'tile' : pygame.transform.scale(image.subsurface(rect), cfg.config.get('display').get('tile_res', [64, 64])) })
					frame.update({ 'tile' : pygame.transform.scale(image.subsurface(rect), [64,64]) })

					# Now is the frame ready to be stored into the list
					frames.append(frame)

				# Now we can store the whole state with texture details and the metadata
				(child_ref if child_ref != None else self).texture_data.update({ action_key : frames})
				(child_ref if child_ref != None else self).texture_length.update({ action_key : len(frames)})
				(child_ref if child_ref != None else self).texture_dynamic.update({ action_key : dynamic})
	
	def __str__(self, level=0):
		
		tabs = '\t' * level

		return f'{tabs}*Instance of {self.__class__.__name__} ({hex(id(self))}) [{ctypes.c_long.from_address(id(self)).value}]:\n\
				{tabs}\tmodel_name\t\t({hex(id(self.model_name))}) [{ctypes.c_long.from_address(id(self.model_name)).value}]:\t{self.model_name}\n\
				{tabs}\tcollision_area\t\t({hex(id(self.collision_area))}) [{ctypes.c_long.from_address(id(self.collision_area)).value}]:\t{self.collision_area}\n\
				{tabs}\ttexture_offset\t\t({hex(id(self.texture_offset))}) [{ctypes.c_long.from_address(id(self.texture_offset)).value}]:\t{self.texture_offset}\n\
				{tabs}\ttexture_file\t\t({hex(id(self.texture_file))}) [{ctypes.c_long.from_address(id(self.texture_file)).value}]:\t{self.texture_file}\n\
				{tabs}\ttexture_data\t\t({hex(id(self.texture_data))}) [{ctypes.c_long.from_address(id(self.texture_data)).value}]:\t{self.texture_data}\n\
				{tabs}\ttexture_length\t\t({hex(id(self.texture_length))}) [{ctypes.c_long.from_address(id(self.texture_length)).value}]:\t{self.texture_length}\n\
				{tabs}\ttexture_dynamic\t\t({hex(id(self.texture_dynamic))}) [{ctypes.c_long.from_address(id(self.texture_dynamic)).value}]:\t{self.texture_dynamic}\n'
	
@functools.lru_cache(maxsize=32)#@Memoize
class EntityModel(TileModel):

	# List of states supported by the entity models
	states = ['default' , 'move_up', 'move_down', 'move_left', 'move_right', 'die']
	
	def __init__(self, path, json_file):
		super().__init__(path, json_file)


class CellModel(TileModel):

	# List of states supported by the cell models
	states = ['default']
	
	def __init__(self, path, json_file):
		super().__init__(path, json_file)

'''
class Assets:
	""" Class that manages efficient usage of textures by providing only 
		one instance for repetitive use.
	"""
	
	_all_tile_models = {}

	ASSETS_PATH = 'assets/'	
	TILE_RESOLUTION = 64

	@classmethod
	def get_entity_model(cls, model_type):

		if model_type not in cls._all_tile_models:
			new_model = EntityModel(Assets.ASSETS_PATH, str(model_type) + '.json')
			cls._all_tile_models.update( { model_type : new_model })
		return cls._all_tile_models.get(model_type)	

	@classmethod
	def get_cell_model(cls, model_type):

		if model_type not in cls._all_tile_models:
			new_model = CellModel(Assets.ASSETS_PATH, str(model_type) + '.json')
			cls._all_tile_models.update( { model_type : new_model })
		return cls._all_tile_models.get(model_type)	
'''
pygame.init()
window = pygame.display.set_mode([640,480])

grey_key_model = EntityModel('assets/','grey_key' + '.json')
print(EntityModel.cache_info())
print(grey_key_model)

key_model = EntityModel('assets/','key' + '.json')
print(EntityModel.cache_info())
print(key_model)

item_model = EntityModel('assets/','item' + '.json')
print(EntityModel.cache_info())
print(item_model)

grey_key_model2 = EntityModel('assets/','grey_key' + '.json')
print(EntityModel.cache_info())
print(grey_key_model2)

EntityModel.cache_clear()

red_key_model = EntityModel('assets/','red_key' + '.json')
print(EntityModel.cache_info())
print(red_key_model)

print(EntityModel.cache_info())

#print(EntityModel._cache.get(('assets/', 'key.json')))

#EntityModel.list_memo

