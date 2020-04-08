import sys 				# for getting size of instance object
import pygame 			# for Camera component
import pygame.freetype 	# for CanTalk component

########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()
if not pygame.freetype.get_init(): pygame.freetype.init() 

########################################################
### Component classes
########################################################

class Component:
	''' Parrent clas sfor all components
	'''
	def __init__(self): 
		pass

	def __str__(self):
		''' Print representation of the component instance
		'''
		return f"Component '{self.__class__.__name__}' at {hex(id(self))} ({sys.getsizeof(self)}): {self.__dict__}"


class Debug(Component):
	'''
	'''
	def __init__(self):
		''' Initiate values for the new Brain component
		'''
		super().__init__()
		self.font = pygame.font.Font(None, 16)


class Brain(Component):
	''' Entity can perform commands stored in its brain. 
	Contains commands and management variables. Commands are executed on given 
	entity and are in form of simple list.
	Command structure is following (tuple): (IF-Exception-Goto, CMD NAME, CMD PARAMS)
	
	TODO - Implement Commands as graph not simple list
	'''
	def __init__(self, commands=[]):
		''' Initiate values for the new Brain component
		'''
		super().__init__()

		# Should the brain process commands (True) or not (False).
		# If there are some commands passed then enable processing
		self.enabled = True if commands else False

		# Brain algorithm
		self.commands = commands

		# Idx of next command to process
		self.next_cmd_idx = 0 if commands else None
		
		# Idx of command currently in process
		self.current_cmd_idx = None

		# Idx of the last_cmd that was processed
		self.last_cmd_idx = None

		# When the current cmd unit was first invoked
		# Necessary for commands that work with time delays (cmd_wait)
		self.cmd_first_call_time = None

		# Init the Loop counter
		# Necessary for loop commands (cmd_loop)
		self.loop_counter = 0

	def process_result(self, exception):
		''' Process the result of processed command.
		Function is called by command queue. Based on the result of function
		move indexes in the brain so the proper command on next_cmd_idx is executed
		on the next run of Brain processor.
		'''
		
		# If the command finished succesfully - move to the next command
		if exception == 0:
			self.next_cmd_idx += 1
			#print(f'process_results: {self.commands[self.current_cmd_idx][1]} - Returned 0. Setting next_cmd_idx to {self.next_cmd_idx}')
		else:
			# If there is return value <> 0 ... that means exception then
			# set self.next_cmd_id to the exception record
			
			# Find out where to skip if there is exception
			goto_on_exception = self.commands[self.current_cmd_idx][0]
			#print(f'process_results: {self.commands[self.current_cmd_idx][1]} - Returned -1. Setting goto_on_exception to  {goto_on_exception}, self.next_cmd_idx = {self.next_cmd_idx}, self.current_cmd_idx = {self.current_cmd_idx}')


			# If there is some skipping defined
			if goto_on_exception != None:
				self.next_cmd_idx = goto_on_exception
				#print(f'process_results: {self.commands[self.current_cmd_idx][1]} - Returned -1. Setting next_cmd_idx to  {self.next_cmd_idx}')
			else:
				# If the command unit does not have defined goto skip on exception
				# then continue with the next command.
				self.next_cmd_idx += 1
				#print(f'process_results: {self.commands[self.current_cmd_idx][1]} - Returned -1, goto_on_exeption = None. Setting next_cmd_idx to  {self.next_cmd_idx}')

	def reset(self, commands=[]):

		# Should the brain process commands (True) or not (False).
		# If there are some commands passed then enable processing
		self.enabled = True if commands else False

		# Brain algorithm
		self.commands = commands

		# Idx of next command to process
		self.next_cmd_idx = 0 if commands else None
		
		# Idx of command currently in process
		self.current_cmd_idx = None

		# Idx of the last_cmd that was processed
		self.last_cmd_idx = None

		# When the current cmd unit was first invoked
		self.cmd_first_call_time = None

		# Init the Loop counter
		self.loop_counter = 0


class CanTalk(Component):
	''' Entity can produce text bubble that is displayed on the screen.
	'''

	def __init__(self, text_color=(255, 255, 255), font='experiments/ecs/JackInput.TTF', font_size=16):
		''' Initiate values for the new CanTalk component
		'''
		super().__init__()

		# Font parameters
		self.text_color = text_color
		self.font = font
		self.font_size = font_size

		# Necessary for generating graphical text representation
		self.font_object = pygame.freetype.Font(self.font, self.font_size)

		# Text to display
		self.text = '...'

		# Surface and rectangle describing the text in graphics
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)


