import core.engine as engine
import core.ecs.components as components
import core.ecs.processors as processors
import functions as func

import pygame
from pygame.locals import *  # used for wait(function)

import random

########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()

########################################################
### Scripting function examples
########################################################

#def wait():
#	''' Waits for the given key to be pressed
#	Enter in this case but can be enhanced to any key.
#	'''
#
#	pygame.event.clear()
#
#	while True:
#		event = pygame.event.wait()
#		if event.type == QUIT:
#			return
#		elif event.type == KEYDOWN:
#			if event.key == K_RETURN:
#				return


def modify_brain(event=None, *args, **kwargs):
	''' Called from quest 
	'''
	# Get the entity whose brain I will be working with
	entity = engine._entity_map.get(kwargs.get("entity", None))

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
		engine.world.get_processor(processors.RenderWorldProcessor).process()
		# Blit the world
		pygame.display.update()
		# Wait to make it more visible
		pygame.time.wait(50)
	# Put the screen back
	camera.screen_pos_x, camera.screen_pos_y = original_cam_pos_x, camera.screen_pos_y

def script_show_text(event, *args, **kwargs):
	''' Show text pane over the whole game window
	and wait for the key press
	'''
	
	font = pygame.font.Font(None, 20)

	# Draw square on the screen
	#pygame.draw.rect(engine.window, (128, 128, 128, 128), pygame.Rect(10, 10, 600, 600), width=0, border_radius = 10)

	# Text is the list of texts that should be displayed
	texts = kwargs.get('texts', [])
	
	# Show the texts separatelly and wait for the key press between
	for text in texts:

		engine.world.get_processor(processors.UpdateCameraOffsetProcessor).process()
		engine.world.get_processor(processors.RenderMapProcessor).process()

		pygame.draw.rect(engine.window, (128, 128, 128, 0), pygame.Rect(10, 10, 600, 600))
		engine.window.blit(font.render(text, True, pygame.Color('white')), (20, 20) )

		# Blit the text on the screen
		#engine.window.blit()
		# Refresh the screen
		pygame.display.update()
		# Wait for the key pressed
		func.wait(pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE)
