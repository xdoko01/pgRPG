import core.config.config as config  # For renderable component IMAGE_PATH
import core.engine as engine # For checking the engine._entity_map - if component has entity as a str as a parameter (HasInventory)

import sys 				# for getting size of instance object
import pygame 			# for Camera component
import pygame.freetype 	# for CanTalk component

########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()
if not pygame.freetype.get_init(): pygame.freetype.init() 

########################################################
### Module globals
########################################################

# Available components - if component is not defined here, it will not be 
# assigned to the entity
ALL_COMPONENTS = ['Debug', 'Labeled', 'Controllable', 'Renderable', 'Transform',\
	'Collidable', 'Camera', 'Brain', 'CanTalk', 'Pickable', 'HasInventory',\
	'Teleport', 'Teleportable', 'Motion']

########################################################
### Module functions
########################################################

def _create_component(world, entity: int, comp_class: str, comp_params: dict):
	''' Add a new component to the given entity in given world
	'''

	# Check if component exists 
	assert(comp_class in ALL_COMPONENTS, f'Trying to assign unknown component {comp_class} to entity {entity}.')

	# Get the component class
	c = globals()[comp_class]

	# Create the instance of the component
	world.add_component(entity, c(**comp_params))

	# Return success
	return 0

########################################################
### Component classes
########################################################

class Component:
	''' Parent class for all components
	'''
	def __init__(self): 
		pass

	def __str__(self):
		''' Print representation of the component instance
		'''
		return f"Component '{self.__class__.__name__}' at {hex(id(self))} ({sys.getsizeof(self)}): {self.__dict__}"

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects.
		'''
		pass

	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		pass


class Debug(Component):
	''' Display debug information on entities that are tagged by this component.
	'''
	def __init__(self, *args, **kwargs):
		''' Initiate values for the new component
		'''
		super().__init__()

		# Font used for displaying debug information
		self.font = pygame.font.Font(None, 16)

	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.font = None

	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.font = pygame.font.Font(None, 16)


class Brain(Component):
	''' Entity can perform commands stored in its brain. 
	Contains commands and management variables. Commands are executed on given 
	entity and are in form of simple list.
	Command structure is following (tuple): (IF-Exception-Goto, CMD NAME, CMD PARAMS)
	'''
	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Brain component
		'''
		super().__init__()

		# Brain algorithm
		self.commands = kwargs.get('commands', [])

		# Should the brain process commands (True) or not (False).
		# If there are some commands passed then enable processing
		self.enabled = True if self.commands else False

		# Idx of next command to process
		self.next_cmd_idx = 0 if self.commands else None
		
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
		else:
			# If there is return value <> 0 ... that means exception then
			# set self.next_cmd_id to the exception record
			
			# Find out where to skip if there is exception
			goto_on_exception = self.commands[self.current_cmd_idx][0]

			# If there is some skipping defined
			if goto_on_exception != None:
				self.next_cmd_idx = goto_on_exception
			else:
				# If the command unit does not have defined goto skip on exception
				# then continue with the next command.
				self.next_cmd_idx += 1

	def reset(self, commands=[]):
		''' Fill the brain with the new set of commands
		'''

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

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new CanTalk component
		'''
		super().__init__()

		# Font parameters
		self.text_color = kwargs.get('text_color', (255, 255, 255))
		self.font = kwargs.get('font', 'experiments/ecs/FiraCode-Regular.ttf')
		self.font_size = kwargs.get('font_size', 12)

		# Necessary for generating graphical text representation
		self.font_object = pygame.freetype.Font(self.font, self.font_size)

		# Text to display
		self.text = '...'

		# Surface and rectangle describing the text in graphics
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)

	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.font_object = None
		self.text_surf = None
		self.text_rect = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.font_object = pygame.freetype.Font(self.font, self.font_size)
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)


class Labeled(Component):
	''' Entity has some id that is used in configuration files (json) to refer to the entity
	and a name.
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Labeled component.
		'''
		super().__init__()

		self.id = kwargs.get("id", None)
		self.name = kwargs.get("name", None)


class Pickable(Component):
	''' Entity is pickable by HasInventory entity
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Item component.
		'''
		super().__init__()


class HasInventory(Component):
	''' Entity has inventory - can pick items
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new HasInventory component.
		'''

		super().__init__()

		# Substitute the inventory items that are specified by id (str) with entity ids (int)
		# based on mapping in engine class
		self.inventory = [engine._entity_map.get(item) if isinstance(item, str) else item for item in kwargs.get('inventory', [])]


class Transform(Component):
	''' Entity has possition in the game world specified by x,y and map.
	
	Used by:
		-	CameraProcessor
	'''

	def __init__(self, *args, **kwargs):

		''' Initiate values for the new Transform component.
		'''
		super().__init__()
		
		# Coordinates in the world
		self.x = kwargs.get('x', 0)
		self.y = kwargs.get('y', 0)
		self.map = kwargs.get('map')

		# Direction SOUTH (0,1) NORD (0,-1) WEST (-1,0) EAST (1,0)
		# Necessary for correct rendering of sprites and text boxes etc.
		self.direction = (0, 1)

		# Remember last possition, on collision return to the last known pos
		self.lastx = self.x
		self.lasty = self.y
		self.lastmap = self.map
		#self.lastdir = self.direction


class Teleport(Component):
	''' Entity is a teleport - i.e. on collision it changes position of
	the object that colided with the entity
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Teleport component.
		'''
	
		super().__init__()
		
		# Teleport destination - mandatory
		try:
			self.dest_map = kwargs.get('dest_map')
			self.dest_x = kwargs.get('dest_x')
			self.dest_y = kwargs.get('dest_y')
		except KeyError:
			raise

		# Key for the teleport - no teleportation without key in inventory (entity) - optional
		teleport_key = kwargs.get('key', None)
		self.key = engine._entity_map.get(teleport_key) if isinstance(teleport_key, str) else teleport_key


class Teleportable(Component):
	''' Entity is a teleportable - i.e. on collision with entity having
	Teleport component can be teleported.
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Teleportable component.
		'''
		super().__init__()

# Implement vector2
class Motion(Component):
	'''	Entity can move
	'''
	
	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Motion component.
		'''
		super().__init__()
		
		self.enabled = True

		# Change of position
		self.dx = kwargs.get('dx', 0.0)
		self.dy = kwargs.get('dy', 0.0)

		# Remember last move and if we have moved
		#self.has_moved = False

		# Remember time when the entity last moved
		# Necessary to know when to reset the direction of the entity due to rendering
		self.last_move = pygame.time.get_ticks()


