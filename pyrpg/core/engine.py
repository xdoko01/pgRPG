''' pyrpg/pyrpg/core/engine.py - called from pyrpg/pyrpg/main.py 

	Implementation of the main game class - Engine.

'''

import logging
import importlib # for passing module name to CLI as a string from config file

import pygame # necessary for window init, clock and font
import pygame.freetype # necessary to work with font
from pygame.locals import * # necessary to work with font

# load and store config dict as cfg.config
# here necessary for loading CLI, fonts and game window conf
import pyrpg.constants.config as cfg 

import pyrpg.core.components.cli # necessary to implement command line interface

# import pyrpg.core.components.map  # necessary for calling Map constructor

# Create local logger
logger = logging.getLogger(__name__)

################################################################
# Define Engine module variables - accessible from other modules
################################################################

# Definition of game states
game_modes = ['TITLE','LOCAL_MAP_MODE','WORLD_MAP_MODE', 'MENU_MODE', 'INVENTORY_MODE', 'SHOP_MODE']
game_mode = None

# Initiate dictionaries holding references to ey game objects
screens = {}
quests = {}
maps = {}
entities = {}

# Initiate pygame entities
window = None
clock = None
font = None

# Initiate reference to debug CLI
cli = None

# Console toggle
console_enabled = False

################################################################
# Define Engine module methods - accessible from other modules
################################################################

def init_globals():
	''' Initiate main game list and dictionaries
	'''
	
	# Without these statements below would be considered local vars
	global screens, quests, maps, entities
	global game_mode
	global window, clock, font
	global cli 

	# Initiate dictionaries holding references to ey game objects
	screens = {}
	quests = {}
	maps = {}
	entities = {}

	# No game mode selected
	game_mode = None

	# Initiate command line in order to control the game from python console (if enabled)
	# TODO - For console, we would need to create console instance (Screen that has link to cli???)
	if cfg.config.get('game').get('cli_enabled', False):
		cli = pyrpg.core.components.cli.CommandLine(importlib.import_module(cfg.config.get('game').get('cli_module', 'pyrpg.core.engine')))
		logger.info('CLI initiated.')

	# Init pygame, clock, font and prepare game window
	pygame.init()
	pygame.display.set_caption(cfg.config.get('display').get('window_title'))

	window = pygame.display.set_mode(cfg.config.get('display').get('resolution'))
	clock = pygame.time.Clock()
	font = pygame.freetype.Font(cfg.config.get('paths').get('font_path') + cfg.config.get('display').get('font_file'), cfg.config.get('display').get('font_size'))


def load_game(quest_id=None):
	''' Load the init quest and run the main loop. FIle with the quest 
	must be named quest_id.json.
	Must be called after init() - to initialize quests dictionary
	'''
	# Without this statement it would not be possible to assign to global var
	global game_mode 

	import pyrpg.core.components.quest # necessary for calling QUest constructor

	# Load defined quest or default quest from config, if missing - reference to engine class is passed as an argument
	# in order to access config and add quest, map, to Engine dictionaries
	pyrpg.core.components.quest.load_quest(quest_id if quest_id else cfg.config.get('game').get('starting_quest'))
	
	# Jump directly into the game
	game_mode = 'LOCAL_MAP_MODE'

	# Enter the main game loop
	# run()

def get_all_entities():
	'''Extract all loaded game entities in a form of list from
	maps dictionary.
	
	Called from Quest.load_phase - clearing entities 
	'''

	# start with empty dictionary
	_all_entities = {}

	# Merge all entity dictionaries together
	for map_id, map_ref in maps.items():
		{**_all_entities, **map_ref.entities}
	
	# Return one big dictionary with key.value pair entity_id : entity_ref
	return _all_entities
	
def get_all_maps():
	'''Extract all loaded game maps in a form of list from
	maps dictionary.
	
	Called from Quest.load_phase - clearing maps 
	'''
	return maps
	
