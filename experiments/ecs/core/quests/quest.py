import core.events.event as event # for creation of QUEST_START, QUEST_FINISH, PHASE_START, PHASE_FINISH events

from core.config.paths import QUEST_PATH

import core.scripts as scripts
import core.commands as commands
import core.engine as engine # to call _create_entity() fnc (probably in the future also to call _create_map)

import json # For loading quest from json

########################################################
### Module functions
########################################################

def load_quest(quest_id, event_queue):
	''' load quest data from the json file and calls quest constructor
	'''
	# Open the quest file	
	try:		
		with open(QUEST_PATH / str(quest_id +'.json'), 'r') as quest_file:
			json_quest_data = quest_file.read()
			quest_data = json.loads(json_quest_data)
	except FileNotFoundError:
		print(f'File {QUEST_PATH / str(quest_id + ".json")} not found.')
		raise

	# Load the quest
	q = Quest(quest_data, event_queue)

	# Return the quest
	return q


########################################################
### Quest class
########################################################

class Quest:
	''' Simple quest for testing purposes
		- should contain data for constructing/destructing the world
		- should remember mapping between entity_id and game_id in some dictionary
		- should contain event handlers
	'''
	def __init__(self, quest_data, event_queue):
		''' Load the data from quest dictionary
		'''
		# All quest data
		self.quest_data = quest_data

		# Quest details
		self.id = self.quest_data.get("id")
		self.name = self.quest_data.get("name")
		self.description = self.quest_data.get("description")
		self.objective = self.quest_data.get("objective")
		self.phase_id = self.quest_data.get("init_phase")

		# Phase data init
		self.phase_name = self.phase_objective = None
		self.maps = self.entities = self.event_handlers = None
		
		# Remember the queue for storing quest/phase events
		self.event_queue = event_queue

		# Phase data load
		self.load_phase(self.phase_id)

		# Report that quest was loaded - generate event
		self.event_queue.append(event.Event('QUEST_START', self, None, params={'quest_id' : self.id}))

		# Phase details
		#phase_data = quest_data.get("phases").get(self.phase_id)
		#self.phase_name = phase_data.get("name")
		#self.phase_objective = phase_data.get("objective")

		# Maps
		#self.maps = phase_data.get("maps", [])

		# Create maps existing in the world
		#try:
		#	for map_name in self.maps:
		#		engine.create_map(map_name)
		#except ValueError:
		#	print(f'Problem with initiation of maps for quest (id-name-phase-map): {self.id} - {self.name} - {self.phase_id} - {map_name}')
		#	raise ValueError

		# Entities
		#self.entities = phase_data.get("entities")

		# Create entities in the world
		#try:
		#	for entity in self.entities: 
		#		engine._create_entity(entity)
		#except ValueError:
		#	print(f'Problem with initiation of entities for quest (id-name-phase): {self.id} - {self.name} - {self.phase_id}')
		#	raise ValueError

		# Event handlers
		#self.event_handlers = phase_data.get("event_handling")

	def event_handler(self, event):

		#print(f'*Starting quest event processing')
		#print(event)

		# Check if there are any actions defined for the event_type and iterate through
		for event_handle in self.event_handlers.get(event.event_type, []):

			#print(f'Handler found for {event.event_type}')
			# Check that conditions are fulfilled - if no conditions are stated then False
			# If no condition then always False
			# Conditions PARAM and SCRIPT and FUNCTION must be fulfilled at the same time
			
			conditions = event_handle.get("conditions", {})
			
			#####
			# PARAMS condition
			#####

			# Expect that the result is True to start with
			cond_param_result = True

			# Evaluate condition PARAM - parameters of the event must equal parameters in the condition
			cond_param = conditions.get("params", {})
			
			# Iterate every parameter of event and compare it to parametr in param condition
			for cond_param_key, cond_param_value in cond_param.items():

				# Find the value for the key in the event.params and compare it with the value in the condition
				# This value then AND with the value cond_param_result
				cond_param_result = cond_param_result and (event.params.get(cond_param_key, None) == engine._entity_map.get(cond_param_value))

			#print(f'Cond_param_result: {cond_param_result}')

			#####
			# SCRIPT condition
			#####
			
			# Expect that the result is False to start with
			cond_script_result = False

			# Evaluate condition SCRIPT - python string must evaluate to True in order the condition to pass
			cond_script = conditions.get("script", "True")

			# Evaluate the script condition
			try:
				cond_script_result = eval(cond_script)
			except SyntaxError:
				print('Error in script condition for event {event}.')

			#print(f'Cond_script_result: {cond_script_result}')

			#####
			# FUNCTION condition
			#####

			# Expect that the result is False to start with
			cond_function_result = False

			# Evaluate condition FUNCTION - python func must evaluate to True in order the condition to pass			
			[cond_function, cond_function_params] = conditions.get("function", ["condition_always_true", {}])


			# Evaluate the function condition
			try:
				#cond_function_result = globals()[cond_function](event, **cond_function_params)
				##cond_function_result = getattr(scripts, scripts.get_script_fnc(cond_function))(event, **cond_function_params)
				cond_function_result = scripts.get_script_fnc(cond_function)(event, **cond_function_params)
			except TypeError:
				print(f'Function {scripts.get_script_fnc(cond_function)} cannot be called')
				raise

			#print(f'Cond_function_result: {cond_function_result}')

			#####
			# Execute ACTION 
			#####

			# If merged all conditions are True
			if cond_param_result and cond_script_result and cond_function_result:

				# Get the list of actions
				actions = event_handle.get("actions", {})

				# Perform one action after another
				for action in actions:

					action_function = action[0]
					action_function_params = action[1]

					try:
						#action_function_result = globals()[action_function](event, **action_function_params)
						##action_function_result = getattr(scripts, scripts.get_script_fnc(action_function))(event, **action_function_params)
						action_function_result = scripts.get_script_fnc(action_function)(event, **action_function_params)
					except TypeError:
						print(f'Function {scripts.get_script_fnc(action_function)} cannot be called')
						raise
					
		#print(f'*Finishing quest event processing')

	def load_phase(self, phase_id):
		''' Load the phase data into the quest 
		properties.
		'''

		# Load phase header
		phase_data = self.quest_data.get("phases").get(self.phase_id)
		self.phase_name = phase_data.get("name")
		self.phase_objective = phase_data.get("objective")

		#####
		# PRE-LOAD cleanup - Do the clearance pre phase load steps
		#####

		# Clean the entities that are no longer needed
		entities_to_clean = phase_data.get("cleanup", {}).get("entities", [])

		for entity_name_to_clean in entities_to_clean:
			engine.delete_entity(entity_name_to_clean)

		# Clean the maps that are no longer needed
		maps_to_clean = phase_data.get("cleanup", {}).get("maps", [])

		for map_name_to_clean in maps_to_clean:
			engine.delete_map(map_name_to_clean)

		#####
		# LOAD PHASE
		#####

		# Maps
		self.maps = phase_data.get("maps", [])

		# Create maps existing in the world
		try:
			for map_name in self.maps:
				engine.create_map(map_name)
		except ValueError:
			print(f'Problem with initiation of maps for quest (id-name-phase-map): {self.id} - {self.name} - {self.phase_id} - {map_name}')
			raise ValueError

		# Entities
		self.entities = phase_data.get("entities")

		# Create entities in the world
		try:
			for entity in self.entities: 
				engine._create_entity(entity)
		except ValueError:
			print(f'Problem with initiation of entities for quest (id-name-phase): {self.id} - {self.name} - {self.phase_id}')
			raise ValueError

		# Event handlers
		self.event_handlers = phase_data.get("event_handling")

		# Report that phase was loaded - generate event
		self.event_queue.append(event.Event('PHASE_START', self, None, params={'phase_id' : self.phase_id}))


	def set_phase(self, phase_id):
		''' Change the phase
		'''

		self.phase_id = phase_id
		self.load_phase(self.phase_id)

		print(f'Phase was set to {self.phase_id}')
		
		return 0