class Labeled(Component):
	''' Entity has some id that is used in configuration files (json) to refer to the entity
	and a name.
	'''

	def __init__(self, id, name):
		''' Initiate values for the new Labeled component.
		'''
		super().__init__()

		self.id = id
		self.name = name


class Pickable(Component):
	''' Entity is pickable by HasInventory entity
	'''

	def __init__(self):
		''' Initiate values for the new Item component.
		'''
		super().__init__()


class HasInventory(Component):
	''' Entity has inventory - can pick items
	'''

	def __init__(self, inventory=[]):
		''' Initiate values for the new HasInventory component.
		'''

		super().__init__()
		self.inventory = inventory


class Transform(Component):
	''' Entity has possition in the game world specified by x,y and map.
	
	Used by:
		-	CameraProcessor
	'''

	def __init__(self, x=0.0, y=0.0, map=None):
		''' Initiate values for the new Transform component.
		'''
		super().__init__()
		
		# Map coordinates
		self.x = x
		self.y = y
		self.map = map
		
		#self.cell_x, self.map_x = math.modf(x) 
		#self.cell_y, self.map_y = math.modf(y)
		#self.map_x = int(self.map_x)
		#self.map_y = int(self.map_y)
		
		# Remember last possition, on collision return to the last known pos
		self.lastx = x
		self.lasty = y


class Teleport(Component):
	''' Entity is a teleport - i.e. on collision it changes position of
	the object that colided with the entity
	'''

	def __init__(self, dest_map, dest_x, dest_y, key=None):
		''' Initiate values for the new Teleport component.
		'''
		super().__init__()
		
		# Teleport destination
		self.dest_map = dest_map
		self.dest_x = dest_x
		self.dest_y = dest_y

		# Key for the teleport - no teleportation without key in inventory (entity)
		self.key = key


class Teleportable(Component):
	''' Entity is a teleportable - i.e. on collision with entity having
	Teleport component can be teleported.
	'''

	def __init__(self):
		''' Initiate values for the new Teleportable component.
		'''
		super().__init__()

# Implement vector2
class Motion(Component):
	'''	Entity can move
	'''

	def __init__(self, dx=0.0, dy=0.0):
		''' Initiate values for the new Motion component.
		'''
		super().__init__()
		
		# Change of position
		self.dx = dx
		self.dy = dy

		# Remember last move and if we have moved
		self.has_moved = False


class Renderable(Component):
	''' Entity is displayable on the game screen
	'''

	def __init__(self, image):
		''' Initiate values for the new Renderable component.
		'''
		super().__init__()

		# Image and its parameters
		self.image = image.convert()
		self.w = image.get_width()
		self.h = image.get_height()


class Controllable(Component):
	''' Entity can be controlled by the keyboard commands
	'''

	def __init__(self, control_keys={}, control_cmds={}):
		''' Initiate values for the new Controllable component.
		'''
		super().__init__()

		# Possibility to disable input for the global processor
		self.enabled = True

		# Keyboard arrows
		default_keys = {
			"left" : 276,
			"right": 275,
			"up" : 273,
			"down" : 274
		}
		
		# Merge defaults with defined
		self.control_keys = {**default_keys, **control_keys}

		# No default commands
		default_cmds = {}

		# Merge defaults with defined
		self.control_cmds = {**default_cmds, **control_cmds}


class Collidable(Component):
	''' Entity collides with other collidable entities
	'''

	def __init__(self, x, y):
		''' Initiate values for the new Collidable component.
		'''
		super().__init__()
		
		# With and height of the collision zone
		self.x = x
		self.y = y

		# Keep track with who the entity collided
		self.collision_events = set()


class Camera(Component):
	''' Entity is in focus of a camera that is displayed in form of a screen
	in the game window.

	Used by:
		-	CameraProcessor

	'''

	def __init__(self, screen_pos_x=0, screen_pos_y=0, screen_width=100, screen_height=100):
		''' Initiate values for the new Camera component.
		'''
		super().__init__()
		
		# Offset variables necessary for camera functionality - Offset is calculated by the CameraProcessor
		self.offset_x = 0
		self.offset_y = 0

		# Topleft position of the Camera screen
		self.screen_pos_x = screen_pos_x
		self.screen_pos_y = screen_pos_y

		# Width and height of the Camera screen
		self.screen_width = screen_width
		self.screen_height = screen_height

		# Camera screen surface on which map is blitted
		self.screen = pygame.Surface((screen_width, screen_height))
