''' pyrpg/pyrpg/core/components/quest.py - called from pyrpg/pyrpg/core/engine.py 

	Implementation of Quest class. Quest initiates all game objects 
	including screens and contains the game logic.

	Quest is defined as a json file. Example structure can be seen below.

		{
			"id" : "q00",
			"name" : "Welcome to Paradise",
			"description" : "",
			"objective" : "",
			"init_phase" : "q00_p01",

			"phases" : {			
				
				"q00_p01" :{

					"name" : "Here we go",
					"objective" : "",

					"prerequisities" : {

						"cleanup" : {
							"maps" : [],
							"screens" :[],
							"entities" : []
						},

						"create" : {
							"maps" : ["map01"],
							"screens" :["player_screen_1"],
						}

					},

					"entities" : {

						"items" : [],

						"characters" : [],

						"players" : [
							{
								"name" : "Player01",
								"id" : "q00_p01_p01",
								"type" : "dark_male",	

								"map" : "map01",
								"screen" : "player_screen_1",
								"pos" : [5.5, 5.5],

								"inventory" : {},

								"control_keys" : {
									"key_move_left" : "97",
									"key_move_right": "100",
									"key_move_up"   : "119",
									"key_move_down" : "115",
									"key_attack"    : "113"
								}
							}
						]
					},

					"event_handling" : {},

					"is_completed" : [],

					"postrequisities" : {

						"cleanup" : {
							"maps" : [],
							"screens" :[],
							"players" : [],
							"entities" : []
						},

						"create" : {
							"maps" : [],
							"screens" :[],
							"players" : [],
						}

					}
				}
			}
		}	

'''

import json # Parsing of quest json definition

# Neccessary for accessing engine variables - maps, screens, quests
# Necessary for calling engine module methods - get_all_entities, ...
import pyrpg.core.engine as engine

# Necessary for calling load_map method - TODO - dont I want engine to do that loading?
import pyrpg.core.components.map as map

# Necessary for calling load_screen method - TODO - dont I want engine to do that loading?
import pyrpg.core.components.screen as screen

# Necessary for calling Player constructor - TODO - dont I want engine to do that loading?
import pyrpg.core.components.mapentity as mapentity

# load and store config dict as cfg.config
# here necessary for loading quest path
import pyrpg.constants.config as cfg 

from pyrpg.core.components.events import EventHandler # EventHandler implementation

def load_quest(quest_id):
	''' Checks if quest is already loaded and register it at Engine instance.
	Quest handles creation of all vital classes such as maps and entities.
	'''

	# Assert that quest is not yet part of the game
	assert (quest_id not in engine.quests)

	# Most of the work is done here
	new_quest = Quest(cfg.config.get('paths').get('quest_path') + quest_id + '.json')

	# Store the quest in the list of active quests
	engine.quests.update( {quest_id : new_quest} )


