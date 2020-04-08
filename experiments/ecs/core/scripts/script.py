import core.engine as engine
import core.ecs.components as components
import core.ecs.processors as processors


import pygame
import random


########################################################
### Scripting function examples
########################################################

def modify_brain(event=None, *args, **kwargs):
	''' Called from quest 
	'''
	# Get the entity whose brain I will be working with
	entity = kwargs.get("entity", None)

	# Get the brain of the entity
	try:
		brain = engine.world.component_for_entity(entity, components.Brain)

		# Stop the brain
		brain.enabled = False

		# Delete and reset the brain with the new commands
		brain.reset(kwargs.get("commands", []))
		
		# Everything worked fine
		return 0

	except KeyError:
		# Entity has no brain
		return -1

def script_condition_always_true(event=None, *args, **kwargs):
	return True

def execute_script(event, *args, **kwargs):
	# Get script name from the arguments
	script_name = kwargs.get("script_ref", '')

	# Get the body of the script from  the quest data
	script_body = kwargs.get("script_body", '')
	
	# Execute the script
	exec(script_body)

def script_condition_example(event, *args, **kwargs):
	print(kwargs.get("test_param", "No test param"))
	return True

def script_disable_teleport(event, *args, **kwargs):
	#####
	# Remove the teleport possibilities from the teleport
	#####
	engine.world.remove_component(event.generator_obj, components.Collidable)

def script_shake_screen(event, *args, **kwargs):
	
	#####
	# Shake the Screen
	#####			
	camera = engine.world.component_for_entity(event.other_obj, components.Camera)
	original_cam_pos_x, camera.screen_pos_y = camera.screen_pos_x, camera.screen_pos_y
	for i in range(30):
		camera.screen_pos_x = camera.screen_pos_x + random.randint(-5,5)
		camera.screen_pos_y = camera.screen_pos_y + random.randint(-5,5)
		# Render the world
		engine.world.get_processor(processors.RenderProcessor).process()
		# Blit the world
		pygame.display.update()
		# Wait to make it more visible
		pygame.time.wait(50)
	# Put the screen back
	camera.screen_pos_x, camera.screen_pos_y = original_cam_pos_x, camera.screen_pos_y

