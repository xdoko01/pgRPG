''' pyrpg/core/components/screen.py

	Implementation of Screen class and connected methods. Screen
	can be created/destroyed during the game based on definition
	present in quest json file.
	
'''

import logging

import math # Necessary to calculate ceiling for offset of cells
import pygame # Necessary to use Surface class

# load and store config dict as cfg.config
# here necessary for loading tile resolution
import pyrpg.constants.config as cfg 

# Neccessary for accessing engine variables - screens
import pyrpg.core.engine as engine

# Create logger for local module
logger = logging.getLogger(__name__)

def load_screen(screen_dict):
	''' Called from Quest - prepares the screen based on parameters
	in the screen_dict dictionary. Dictionary is loaded from the 
	file containing configuration of the quest.
	'''
	
	# Assert that map is not yet registered/created
	assert (screen_dict.get('id') not in engine.screens)
	
	if screen_dict.get('type') == 'MapScreen2D':
		new_screen = MapScreen2D(screen_dict)
	else:
		new_screen = Screen(screen_dict)
	
	engine.screens.update( {screen_dict.get('id') : new_screen} )

class Screen(pygame.Surface):
	''' Basic class for game screen as a child of Surface class. Game can have
	several Screens displayed. For example one for game map orientation, one
	as main game Screen with player, and one with game statistics. It is also
	possible to have 2 main game Screens displayed, first for one player and
	second for second player.
	'''
	
	''' obsolete
	def create_screen(cls, screen_id):
		# Open json file with definition of the Screen
		try:
			# Read the model definition from model.json
			with open(screen_id + '.json', 'r') as scr_file:
				json_scr_data = scr_file.read()
		except FileNotFoundError:
			print(f"File {screen_id + '.json'} not found.")

		scr_data = json.loads(json_scr_data)

		scr_type = scr_data.get('type', 'Screen')

		if scr_type == 'MapScreen2D':
			new_screen = MapScreen2D(scr_data)
		else:
			new_screen = Screen(scr_data)

		return new_screen
	'''

	def __init__(self, params_dict):
		''' Screen instance Constructor, using Surface constructor and adding
		position, dimensions and id of the Screen in the game window.
		'''

		self.id = params_dict.get('id', '')
		self.dim = params_dict.get('dim', [0, 0])
		self.pos = params_dict.get('pos', [0, 0])

		# Screen ID must not be empty string
		assert(self.id != '')

		# Call init of pygame.Surface class
		super().__init__(self.dim)


class MapScreen(Screen):
	''' MapScreen displays game situation of the player or other character
	entity on the map. There are other classes for other information that
	we might want to display in a form of the screen.
	'''

	def __init__(self, params_dict):
		''' MapScreen instance constructor, using Screen constructor and adding
		information whether to display textures or just wireframe.
		'''
		
		# Call init of Screen class
		super().__init__(params_dict)

		self.textures = params_dict.get('textures', True) 

		# Assign entity to the screen - can be None		
		self.entity = params_dict.get('entity', None)

	def register_entity(self, entity):
		''' Decide what entity (character/player) should be displayed on the
		map screen - it can be item/player/character/teleport/whatever that
		is inherited from Entity class.
		'''
		self.entity = entity

	def draw(self):
		''' Draw the MapScreen. Currently, solid constant fill.
		'''

		self.fill((50,50,50))

	def clear_resources(self):
		''' When destroying screen, we need to put away reference to 
		the entity.
		'''
		self.entity = None


class MapScreen2D(MapScreen):
	''' MapScreen2D displays game situation of the player or other character
	entity on the map in 2D graphics. There might be other classes for other 
	forms of graphic - isomorphic / 3D
	'''

	def __init__(self, params_dict):
		''' MapScreen2D instance constructor, using MapScreen constructor 
		and adding information for 2D representation.
		'''
		
		# Call MapScreen consturctor
		super().__init__(params_dict)

		# Where to display the assigned entity - in the centre
		self._entity_pos = [self.get_width() / 2, self.get_height() / 2]

		# What is the resolution of the cell
		self._tile_res = cfg.config.get('display').get('tile_res')

		# How many cells fit onto the screen
		self._min_offset_x = -1 * math.ceil(self.get_width() / self._tile_res[0] / 2)
		self._max_offset_x = math.ceil(self.get_width() / self._tile_res[0]  / 2) + 1
		self._min_offset_y = -1 * math.ceil(self.get_height() / self._tile_res[1]  / 2)
		self._max_offset_y = math.ceil(self.get_height() / self._tile_res[1]  / 2) + 1

	def draw(self):
		''' Draw the screen on the game window
		'''
		
		# Draw the basic background
		super().draw()

		# Draw the map
		'''
		if self.textures: 
			self.entity.map.draw(self, '2D_TEXTURES') 
		else: 
			self.entity.map.draw(self, '2D_PLAIN')
		'''

		# Draw map entities - items, characters, players
		'''
		for entity_id, entity_instance in self.entity.map.entities.items():

			# Draw only those that can be displayed
			pass
		'''
logger.info('Game screen.py module successfully loaded/imported.')