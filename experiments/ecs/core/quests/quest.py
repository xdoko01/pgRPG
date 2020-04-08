import core.scripts.script as script
import core.commands.commands as commands

########################################################
### Quest class
########################################################

class Quest:
	''' Simple quest for testing purposes
		- should contain data for constructing/destructing the world
		- should remember mapping between entity_id and game_id in some dictionary
		- should contain event handlers
	'''
	def __init__(self):
		
		self.phase = 'phase01'

		self.script01 = "for i in range(10):\n\tprint('ahoj')\n\tprint('borce')\nscript_disable_teleport(event)"

		self.event_handlers = {
			
			"COLLISION" : [
				{
					"conditions" : {
						"params" : {
							"entity1" : 1,
							"entity2" : 7
						},
						"script" : "self.phase == 'phase01'" # Only in the first phase of the quest

					},
					"actions" : [
						("execute_script", {"script_body" : "print(f'Modifying Global Brain')"}),
						("modify_brain", {
							"entity" : 4, # script=4	 
							"commands" : [
								# Stop Brain processing to both Player and NPC (cmd_disable_brain)
								(None, commands.cmd_toggle_brain, {"entity" : 1, "enable" : False}), #0
								(None, commands.cmd_toggle_brain, {"entity" : 7, "enable" : False}), #1
								# Stop Controlls to the PLAYER and NPC (cmd_toggle_control)
								(None, commands.cmd_toggle_control, {"entity" : 1, "enable" : False}), #2
								(None, commands.cmd_toggle_control, {"entity" : 7, "enable" : False}), #3
								# Show text bubble to Player - 'HI, do jou have some job for me?'	
								(4, commands.cmd_show_dialog, {"entity" : 1, "time" : 10000, "text" : 'Hi, do jou have some job for me?'}), #4
								# Show text buble to NPC - 'Sure, I need to get rid of those bloody rats.'
								(5, commands.cmd_show_dialog, {"entity" : 7, "time" : 10000, "text" : 'Sure, I need to get rid of those bloody rats.'}), #5
								# Show text bubble to Player - 'No, problem. Where can I find them?'
								(6, commands.cmd_show_dialog, {"entity" : 1, "time" : 10000, "text" : 'No, problem. Where can I find them?'}), #6
								# Show text buble to NPC - 'They are in the cellar. Here is the key'
								(7, commands.cmd_show_dialog, {"entity" : 7, "time" : 10000, "text" : 'They are in the cellar. Here is the key'}), #7
								# NPC gives item to Player(Key) (cmd_add_to_inventory, cmd_remove_to_inventory)
								(None, commands.cmd_remove_from_inventory, {"entity" : 7, "item" : 6}), #8
								(None, commands.cmd_add_to_inventory, {"entity" : 1, "item" : 6}), #9
								# Show text bubble to Player - 'Thanks.'
								(10, commands.cmd_show_dialog, {"entity" : 1, "time" : 5000, "text" : 'Thanks!'}), #10
								# Add camera component to the NPC (cmd_add_screen)
								(None, commands.cmd_add_screen, {"entity" : 7, "screen_pos_x" : 0, "screen_pos_y" : 400, "screen_width" : 300, "screen_height" : 300}), #11
								# Resume Brain processing for Player and NPC (cmd_enable_brain)
								(None, commands.cmd_toggle_brain, {"entity" : 1, "enable" : True}), #12
								(None, commands.cmd_toggle_brain, {"entity" : 7, "enable" : True}), #13	
								# Resume Controlls to the PLAYER and NPC (cmd_toggle_control)
								(None, commands.cmd_toggle_control, {"entity" : 1, "enable" : True}), #14
								(None, commands.cmd_toggle_control, {"entity" : 7, "enable" : True}), #15
								# change quest phase from 1 to 2 (cmd_set_quest_phase)					
								(None, commands.cmd_set_quest_phase, {"quest" : "test_quest", "phase" : "phase02"}) #16		
								]
							}
						)
					]
				},
				{
					"conditions" : {
						"params" : {
							"entity1" : 1,
							"entity2" : 7
						},
						"script" : "self.phase == 'phase02'" # Only in the second phase of the quest

					},
					"actions" : [
						("execute_script", {"script_body" : "print(f'Modifying Global Brain')"}),
						("modify_brain", {
							"entity" : 4, # script=4	 
							"commands" : [
								# Stop Brain processing to both Player and NPC (cmd_disable_brain)
								(None, commands.cmd_toggle_brain, {"entity" : 1, "enable" : False}), #0
								(None, commands.cmd_toggle_brain, {"entity" : 7, "enable" : False}), #1
								# Stop Controlls to the PLAYER and NPC (cmd_toggle_control)
								(None, commands.cmd_toggle_control, {"entity" : 1, "enable" : False}), #2
								(None, commands.cmd_toggle_control, {"entity" : 7, "enable" : False}), #3
								# Show text bubble to Player - 'Hi, its harder than I though'	
								(4, commands.cmd_show_dialog, {"entity" : 1, "time" : 10000, "text" : 'Hi, its harder than I though'}), #4
								# Show text buble to NPC - 'Go on, finish them 
								(5, commands.cmd_show_dialog, {"entity" : 7, "time" : 10000, "text" : 'Go on, finish them '}), #5
								# Resume Brain processing for Player and NPC (cmd_enable_brain)
								(None, commands.cmd_toggle_brain, {"entity" : 1, "enable" : True}), #6
								(None, commands.cmd_toggle_brain, {"entity" : 7, "enable" : True}), #7	
								# Resume Controlls to the PLAYER and NPC (cmd_toggle_control)
								(None, commands.cmd_toggle_control, {"entity" : 1, "enable" : True}), #8
								(None, commands.cmd_toggle_control, {"entity" : 7, "enable" : True}), #9
								]
							}
						)
					]
				}				
			],

			"TELEPORTATION" : [
				{
					"conditions" : {
						"params" : {
							"teleport" : 4,
							"teleportee" : 1
						},
						"script" : "event.params.get('teleport') == 4 and event.params.get('teleportee') == 1 and self.script01 != None",
						"function" : ("script_condition_example", { "test_param" : "this is not atest"})
					},
					"actions" : [ 
						("execute_script", { 
							#"script_file" : "",
							#"script_ref" : "script01",
							"script_body" : "pygame.time.wait(500)" 
							}
						), 
						("script_shake_screen", {}), 
						("script_disable_teleport", {}),
						
						("modify_brain", {
							"entity" : 1, 
							"commands" : [
								(0, commands.cmd_show_dialog, {"time" : 5000, "text" : 'I have just been teleported!'})
								]
							}
						)
					]					
				}				
			]
		}

	def event_handler(self, event):

		print(f'*Starting quest event processing ALT 2')
		print(event)

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
				cond_param_result = cond_param_result and (event.params.get(cond_param_key, None) == cond_param_value)

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

			#####
			# FUNCTION condition
			#####

			# Expect that the result is False to start with
			cond_function_result = False

			# Evaluate condition FUNCTION - python func must evaluate to True in order the condition to pass			
			(cond_function, cond_function_params)  = conditions.get("function", ("script_condition_always_true", {}))


			# Evaluate the function condition
			try:
				#cond_function_result = globals()[cond_function](event, **cond_function_params)
				cond_function_result = getattr(script, cond_function)(event, **cond_function_params)
			except SyntaxError:
				print('Error in function condition for event {event}.')

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
					
		print(f'*Finishing quest event processing')

	def set_phase(self, phase):
		self.phase = phase
		print(f'Phase was set to {self.phase}')
		return 0
