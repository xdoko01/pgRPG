''' Module containing all components

	TODO 
	- implement __slots__ on component objects for memory optimization
	- implement parameter checking on component constructors
	- implement if __name == '__main__'

'''

import core.config.config as config  # For renderable component IMAGE_PATH
import core.engine as engine # For checking the engine._entity_map - if component has entity as a str as a parameter (HasInventory) + engine._maps 

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
ALL_COMPONENTS = ['Debug', 'Labeled', 'Controllable', 'Renderable', 'Position',\
	'Collidable', 'Camera', 'Brain', 'CanTalk', 'Pickable', 'HasInventory',\
	'Teleport', 'Teleportable', 'Motion']

########################################################
### Module functions
########################################################

def create_component(world, entity: int, comp_class: str, comp_params: dict):
	''' Add a new component to the given entity in given world. 
	
	Parameters:
		:param world: ECS world in which the component should be created.
		:type world: esper.World()
	
		:param entity: Entity to which component should be assigned.
		:type entity: int

		:param comp_class: Name of the component class.
		:type comp_class: str

		:param comp_params: Parameters for initiation of component instance.
		:type comp_params: dict

		:return: Returns 0 if component instance was successfully created and assigned.

		:raises: ValueException, if component instance cannot be created

	Called from:
		engine module -> create_entity function
	'''

	# Get the component class - check if such class exists and is allowed
	try:
		# Check if component exists 
		assert comp_class in ALL_COMPONENTS, f'Trying to assign unknown component {comp_class} to entity {entity}.'

		comp_name = globals()[comp_class]
	
	except (AssertionError, KeyError):
		print(f'Trying to assign unknown component {comp_class} to entity {entity}.')
		raise ValueError

	# Try to create instance of the component
	try:
		# Create the instance of the component
		comp_inst = comp_name(**comp_params)
	except ValueError:
		print(f'Incorrect parameters while creating component {comp_class} for entity {entity}')
		raise ValueError

	# Add new component to the world
	world.add_component(entity, comp_inst)

	# Return success
	return 0

########################################################
### Component classes
########################################################

class Component(object):
	''' Parent class for all components. Inheritance from object is a must
	because __slots__ are used in inherited component classes.
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

	Used by:
		-	RenderDebugProcessor
	'''

	__slots__ = 'font'

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
	''' Entity can perform commands stored in its brain. Contains commands 
	and management variables. Commands are executed on given entity and are 
	in form of simple list.
	
	Command structure is following (tuple): (IF-Exception-Goto, CMD NAME, CMD PARAMS)

	Overview:
		-	Brain processor checks the commant that is on current position and puts
		it into command queue for processing.
		-	If command returns success (no exception) the index of the brain moves
		to the next command and again puts it into the queue for processing.
		-	If command returns exception then the index is moved so that it is 
		pointing to  IF-EXCEPTION_GOTO item in the list.
		-	Those exceptions then facilitate execution of one command many times
		until it succeedes (for examle wait command) or looping in the commands
		(loop command)

	Used by:
		-	BrainProcessor
		-	RenderDebugProcessor
	'''

	__slots__ = ['commands', 'enabled', 'next_cmd_idx', 'current_cmd_idx', 'last_cmd_idx',\
				'cmd_first_call_time', 'loop_counter']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Brain component.

			Parameters:
				:param commands: List of commands to execute
				:type commands: list
		'''

		super().__init__()

		# Brain algorithm in form of the list
		self.commands = kwargs.get('commands', [])

		try:
			assert isinstance(self.commands, list), f'Commands must be passed as a list.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError		

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
		''' Processes the result of processed command and moves the brain indexes
		so that those are pointing to the next command that needs to be pushed
		into the command queue.
		
		Overview:
			Function is called by command queue processor. Based on the result of function
			move indexes in the brain so the proper command on next_cmd_idx is executed
			on the next run of Brain processor.
		
		Parameters:
			:param exception: In case of successfull cmd finish returns 0
			:type exception: int
		
		Called from:
			engine module -> process_game_commands function		
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
		''' Empty and fill the brain with the new set of commands.

		Parameters:
			:param commands: List of new commands to be added into empty brain.
			:type commands: list
		
		Called from:
			scripts module -> modify_brain function		
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
	''' Entity can generate the text bubble that is displayed on the screen.

	Used by:
		-	RenderWorldProcessor
	'''

	__slots__ = ['font_object', 'text', 'text_surf', 'text_rect']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new CanTalk component.

		Parameters:
			:param text_color: Color of the text
			:type text_color: tuple

			:param font: Path to the used font
			:type font: str

			:param font_size: Size of the font
			:type font: int
		'''

		super().__init__()

		# Font parameters
		self.text_color = kwargs.get('text_color', (255, 255, 255))
		self.font = kwargs.get('font', 'experiments/ecs/FiraCode-Regular.ttf')
		self.font_size = kwargs.get('font_size', 12)

		# Check that parameters have correct type
		try:
			assert isinstance(self.font, str), f'Font must be passed in the form of string.'
			assert isinstance(self.font_size, int), f'Font size must be passed as int.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Necessary for generating graphical text representation
		self.font_object = pygame.freetype.Font(self.font, self.font_size)

		# Text to display
		self.text = '...'

		# Surface and rectangle describing the text in graphics
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects.
		'''
		self.font_object = None
		self.text_surf = None
		self.text_rect = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component.
		'''
		self.font_object = pygame.freetype.Font(self.font, self.font_size)
		(self.text_surf, self.text_rect) = self.font_object.render(self.text, self.text_color, None)