def get_all_screens():
	'''Extract all loaded game screens in a form of list from
	screens dictionary.
	
	Called from Quest.load_phase - clearing maps 
	'''
	return screens

def send_event(event):
	''' Engine is EventDispatcher implementation. This function sends
	event to every registered Quest instance in Engine.quests dictionary
	by invoking event_handler method on the quest.
	'''

	# TODO - here we can inspect event object and decide to which event handler
	# to send it to (to all/some quests, to all/some maps, to all/some screens)

	# Send the event to all quests 
	for q_key, q_value in quests.items():
		q_value.event_handler(event)

def run():
	''' Implementaion of the main loop. Dependend on the game mode
	and console shown/not shown.
	'''

	# If console is displayed, take and process input from it
	if console_enabled: update_console()

	if game_mode == 'LOCAL_MAP_MODE': update_local_map()
	

def update_local_map():
	''' Main game loop for the game action happening on the map.
	'''

	# CALL THE ScriptProcessor if processor has some commands to perform, he will perform and block user input.
	# if no commands in pipe then normal operation will happen

	# if ScriptProcessor is in operation, check if dialog is displayed and/or waiting for answer/space pressed.

	# Iterate all maps from list of maps and on every entity call update method. For Players, update method
	# contains also reading of keys and processing it (see original game).
	while True:
		pass


