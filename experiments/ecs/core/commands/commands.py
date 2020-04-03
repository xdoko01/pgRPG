import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

import pygame.time # pygame.ime

# TODO - do it as functions and not classes
# world should be probably passed always to command so command can actually do something usefull
# probably entity of the world should be passed


def cmd_move_left_ent(entity, step):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = engine.world.component_for_entity(entity, components.Motion)
	motion.dx = -step
	
def cmd_move_right_ent(entity, step):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = engine.world.component_for_entity(entity, components.Motion)
	motion.dx = step

def cmd_move_up_ent(entity, step):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = engine.world.component_for_entity(entity, components.Motion)
	motion.dy = -step

def cmd_move_down_ent(entity, step):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = engine.world.component_for_entity(entity, components.Motion)
	motion.y = step

############

def cmd_move_left(entity, step, component=None):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = component if component else engine.world.component_for_entity(entity, components.Motion)
	motion.dx = -step

def cmd_move_right(entity, step, component=None):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = component if component else engine.world.component_for_entity(entity, components.Motion)
	motion.dx = step

def cmd_move_up(entity, step, component=None):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = component if component else engine.world.component_for_entity(entity, components.Motion)
	motion.dy = -step

def cmd_move_down(entity, step, component=None):
	''' Entity is optional, there can be commands that do not require entity
	'''
	motion = component if component else engine.world.component_for_entity(entity, components.Motion)
	motion.dy = step

####################

def cmd_show_dialog(*args, **kwargs):
	''' Show text dialog
	'''
	# Get entity from cmd parameters
	entity = kwargs.get("entity", None)
	
	# Get can talk component from entity
	can_talk = engine.world.component_for_entity(entity, components.CanTalk)

	# Get brain component(timer) and all the other cmd parameters
	brain = kwargs.get("brain", None)
	text = kwargs.get("text", '')
	time = kwargs.get("time", 0)
	
	current_time = pygame.time.get_ticks()
	
	if current_time - brain.cmd_first_call_time >= time:
		
		# Text has been shown long enough - continue without exception and reset the text
		# in can_talk component (as a result it will not be drawn by the render function)
		can_talk.text = ''		

		return 0
	else:
		# There is still some time to display the text - return exception

		# TODO - maybe only for the first time it is called last_idx <> next_idx condition
		if brain.last_cmd_idx != brain.next_cmd_idx:
			can_talk.text = text
			(can_talk.text_surf, can_talk.text_rect) = can_talk.font_object.render(can_talk.text, (0,0,255), None)

		return -1


def cmd_loop(*args, **kwargs):
	''' Loop command - uses information stored in brain about actual number of loops
	'''
	iterations = kwargs.get("iterations", 0)
	brain = kwargs.get("brain", None)

	# Increase counter
	brain.loop_counter += 1

	if iterations > brain.loop_counter:
		# Throw exception - iteration has not finished
		return -1
	else:
		# Reset the looper
		brain.loop_counter = 0
		# Do not throw exception, looping has finished
		return 0


def cmd_wait(*args, **kwargs):
	''' Wait command used for example to slow done the motion
	'''
	wait_time = kwargs.get("time", 0)
	brain = kwargs.get("brain", None)

	current_time = pygame.time.get_ticks()
	
	if current_time - brain.cmd_first_call_time >= wait_time:
		# Unit has waited long enough - continue without exception
		return 0
	else:
		# There is still some time to wait - return exception
		return -1

def cmd_goto(*args, **kwargs):
	''' Goto command always returns exception. By doing that
	it always skips to unit defined by index in IF-EXCEPTION-GOTO
	'''
	return -1


def cmd_none(*args, **kwargs):
	''' Empty command - Null object pattern.
	It is useful if we want some action keys to do nothing
	'''
	return 0

def cmd_move(*args, **kwargs):
	''' Pass whatever information you think are necessary for the command
	and let the command utilize them or not
	'''

	# Get parameters for movement
	entity = kwargs.get("entity")
	
	# It is important to return None if parameter is not passed and not 0
	# The reason is that several commands may come in one loop and we do not
	# want to change the results of the previous command - enable diagonal
	# scrolling.
	dx = kwargs.get("dx", None)
	dy = kwargs.get("dy", None)

	# if Move component does not exist on entity then error is not raised
	try:
		# Get the motion component from the entity
		motion = engine.world.component_for_entity(entity, components.Motion)
		
		# Change the motion if parameter passed in the command
		motion.dx = dx if dx else motion.dx
		motion.dy = dy if dy else motion.dy

	except KeyError:
		print(f'Entity {entity} does not have Motion component.')
		
	finally:
		# Mark that command has finished. Important for Brain processor
		return 0 

def cmd_disable_collision(*args, **kwargs):
	'''
	'''
	entity = kwargs.get("entity")
	engine.world.remove_component(entity, components.Collidable)		



########################################
class Command:

	def __init__(self):
		pass

	def execute(self):
		pass

class MoveCommand(Command):

	def __init__(self, dx, dy):
		super().__init__()
		self.dx = dx
		self.dy = dy

	def execute(self, motion_component):
		motion_component.dx = self.dx
		motion_component.dy = self.dy

class DisableTeleportCommand(Command):
	
	def __init__(self, world):
		super().__init__()
		self.world = world

	def execute(self, teleport_entity):
		self.world.remove_component(4, components.Collidable)		
