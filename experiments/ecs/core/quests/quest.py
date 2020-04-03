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
		
		self.script01 = "for i in range(10):\n\tprint('ahoj')\n\tprint('borce')\nscript_disable_teleport(event)"

		self.event_handlers = {
			
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