class Renderable(Component):
	''' Entity is displayable on the game screen
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Renderable component.
		'''
		super().__init__()


		# Image and its parameters
		self.image_file = kwargs.get("image", "")
		self.image = pygame.image.load(config.IMAGE_PATH + self.image_file).convert()
		self.w = self.image.get_width()
		self.h = self.image.get_height()

		# Diff vector from centre of the sprite to the topleft corner
		# it is used by Render processor to get the right point where
		# to render the sprite. i.e. position of the character can be 
		# 100, 100 but in order to be centered on this position, render 
		# processor must blit the sprite on 75,75 (example w,h=50)
		self.d_w = self.w / 2
		self.d_h = self.h / 2

	def topleft(self, pos):
		''' Returns correction of coordinates to display the sprite correctly
		'''
		return (pos[0] - self.d_w, pos[1] - self.d_h)

	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.image = None
		self.w = None
		self.h = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.image = pygame.image.load(config.IMAGE_PATH + self.image_file).convert()
		self.w = self.image.get_width()
		self.h = self.image.get_height()


class Controllable(Component):
	''' Entity can be controlled by the keyboard commands
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Controllable component.
		'''
		super().__init__()

		control_keys = kwargs.get("control_keys", {})
		control_cmds = kwargs.get("control_cmds", {})

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

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Collidable component.
		'''
		super().__init__()
		
		# With and height of the collision zone
		self.x = kwargs.get('x', 0)
		self.y = kwargs.get('y', 0)

		# Keep track with who the entity collided
		self.collision_events = set()


class Camera(Component):
	''' Entity is in focus of a camera that is displayed in form of a screen
	in the game window.

	Used by:
		-	UpdateCameraOffsetProcessor

	'''
	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Camera component.
		'''
		
		super().__init__()

		# Should the camera be always centered on the entity - default is False (better)
		self.always_center = False
		
		# Rectancle (top-left and bottom-right positions in pixels) of the map that is displayed on
		# camera.screen surface. It is used for rendering of map on the screen. Rectancle is calculated
		# by the UpdateCameraOffsetProcessor.
		self.map_screen_rect = (0,0,0,0)

		# Offset variables necessary for camera functionality - Offset is calculated by the 
		# UpdateCameraOffsetProcessor
		self.offset_x = 0
		self.offset_y = 0

		# Topleft position of the Camera screen
		self.screen_pos_x = kwargs.get('screen_pos_x', 0)
		self.screen_pos_y = kwargs.get('screen_pos_y', 0)

		# Width and height of the Camera screen
		self.screen_width = kwargs.get('screen_width', 100)
		self.screen_height = kwargs.get('screen_height', 100)

		# Half of width and height is precalculated to avoid repetitive calculations /2
		self.screen_width_half = int(round(self.screen_width / 2))
		self.screen_height_half = int(round(self.screen_height / 2))

		# Camera screen surface on which map is blitted
		self.screen = pygame.Surface((self.screen_width, self.screen_height))
	
	def apply(self, pos=(0,0)):
		''' Applying camera offset to some position. Returns new position
		of the object and hence enables scrolling effect.
		'''
		# Move the sprite of the entity - returns new shifted coordinates
		return (pos[0] + self.offset_x, pos[1] + self.offset_y)
	
	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.screen = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.screen = pygame.Surface((self.screen_width, self.screen_height))

