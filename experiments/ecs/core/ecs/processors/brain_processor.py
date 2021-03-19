__all__ = ['BrainProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components
import pygame	# for pygame.time.get_ticks()


class BrainProcessor(esper.Processor):

	def __init__(self, input_command_queue):
		super().__init__()
		
		self.input_command_queue = input_command_queue

	def process(self, *args, **kwargs):
		for ent, (brain) in self.world.get_component(components.Brain):
			
			# Only continue processing if the brain is enabled
			if brain.enabled:

				# Get the command unit for processing
				try:
					unit = brain.commands[brain.next_cmd_idx]
				except:
					print(f'No command found, disabling brain. {brain}')
					brain.enabled = False
					return
				
				# Move pointers - next_cmd_idx is not yet decided, depends on the result of unit execution
				brain.last_cmd_idx = brain.current_cmd_idx
				brain.current_cmd_idx = brain.next_cmd_idx
				
				# Parse command unit - cmd_fnc is string
				_, cmd_fnc, cmd_params = unit

				# Put the command into the queue for processing - entity and brain can be override by the command
				# itself. It is used for global scripting functionality.
				self.input_command_queue.append((cmd_fnc, {**{"entity" : ent, "brain" : brain}, **cmd_params}))

				# If the unit exist then check if it was previously called
				# remember the self.unit_first_call_time
				if brain.next_cmd_idx != brain.last_cmd_idx:
					brain.cmd_first_call_time = pygame.time.get_ticks()
					#print(f'Setting up first call cmd time: {cmd_fnc}')

				# DEBUG
				#print(f'CMD inserted - Cmd: {cmd_fnc}, last_idx: {brain.last_cmd_idx}, current_idx: {brain.current_cmd_idx}, next_idx: {brain.next_cmd_idx}')

				# The result of the command will be communicated by the command_queue directly to component function
				#brain.process_resutt()