class Labeled(Component):
	''' Entity has some id and name that is used in configuration files (json) 
	to refer to the entity.

	Used by:
		-	RenderDebugProcessor
	'''

	__slots__ = ['id', 'name']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the  Labeled component.

		Parameters:
			:param id: Game ID of the entity. Can differ from ECS id
			:type id: str

			:param name: Game name of the entity
			:type name: str
		'''
		super().__init__()

		self.id = kwargs.get("id", None)
		self.name = kwargs.get("name", None)


class Pickable(Component):
	''' Entity is pickable by HasInventory entity.

	Used by:
		-	CollisionItemProcessor
	'''

	__slots__ = []

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Item component. Component has
		no arguments, it is just a tag, in fact.
		'''

		super().__init__()


class HasInventory(Component):
	''' Entity has inventory - can pick items and add it to the inventory.

	Used by:
		-	RenderDebugProcessor
		-	CollisionTeleportProcessor
		-	CollisionItemProcessor
	'''

	__slots__ = ['inventory']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new HasInventory component.

		Parameters:
			:param inventory: List of entities that are in the inventory
			:type inventory: List of string or list of integers
		'''

		super().__init__()

		# Check that inventory is a list
		try:
			assert isinstance(kwargs.get('inventory', []), list), f'Inventory must be a list of entities.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Substitute the inventory items that are specified by id (str) with entity ids (int)
		# based on mapping in engine class
		try:
			self.inventory = [engine._entity_map.get(item) if isinstance(item, str) else item for item in kwargs.get('inventory', [])]
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Item in the inventory is not initiated in global list of entities.')
			raise ValueError


class Position(Component):
	''' Entity has possition in the game world specified by x, y and map.
	
	Used by:
		-	UpdateCameraOffsetProcessor
		-	MovementProcessor
		-	RenderMapProcessor
		-	RenderWorldProcessor
		-	RenderDebugProcessor
		-	CollisionMapProcessor
		-	CollisionEntityGeneratorProcessor
		-	CollisionTeleportProcessor
		-	CollisionEntityProcessor
		-	CollisionCorrectorProcessor
		-	RenderMapProcessorFullScan (OBSOLETE)
	'''

	__slots__ = ['x', 'y', 'map', 'direction']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Position component.

		Parameters:
			:param x: X-axis position in pixels on the map.
			:type x: int

			:param y: Y-axis position in pixels on the map.
			:type y: int

			:param map: Name of the map where entity is present.
			:type map: str

			:raise: ValueError - in case mandatory parameters are missing.
		'''

		super().__init__()
		
		# Coordinates in the world
		try:
			self.x = kwargs.get('x')
			self.y = kwargs.get('y')
			self.map = kwargs.get('map')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that map exists in the global list of all initiated maps engine
		try:
			assert self.map in engine._maps.keys(), f'Map {self.map} is not initialized for {self.__class__} component.'
			assert isinstance(self.x, int), f'Position x is not an integer for {self.__class__} component.'
			assert isinstance(self.y, int), f'Position y is not an integer for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Direction SOUTH (0,1) NORD (0,-1) WEST (-1,0) EAST (1,0)
		# Necessary for correct rendering of sprites and text boxes etc.
		self.direction = (0, 1)

		# Remember last possition, on collision return to the last known pos
		# Required for resolution of collisions with the map
		self.lastx = self.x
		self.lasty = self.y
		self.lastmap = self.map


class Teleport(Component):
	''' Entity is a teleport - i.e. on collision it changes position of
	the object that collided with the entity.

	Used by:
		-	CollisionTeleportProcessor
	'''

	__slots__ = ['dest_x', 'dest_y', 'dest_map']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Teleport component.

		Parameters:
			:param dest_x: X-axis position in pixels on the target map.
			:type dest_x: int

			:param dest_y: Y-axis position in pixels on the target map.
			:type dest_y: int

			:param dest_map: Name of the target map where entity is teleported.
			:type dest_map: str

			:param key: Entity representing key that is necessary to be in the inventory in order to teleport.
			:type key: str or int

			:raise: ValueError - in case mandatory parameters are missing.
		'''
	
		super().__init__()
		
		# Teleport destination - mandatory
		try:
			self.dest_map = kwargs.get('dest_map')
			self.dest_x = kwargs.get('dest_x')
			self.dest_y = kwargs.get('dest_y')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing')
			raise ValueError

		# Assert that targetmap exists in the global list of all initiated maps engine and position is integer
		try:
			assert self.dest_map in engine._maps.keys(), f'Destination map {self.dest_map} is not initialized for {self.__class__} component.'
			assert isinstance(self.dest_x, int), f'Position x is not an integer for {self.__class__} component.'
			assert isinstance(self.dest_y, int), f'Position y is not an integer for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError


		# Key for the teleport - no teleportation without key in inventory (entity) - optional
		teleport_key = kwargs.get('key', None)
		
		# Check that the key entity exists in global list of entities
		try:
			self.key = engine._entity_map.get(teleport_key) if isinstance(teleport_key, str) else teleport_key
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Key {teleport_key} is not present in list of entities.')
			raise ValueError


class Teleportable(Component):
	''' Entity is a teleportable - i.e. on collision with entity having
	Teleport component can be teleported.

	Used by:
		-	CollisionTeleportProcessor
	'''

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Teleportable component.
		'''
		super().__init__()


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

