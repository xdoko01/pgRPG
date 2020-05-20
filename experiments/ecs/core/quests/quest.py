
import core.config.config as config  # For load_quest QUEST_PATH_PATH
import core.scripts.script as script
import core.commands.commands as commands
import core.engine as engine # to call _create_entity() fnc (probably in the future also to call _create_map)

import json # For loading quest from json

########################################################
### Module functions
########################################################

def load_quest(quest_id):
	''' load quest data from the json file and calls quest constructor
	'''
	# Open the quest file	
	try:		
		with open(config.QUEST_PATH + quest_id +'.json', 'r') as quest_file:
			json_quest_data = quest_file.read()
			quest_data = json.loads(json_quest_data)
	except FileNotFoundError:
		print(f'File {QUEST_PATH + quest_id + ".json"} not found.')
		raise

	# Load the quest
	q = Quest(quest_data)

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
	def __init__(self, quest_data={}):
		''' Load the data from dictionary
		'''

		# Quest details
		self.id = quest_data.get("id")
		self.name = quest_data.get("name")
		self.description = quest_data.get("description")
		self.objective = quest_data.get("objective")		
		self.phase_id = quest_data.get("init_phase")		

		# Phase details
		phase_data = quest_data.get("phases").get(self.phase_id)
		self.phase_name = phase_data.get("name")
		self.phase_objective = phase_data.get("objective")

		# Entities
		self.entities = phase_data.get("entities")

		# Create entities in the world
		try:
			for entity in self.entities: engine._create_entity(entity)
		except ValueError:
			print(f'Problem with initiation of entities for quest (id-name-phase): {self.id} - {self.name} - {self.phase_id}')
			raise ValueError

		# Event handlers
		self.event_handlers = phase_data.get("event_handling")

		''' original code
		self.entities = [
			{
				"id" : "player01",
				"templates" : ["player"],
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "player01", "name" : "First Player"}},
					{"type" : "Position", "params" : {"x" : 200, "y" : 200, "map" : "map01"}},
					#{"type" : "Motion", "params" : {"dx" : 0, "dy" : 0}},
					{"type" : "Controllable", "params" :  {
						"control_keys" : {}, 
						"control_cmds" : {"up": "move", "down": "move", "left": "move", "right": "move"}
						}
					},
					#{"type" : "Renderable", "params" : {"image" : "player.png"}},
					#{"type" : "Teleportable", "params" : {}},
					#{"type" : "Collidable", "params" : {"x" : 32, "y" : 32}},
					{"type" : "Camera", "params" : {"screen_pos_x" : 0, "screen_pos_y" : 0, "screen_width" : 300, "screen_height" : 300}},
					#{"type" : "HasInventory", "params" : {}},
					#{"type" : "Brain", "params" : {"commands" : []}},
					#{"type" : "CanTalk", "params" : {}},
					{"type" : "Debug", "params" : {}}
				]
			},
			{
				"id" : "item01",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "item01", "name" : "Static Item"}},
					{"type" : "Position", "params" : {"x" : 300, "y" : 300, "map" : "map01"}},
					{"type" : "Motion", "params" : {"dx" : 0, "dy" : 0}},
					{"type" : "Renderable", "params" : {"image" : "item.png"}},
					{"type" : "Collidable", "params" : {"x" : 32, "y" : 32}},
					{"type" : "Camera", "params" : {"screen_pos_x" : 0, "screen_pos_y" : 310, "screen_width" : 300, "screen_height" :300}},
					{"type" : "Pickable", "params" : {}},
				]
			},
			{
				"id" : "camera01",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "camera", "name" : "Dynamic Camera"}},
					{"type" : "Position", "params" : {"x" : 400, "y" : 300, "map" : "map01"}},
					{"type" : "Motion", "params" : {"dx" : 0, "dy" : 0}},
					{"type" : "Controllable", "params" :  {
						"control_keys" : {'up' : 119, 'down' : 115, 'left' : 97, 'right' : 100}, 
						"control_cmds" : {"up": "none", "down": "move", "left": "move", "right": "move"}
						}
					},
					{"type" : "Camera", "params" : {"screen_pos_x" : 310, "screen_pos_y" : 0, "screen_width" : 300, "screen_height" :300}},
					{"type" : "CanTalk", "params" : {}},
					{"type" : "Debug", "params" : {}},
					{"type" : "Brain", "params" : {"commands" : [
						# IF-EXCEPTION-GOTO, CMD-FNC, CMD-PARAM
						### Move Left
						(None, 	"move", {"dx" : -120}), #0
						(0, 	"loop", {"iterations" : 1}), #1
						### Move Up
						(None, 	"move", {"dy" : -120}), #2
						(2, 	"loop", {"iterations" : 1}), #3
						### Move Right
						(None, 	"move", {"dx" : 120}), #4
						(4, 	"loop", {"iterations" : 1}), #5
						###	Move Down
						(None, 	"move", {"dy" : 120}), #6
						(6, 	"loop", {"iterations" : 1}), #7
						### Show Text
						(8, 	"show_dialog", {"time" : 1000, "text" : 'Hello world!'}), #8
						### Wait for space pressed
						(9, 	"wait_key", {"key" : 276}), #9
						(0, 	"goto", {}) #10
					]}}
				]
			},
			{
				"id" : "script_engine",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "script_engine", "name" : "Global Script Engine"}},
					{"type" : "Brain", "params" : {"commands" : [
					#	# IF-EXCEPTION-GOTO, CMD-FNC, CMD-PARAM
					#	(None, 	"move", {"entity" : "camera01", "dx" : -120}), #0
					#	(0, 	"loop", {"iterations" : 100}), #1
					#	(None, 	"move", {"entity": "camera01", "dy" : -120}), #2
					#	(2, 	"loop", {"iterations" : 20}), #3
					#	(None, 	"toggle_brain", {"entity" : "camera01", "enable" : False}), #4
					#	(0, 	"goto", {})  #5	
					]}}
				]
			},
			{
				"id" : "tele01",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "tele01", "name" : "Static Teleport"}},
					{"type" : "Position", "params" : {"x" : 400, "y" : 400, "map" : "map01"}},
					{"type" : "Motion", "params" : {"dx" : 0, "dy" : 0}},
					{"type" : "Renderable", "params" : {"image" : "teleport.png"}},
					{"type" : "Collidable", "params" : {"x" : 32, "y" : 32}},
					{"type" : "Camera", "params" : {"screen_pos_x" : 310, "screen_pos_y" : 310, "screen_width" : 300, "screen_height" : 300}},
					{"type" : "Teleport", "params" : {"dest_map" : "map01", "dest_x" : 200, "dest_y" : 1000, "key" : "item01"}}
				]
			},
			{
				"id" : "key01",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "key01", "name" : "Key to the cellar"}},
					{"type" : "Renderable", "params" : {"image" : "key.png"}},
					{"type" : "Collidable", "params" : {"x" : 20, "y" : 20}},
					{"type" : "Pickable", "params" : {}}
				]
			},
			{
				"id" : "npc01",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "npc01", "name" : "Merchant"}},
					{"type" : "Position", "params" : {"x" : 800, "y" : 200, "map" : "map01"}},
					{"type" : "Motion", "params" : {"dx" : 0, "dy" : 0}},
					{"type" : "Renderable", "params" : {"image" : "npc.png"}},
					{"type" : "Collidable", "params" : {"x" : 40, "y" : 40}},
					{"type" : "HasInventory", "params" : {"inventory" : ["key01"]}},
					{"type" : "CanTalk", "params" : {}},
					{"type" : "Debug", "params" : {}},
					{"type" : "Brain", "params" : {"commands" : [
						# IF-EXCEPTION-GOTO, CMD-FNC, CMD-PARAM
						### Move Left
						(None, 	"move", {"dx" : -120}), #0
						(0, 	"loop", {"iterations" : 30}), #1
						### Wait and show text
						(2, 	"show_dialog", {"time" : 3000, "text" : '... who will help me ...?'}), #2
						### Move Right
						(None, 	"move", {"dx" : 120}), #3
						(3, 	"loop", {"iterations" : 30}), #4
						### Wait and show text
						(5, 	"show_dialog", {"time" : 3000, "text" : '... Somebody please help me !!'}), #5
						(0, 	"goto", {}) #10
					]}}
				]
			},
			{
				"id" : "npc02",
				"components" : [
					{"type" : "Labeled", "params" : {"id" : "npc02", "name" : "Test NPC 02"}},
					{"type" : "Renderable", "params" : {"image" : "npc.png"}},
					{"type" : "Position", "params" : {"x" : 500, "y" : 500, "map" : "map01"}},
					{"type" : "Collidable", "params" : {"x" : 32, "y" : 32}},
					{"type" : "Camera", "params" : {"screen_pos_x" : 700, "screen_pos_y" : 700}}
				]
			}
		]
		self.phase_id = 'phase01'

		self.event_handlers = {
			
			"COLLISION" : [
				{
					"conditions" : {
						"params" : {
							"entity1" : "player01",
							"entity2" : "npc01"
						},
						"script" : "self.phase_id == 'phase01'" # Only in the first phase of the quest

					},
					"actions" : [
						["execute_script", {"script_body" : "print(f'Modifying Global Brain')"}],
						["modify_brain", {
							"entity" : "script_engine",
							"commands" : [
								# Stop Talking text of both Player and NPC (cmd_disable_talk)
								[None, "disable_talk", {"entity" : "player01"}], #0
								[None, "disable_talk", {"entity" : "npc01"}], #1
								# Stop Brain processing to both Player and NPC (cmd_toggle_brain)
								[None, "toggle_brain", {"entity" : "player01", "enable" : False}], #2
								[None, "toggle_brain", {"entity" : "npc01", "enable" : False}], #3
								# Stop Controlls to the PLAYER and NPC (cmd_toggle_control)
								[None, "toggle_control", {"entity" : "player01", "enable" : False}], #4
								[None, "toggle_control", {"entity" : "npc01", "enable" : False}], #5
								# Stop Motion to the PLAYER and NPC- so that direction is not reset all the time
								[None, "toggle_motion", {"entity" : "player01", "enable" : False}], #6
								[None, "toggle_motion", {"entity" : "npc01", "enable" : False}], #7
								# Lets entities face each other for the dialog
								[None, "face_entity", {"entity" : "npc01", "face" : "player01"}], #8
								[None, "face_entity", {"entity" : "player01", "face" : "npc01"}], #9								
								# Show text bubble to Player - 'HI, do jou have some job for me?'	
								[10, "show_dialog", {"entity" : "player01", "time" : 5000, "text" : 'Hi, do jou have some job for me?'}], #10
								# Show text buble to NPC - 'Sure, I need to get rid of those bloody rats.'
								[11, "show_dialog", {"entity" : "npc01", "time" : 5000, "text" : 'Sure, I need to get rid of those bloody rats.'}], #11
								# Show text bubble to Player - 'No, problem. Where can I find them?'
								[12, "show_dialog", {"entity" : "player01", "time" : 5000, "text" : 'No, problem. Where can I find them?'}], #12
								# Show text buble to NPC - 'They are in the cellar. Here is the key'
								[13, "show_dialog", {"entity" : "npc01", "time" : 5000, "text" : 'They are in the cellar. Here is the key'}], #13
								# NPC gives item to Player(Key) (cmd_add_to_inventory, cmd_remove_to_inventory)
								[None, "remove_from_inventory", {"entity" : "npc01", "item" : "key01"}], #14
								[None, "add_to_inventory", {"entity" : "player01", "item" : "key01"}], #15
								# Show text bubble to Player - 'Thanks.'
								[16, "show_dialog", {"entity" : "player01", "time" : 5000, "text" : 'Thanks!'}], #16
								# Add camera component to the NPC (cmd_add_screen)
								[None, "add_screen", {"entity" : "npc01", "screen_pos_x" : 0, "screen_pos_y" : 400, "screen_width" : 300, "screen_height" : 300}], #17
								# Resume Motion processing for Player and NPC 
								[None, "toggle_motion", {"entity" : "player01", "enable" : True}], #18
								[None, "toggle_motion", {"entity" : "npc01", "enable" : True}], #19
								# Resume Brain processing for Player and NPC (cmd_enable_brain)
								[None, "toggle_brain", {"entity" : "player01", "enable" : True}], #20
								[None, "toggle_brain", {"entity" : "npc01", "enable" : True}], #21
								# Resume Controlls to the PLAYER and NPC (cmd_toggle_control)
								[None, "toggle_control", {"entity" : "player01", "enable" : True}], #22
								[None, "toggle_control", {"entity" : "npc01", "enable" : True}], #23
								# change quest phase from 1 to 2 (cmd_set_quest_phase)					
								[None, "set_quest_phase", {"quest" : "test_quest", "phase" : "phase02"}] #24
								]
							}
						]
					]
				},
				{
					"conditions" : {
						"params" : {
							"entity1" : "player01",
							"entity2" : "npc01"
						},
						"script" : "self.phase_id == 'phase02'" # Only in the second phase of the quest

					},
					"actions" : [
						["execute_script", {"script_body" : "print(f'Modifying Global Brain')"}],
						["modify_brain", {
							"entity" : "script_engine", # script=4	 
							"commands" : [
								# Stop Talking text of both Player and NPC (cmd_disable_talk)
								[None, "disable_talk", {"entity" : "player01"}], #0
								[None, "disable_talk", {"entity" : "npc01"}], #1								
								# Stop Brain processing to both Player and NPC (cmd_disable_brain)
								[None, "toggle_brain", {"entity" : "player01", "enable" : False}], #2
								[None, "toggle_brain", {"entity" : "npc01", "enable" : False}], #3
								# Stop Controlls to the PLAYER and NPC (cmd_toggle_control)
								[None, "toggle_control", {"entity" : "player01", "enable" : False}], #4
								[None, "toggle_control", {"entity" : "npc01", "enable" : False}], #5
								# Stop Motion to the PLAYER and NPC- so that direction is not reset all the time
								[None, "toggle_motion", {"entity" : "player01", "enable" : False}], #6
								[None, "toggle_motion", {"entity" : "npc01", "enable" : False}], #7
								# Lets entities face each other for the dialog
								[None, "face_entity", {"entity" : "npc01", "face" : "player01"}], #8
								[None, "face_entity", {"entity" : "player01", "face" : "npc01"}], #9								
								# Show text bubble to Player - 'Hi, its harder than I though'	
								[10, "show_dialog", {"entity" : "player01", "time" : 5000, "text" : 'Hi, its harder than I though'}], #10
								# Show text buble to NPC - 'Go on, finish them 
								[11, "show_dialog", {"entity" : "npc01", "time" : 5000, "text" : 'Go on, finish them '}], #11
								# Resume Motion processing for Player and NPC 
								[None, "toggle_motion", {"entity" : "player01", "enable" : True}], #12
								[None, "toggle_motion", {"entity" : "npc01", "enable" : True}], #13
								# Resume Brain processing for Player and NPC (cmd_enable_brain)
								[None, "toggle_brain", {"entity" : "player01", "enable" : True}], #14
								[None, "toggle_brain", {"entity" : "npc01", "enable" : True}], #15
								# Resume Controlls to the PLAYER and NPC (cmd_toggle_control)
								[None, "toggle_control", {"entity" : "player01", "enable" : True}], #16
								[None, "toggle_control", {"entity" : "npc01", "enable" : True}] #17
								]
							}
						]
					]
				}				
			],

			"TELEPORTATION" : [
				{
					"conditions" : {
						"params" : {
							"teleport" : "tele01",
							"teleportee" : "player01"
						},
						"function" : ["script_condition_example", { "test_param" : "this is not atest"}]
					},
					"actions" : [ 
						["execute_script", { 
							#"script_file" : "",
							#"script_ref" : "script01",
							"script_body" : "pygame.time.wait(500)" 
							}
						], 
						["script_shake_screen", {}], 
						["script_disable_teleport", {}],
						
						["modify_brain", {
							"entity" : "player01", 
							"commands" : [
								[0, "show_dialog", {"time" : 5000, "text" : 'I have just been teleported!'}]
								]
							}
						]
					]					
				}				
			]
		}
		'''

	def event_handler(self, event):

		#print(f'*Starting quest event processing')
		#print(event)

		# Check if there are any actions defined for the event_type and iterate through
		for event_handle in self.event_handlers.get(event.event_type, []):

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
			[cond_function, cond_function_params] = conditions.get("function", ["script_condition_always_true", {}])


			# Evaluate the function condition
			try:
				#cond_function_result = globals()[cond_function](event, **cond_function_params)
				cond_function_result = getattr(script, cond_function)(event, **cond_function_params)
			except SyntaxError:
				print('Error in function condition for event {event}.')

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
						action_function_result = getattr(script, action_function)(event, **action_function_params)
					except SyntaxError:
						print('Error in action function for event {event}.')
					
		#print(f'*Finishing quest event processing')

	def set_phase(self, phase):
		self.phase_id = phase
		print(f'Phase was set to {self.phase_id}')
		return 0