"""
class Engine:
	''' Master class encapsulating the whole game. Handles functions such as
	initiating the game window, initiating the game and info screens, loading
	game levels and executing the main game loop.
	'''

	# Definition of game states
	game_modes = ['TITLE','LOCAL_MAP_MODE','WORLD_MAP_MODE', 'MENU_MODE', 'INVENTORY_MODE', 'SHOP_MODE']

	def __init__(self):
		''' Initiate pygame window, clock and cli interface.
		'''

		# Share Engine reference to other classes - this needs to be done in order to be able to 
		# call EventHandler - Engine.send_event. Only one engine allowed
		assert (pyrpg.core.components.quest.Quest.engine == None)
		pyrpg.core.components.quest.Quest.engine = self
		
		assert (pyrpg.core.components.map.Map.engine == None)
		pyrpg.core.components.map.Map.engine = self

		assert (pyrpg.core.components.screen.Screen.engine == None)
		pyrpg.core.components.screen.Screen.engine = self

		assert (pyrpg.core.components.mapentity.MapEntity.engine == None)
		pyrpg.core.components.mapentity.MapEntity.engine = self

		# Initiate command line in order to control the game from python console (if enabled)
		if cfg.config.get('game').get('cli'):
			self.cli = pyrpg.core.components.cli.CommandLine(self)

		# Initiate dictionaries holding references to ey game objects
		self.screens = {}
		self.quests = {}
		self.maps = {}

		# No game mode selected
		self.game_mode = None

		# Init pygame, clock, font and prepare game window
		pygame.init()
		pygame.display.set_caption(cfg.config.get('display').get('window_title'))
		self.window = pygame.display.set_mode(cfg.config.get('display').get('resolution'))
		self.clock = pygame.time.Clock()
		self.font = pygame.freetype.Font(cfg.config.get('paths').get('font_path') + cfg.config.get('display').get('font_file'), cfg.config.get('display').get('font_size'))

	def load_game(self, quest_id=None):
		''' Load the init quest and run the main loop. FIle with the quest 
		must be named quest_id.json
		'''

		# Load defined quest or default quest from config, if missing - reference to engine class is passed as an argument
		# in order to access config and add quest, map, to Engine dictionaries
		pyrpg.core.components.quest.load_quest(quest_id if quest_id else cfg.config.get('game').get('starting_quest'))
		
		# Jump directly into the game
		self.game_mode = 'LOCAL_MAP_MODE'

		# Enter the main game loop
		self.run()

	def get_all_entities(self):
		'''Extract all loaded game entities in a form of list from
		maps dictionary.
		
		Called from Quest.load_phase - clearing entities 
		'''

		# start with empty dictionary
		_all_entities = {}

		# Merge all entity dictionaries together
		for map_id, map_ref in self.maps.items():
			{**_all_entities, **map_ref.entities}
		
		# Return one big dictionary with key.value pair entity_id : entity_ref
		return _all_entities
	
	def get_all_maps(self):
		'''Extract all loaded game maps in a form of list from
		maps dictionary.
		
		Called from Quest.load_phase - clearing maps 
		'''
		return self.maps
	
	def get_all_screens(self):
		'''Extract all loaded game screens in a form of list from
		screens dictionary.
		
		Called from Quest.load_phase - clearing maps 
		'''
		return self.screens
	

	''' moved to Quest.load_quest
	def load_quest(cls, quest_id):
		# Initiate the quest. Quest handles creation of all vital classes 
		# such as maps and entities.
		

		# Assert that quest is not yet part of the game
		assert (quest_id not in cls.quests)

		# Most of the work is done here
		new_quest = pyrpg.core.components.quest.Quest(cls.config.get('paths').get('quest_path') + quest_id + '.json')

		# Store the quest in the list of active quests
		cls.quests.update( {quest_id : new_quest} )
	'''

	''' Move this to MAP class
	def load_map(cls, map_id):
		# Called from Quest class. Loads map instance and save it
		#to the list of maps stored on ngine level.
		#

		# Assert that map is not yet registered/created
		assert (map_id not in cls.maps)

		# Most of the work is done here
		new_map = pyrpg.core.components.map.Map()
		
		# Store the map in list of the active maps
		cls.maps.update( {map_id : new_map} )
	'''

	# move this to map class
	#def unload_map(cls, map_id):
	#	''' Called from Quest during clearing of phase '''
	#
	#	# I assume that we are unloading existing map
	#	assert(map_id in maps)
	#	
	#	# Clear all pointers to entities assigned on map
	#	cls.maps.get(map_id).clear_resources()
	#	
	#	# Delete the map from dict of maps
	#	del cls.maps[map_id]

	# move this to screen class
	def load_screen(cls, screen_id):
		''' Read screen setup from json and add it to the list of screens '''

		assert(screen_id not in cls.screens)		
		new_screen = Screen.create_screen(screen_id)
		cls.screens.update( {screen_id : new_screen} )

	# move this to screen class
	def unload_screen(cls, screen_id):
		''' Remove screen from the list of screen. Called by Quest Cleanup '''
		
		# I assume that we are unloading existing screen
		assert(screen_id in screens)
		
		# Clear all pointers to entities assigned on screen		
		cls.screens.get(screen_id).clear_resources()

		# Delete the screen from dict of screens
		del cls.screens[screen_id]


	def send_event(cls, event):
		''' Engine is EventDispatcher implementation. This function sends
		event to every registered Quest instance in Engine.quests dictionary
		by invoking event_handler method on the quest.
		'''

		# TODO - here we can inspect event object and decide to which event handler
		# to send it to (to all/some quests, to all/some maps, to all/some screens)

		# Send the event to all quests 
		for q_key, q_value in quests.items():
			q_value.event_handler(event)

	def run(cls):
		''' Implementaion of the main loop. Dependend on the game mode
		'''
		if game_mode == 'LOCAL_MAP_MODE': cls.update_local_map()
	
	def update_local_map(cls):
		''' Main game loop for the game action happening on the map.
		'''

		# CALL THE ScriptProcessor if processor has some commands to perform, he will perform and block user input.
		# if no commands in pipe then normal operation will happen

		# if ScriptProcessor is in operation, check if dialog is displayed and/or waiting for answer/space pressed.

		# Iterate all maps from list of maps and on every entity call update method. For Players, update method
		# contains also reading of keys and processing it (see original game).
"""

# Log successful engine load
logger.info('Game engine.py module successfully loaded/imported.')
