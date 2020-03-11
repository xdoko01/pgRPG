''' pyrpg/pyrpg/core/engine.py - called from pyrpg/pyrpg/main.py 

	Implementation of the main game - Engine.

	Aim:
	-> Initiates all main game variables as Engine module globals (init_globals())
	-> Implements tha main game loop (run())

	Usage:
	-> Run the pyrpg game
	
	Notes:
	
	Examples:

'''

# Create local logger
import logging
logger = logging.getLogger(__name__)

import pygame # necessary for window init, clock and font
import pygame.freetype # necessary to work with font
from pygame.locals import * # necessary to work with font

# load and store config dict as cfg.config
# here necessary for loading COnsole params, fonts and game window conf
import pyrpg.constants.config as cfg 

# import pyrpg.core.components.map  # necessary for calling Map constructor


################################################################
################################################################
# Define Engine module variables - accessible from other modules
################################################################
################################################################

# Definition of game states
GAME_MODES = ['TITLE','LOCAL_MAP_MODE','WORLD_MAP_MODE', 'MENU_MODE', 'INVENTORY_MODE', 'SHOP_MODE']
game_mode = None

# Initiate dictionaries holding references to  game objects
screens, quests, maps, entities = {}, {}, {}, {}

# Initiate pygame entities
window = None
clock = None
font = None

# Initiate reference to debug console
console = None

exit = None

################################################################
################################################################
# Define Engine module methods - accessible from other modules
################################################################
################################################################

def init_globals():
	''' Initiate main game list and dictionaries
	'''
	
	# Without these statements below would be considered local vars
	global screens, quests, maps, entities
	global game_mode, exit

	# Initiate dictionaries holding references to ey game objects
	screens = {}
	quests = {}
	maps = {}
	entities = {}

	# No game mode selected
	game_mode = None

	exit = False

	################################################################
	# Init PyGame
	################################################################

	# Without these statements below would be considered local vars
	global window, clock, font

	# Supported from 1.9.5 pygame
	if not pygame.get_init(): pygame.init()

	pygame.display.set_caption(cfg.config.get('display').get('window_title'))
	window = pygame.display.set_mode(cfg.config.get('display').get('resolution'))
	font = pygame.freetype.Font(cfg.config.get('paths').get('font_path') + cfg.config.get('display').get('font_file'), cfg.config.get('display').get('font_size'))
	clock = pygame.time.Clock()

	logger.info('Pygame initiated')


	################################################################
	# Init Console
	################################################################

	# Without this statement below would be considered local var
	global console

	# Create console only in case it is defined in the config
	if cfg.config.get('console', False):

		import importlib # for passing module name to COnsole as a string from config file
		import pyrpg.core.components.console # necessary to implement Console

		console = pyrpg.core.components.console.Console(
					importlib.import_module(cfg.config.get('console').get('global').get('cli_module', 'pyrpg.core.engine')),
					window.get_width(),
					cfg.config.get('console')
				)

		logger.info('Console initiated')

def load_game(quest_id=None):
	''' Load the init quest and run the main loop. FIle with the quest 
	must be named quest_id.json.
	Must be called after init() - to initialize quests dictionary
	'''

	# Without this statement it would not be possible to assign to global var
	global game_mode 

	import pyrpg.core.components.quest # necessary for calling QUest constructor

	# Load defined quest or default quest from config, if missing
	pyrpg.core.components.quest.load_quest(quest_id if quest_id else cfg.config.get('game').get('starting_quest'))
	
	# Jump directly into the game
	game_mode = 'LOCAL_MAP_MODE'

	# Log successful Game load
	logger.info(f'Game loaded')

def run():
	''' Implementaion of the main loop. Dependend on the game mode
	and console shown/not shown.
	'''

	while not exit:
		
		# Clear the window
		window.fill((0, 0, 0))

		# Process the keys pressed
		events = pygame.event.get()

		# Process the generic actions bound to key pressed - such as exiting the game, toggling console, changing the game mode etc.
		update_generic_actions(events)

		# Based on game mode, call the convenient function
		if not console.enabled:
			if game_mode == 'LOCAL_MAP_MODE': update_local_map(events)

		# Process the console events
		console.update(events)

		# Display the console
		console.show(window)
		
		# Refresh the display
		pygame.display.update()
		
		# Keep FPS on 30
		clock.tick(30)

	exit_game()

def exit_game():
	''' Exit game
	'''
	pygame.quit()

def update_generic_actions(events):
	''' Function to process generic actions not dependent on game_mode.
	Typically exiting the game or toggling console
	Events contain key pressedd list.
	'''

	# Without this statement it would not be possible to assign to global var
	global exit

	# Process the keys
	for event in events:
		
		# Exit on closing of the window
		if event.type == pygame.QUIT: exit = True
		elif event.type == pygame.KEYDOWN:
			# ESC pressed
			if event.key == pygame.K_ESCAPE: exit = True						
			# Toggle console on/off the console	
		elif event.type == pygame.KEYUP:									
			if event.key == pygame.K_F1: 						
				# Toggle the console - if on then off if off then on
				console.toggle()

def update_local_map(events):
	''' Main game loop for the game action happening on the map.
	Events contain key pressedd list.
	'''

	# CALL THE ScriptProcessor if processor has some commands to perform, he will perform and block user input.
	# if no commands in pipe then normal operation will happen

	# if ScriptProcessor is in operation, check if dialog is displayed and/or waiting for answer/space pressed.

	# Iterate all maps from list of maps and on every entity call update method. For Players, update method
	# contains also reading of keys and processing it (see original game).
	pass

def game_info():
	''' Return information about the whole game world
	'''

	out = '*** Game Info - START ***\n'

	out += 'Quests\n'
	out += '------\n'		
	for key, quest in quests.items():
		out += f'\t{key}\n'
		out += '\t- - - -\n'		
		out += f'\t\t{str(quest)}\n'

	out += 'Screens\n'
	out += '-------\n'		
	for key, screen in screens.items():
		out += f'\t{key}\n'
		out += '\t- - - -\n'
		out += f'\t\t{str(screen)}\n'

	out += 'Maps\n'
	out += '----\n'	
	for key, map in maps.items():
		out += f'\t{key}\n'
		out += '\t- - - -\n'
		out += f'\t\t{str(map)}\n'

	out += 'Entities\n'
	out += '--------\n'	
	for key, entity in entities.items():
		out += f'\t{key}\n'
		out += '\t- - - -\n'		
		out += f'\t\t{str(entity)}\n'

	out += '*** Game Info - END ***\n'

	return out


################################################################
################################################################
# Define Console functions - data to be returned in console
################################################################
################################################################

def cons_get_info_header():
	''' Return dynamic information to be displayed in console header
	'''
	return 'Mode: ' + str(game_mode)

def cons_get_info_footer():
	''' Return dynamic information to be displayed in console footer
	'''
	return 'FPS: ' + str(clock.get_fps())

################################################################
################################################################
# XXX
################################################################
################################################################

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

################################################################
################################################################
# Define Event functions
################################################################
################################################################

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
