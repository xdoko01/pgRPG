''' pyrpg/pyrpg/constants/config.py

	Called from:
	- pyrpg/pyrpg/main.py (first import)
	- pyrpg/pyrpg/core/engine.py (import)
	- pyrpg/pyrpg/core/components/screen.py (import)
	- pyrpg/pyrpg/core/components/mapentity.py (import)
	- pyrpg/pyrpg/core/components/quest.py (import)
	- pyrpg/pyrpg/core/components/assets.py (import)
	- ... maybe more

	Aim:
	- Loading game configuration from JSON file
	- Setting up logger configuration for the game 

	Usage:
	- Any pyrpg module can access the configuration by doing the following steps:
		
		import pyrpg.constants.config as cfg ... importing this module
		cfg.config ... accessing public variable config from this module
	
	Notes:
	 - It is not necessary to have config as a class. Module with module variable returning
	 configuration dict.
	
	Examples:
	 - See pyrpg/config.json for the example

'''

import logging
import logging.config
import json

def load_config(config_file_path=None):
	''' Load default config and overwrite with config from the file, if stated.
	'''
	# Get hardcoded config values
	config = get_defaults()
	
	# Read config from config file
	try:		
		with open(config_file_path if config_file_path else config.get('config_file'), 'r') as config_file:
			json_config_data = config_file.read()
			config_data = json.loads(json_config_data)
	except FileNotFoundError:
		print(f"Config file not found.")
		raise

	# Overwrite defaults by config file
	return {**config, **config_data}

def get_defaults():
	''' Returns default game configuration - hardcoded
	'''
	return {
			'config_file' : 'config.json',
			'paths' :  {
				'model_path' : 'pyrpg/resources/models/',
				'map_path' :  'pyrpg/resources/maps/',
				'quest_path' :  'pyrpg/resources/quests/',
				'font_path' :  'pyrpg/resources/fonts/',
				'image_path' : 'pyrpg/resources/images/',
				'script_path' : 'pyrpg/resources/scripts/'			
				},
			'logging' : {
				},
			'display' : {
				'resolution' : [640, 480],
				'fullscreen' : False,
				'fps' : 30,
				'show_fps' : True,
				'collision_map' : False,
				'raycasting' : False,
				'window_title': 'PyRPG',
				'font_file' : 'my_courier.ttf',
				'font_size' : 16
				},
			'sound' : {
				'sound_volume': 0,
				'music_volume' : 0		
				},
			'game' : {
				'starting_quest': 'main_quest.json'
				},
			'console' : {
				'global' : {
					'cli_module' : None,	
					'bck_alpha' : 150,
					},
				'input' : {
					'font_file' : 'pyrpg/resources/fonts/JackInput.ttf',
					'bck_alpha' : 0
					},
				'output' : {
					'font_file' : 'pyrpg/resources/fonts/JackInput.ttf',
					'bck_alpha' : 0,
					'display_lines' : 20,
					'display_columns' : 100
					}
				}
			}

# Load and store configuration in this public variable.
# Python makes sure that although this module is used in
# several imports the actual import happens only once and
# hence prevents repetitive loads of the same config.
config = load_config()

# Initiate logger - configuration stored in config.logging dict
logging.config.dictConfig(config.get("logging"))

# Create logger for config.py module
logger = logging.getLogger(__name__)

# Log successful config load
logger.info('Game logger successfully configured.')
logger.info('Game config.py module successfully loaded/imported.')