class Quest(EventHandler):
	''' Main Quest class TBD ...
	'''

	def __init__(self, quest_json):

		# Read the quest file
		try:
			with open(quest_json, 'r') as quest_file:
				json_quest_data = quest_file.read()
		except FileNotFoundError:
			print(f"File {quest_id + '.json'} not found.")
			raise

		quest_data = json.loads(json_quest_data)

		# Parse the file for general quest information
		self.id = quest_data.get('id', "")
		self.name = quest_data.get('name', "")
		self.description = quest_data.get('description', "")
		self.objective = quest_data.get('objective', "")
		self.phase_id = quest_data.get('init_phase', "")
		self.phases_definition = quest_data.get("phases", {})
		self.phase_name = ""
		self.phase_objective = ""
		self.phase_definition = {}

		# Load the initial phase of the quest
		self.load_phase(self.phase_id)

	def load_phase(self, phase_id):

		# Find the relevant data for the phase_id in self.phases_definition
		assert(phase_id in self.phases_definition)
		self.phase_definition = self.phases_definition.get(phase_id)

		# Load phase properties
		self.phase_name = self.phase_definition.get("name", "")
		self.phase_objective = self.phase_definition.get("objective", "")

		# Process the prerequisities - cleanup ###
		##########################################
		
		# Cleanup entities - must be done first to unregister entities at maps and screens
		'''  I dont know why to do it like that. If I want to clean some MapEntity, I need to 
		find it on maps level and get rid of it - that would mean to have some function that would
		return entity instance based on ID - iterate all maps and find it. All maps are stored on
		Engine level only at the moment, so I need to iterate those dictionaries.'''
		
		# Get dictionary of all entities currently loaded in the game
		_all_entities = engine.get_all_entities()

		# Iterate the cleanup prereq. for entities and remove them from the game totally
		for entity_id in self.phase_definition.get('prerequisities', {}).get('cleanup', {}).get('entities', []):

			# Raise error if Quest is trying to remove not existing entity
			assert(entity_id in _all_entities)
			
			# Unregister reference to model
			_all_entities.get(entity_id).clear_resources()

		# Cleanup maps - unregister map means also unregistering all entities on the map 
		# (but they still may be pointed at on quest level).

		# Get dictionary of all maps currently loaded in the game
		_all_maps = engine.get_all_maps()

		# Iterate the cleanup prereq. for maps and remove them from the game totally
		for map_id in self.phase_definition.get('prerequisities', {}).get('cleanup', {}).get('maps', []):
			
			# Raise error if Quest is trying to remove not existing map
			assert(map_id in _all_maps)

			# Cleanup all entities on the map - every entity gets rid of model and 
			# is put away from list of entities
			_all_maps.get(map_id).clear_resources()

			# Remove from Engine maps
			del Quest.engine.maps[map_id]

		# Get dictionary of all screens currently loaded in the game
		_all_screens = engine.get_all_screens()

		# Iterate the cleanup prereq. for maps and remove them from the game totally
		for screen_id in self.phase_definition.get('prerequisities', {}).get('cleanup', {}).get('screens', []):

			# Raise error if Quest is trying to remove not existing screen
			assert(screen_id in _all_screens)

			# Cleanup all screens in the game 
			_all_screens.get(screen_id).clear_resources()

			# Remove from Engine screens dict
			del Quest.engine.screens[screen_id]

		# Process the prerequisities - create ###
		##########################################
		
		# Create maps
		for map_id in self.phase_definition.get('prerequisities', {}).get('create', {}).get('maps', []):
			map.load_map(map_id)

		# Create screens
		for screen_dict in self.phase_definition.get('prerequisities', {}).get('create', {}).get('screens', []):
			screen.load_screen(screen_dict)

		# Main part - Create the Entities      ###
		##########################################

		# Create and fill the Items entities requested by the Quest
		for item in self.phase_definition.get('entities', {}).get('items', []):
			# Create empty item type - that contains all graphical data already
			new_item = Item(item.get('type'))
			# Fill Item with instance specific data
			new_item.setup(item)
			# Add Item to the list of quest entities
			assert(new_item.id not in entities)
			self.entities.update({new_item.id : new_item})
			# Register new Item at the map if necessary
			new_item.register_map()
			# Register new Item at the screen if necessary
			new_item.register_screen(item.get('screen',''))

		# Create and fill the Character entities requested by the Quest		
		for character in self.phase_definition.get('entities', {}).get('characters', []):
			# Create empty character type - that contains all graphical data already
			new_character = Character(character.get('type'))
			# Fill Character with instance specific data
			# Should SETUP fill also ivnentory? I think that yes - from the dictionary info sent to setup
			new_character.setup(character)
			# Add Character to the list of quest entities
			assert(new_character.id not in entities)
			self.entities.update({new_character.id : new_character})
			# Register new Character at the map if necessary
			new_character.register_map()
			# Register new Character at the screen if necessary
			new_character.register_screen(character.get('screen',''))

		# Create and fill the Player entities requested by the Quest		
		for player in self.phase_definition.get('entities', {}).get('players', []):
			# Create empty player type - that contains all graphical data already
			new_player = mapentity.Player(player.get('type'))
			# Fill Player with instance specific data
			new_player.setup(player)
			# Add Character to the list of quest entities
			assert(new_player.id not in engine.entities)
			engine.entities.update({new_player.id : new_player})
			# Add quest.id to the list of player's quests
			new_player.quests.append(self.id)
			# Register new player at the map if necessary
			new_player.register_map()
			# Register new Player at the screen if necessary
			new_player.register_screen(player.get('screen',''))


		# Store conditions for event handling into the quest dict structure - skipping for now
		pass


	def event_handler(self, event):
		""" Quest is an event handler. Event is delivered by 
		Event dispather who is class Engine.
		"""

		# Work with Quest inventory of events stored on quest level
		pass

		# You should be able to call ScriptProcessor.add_command from here (Quest)
		# This will start the cutscene or can initiate showing dialogs or adding items to inventory ...



