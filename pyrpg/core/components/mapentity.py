''' pyrpg/pyrpg/core/components/mapentity.py
'''

import ctypes # to show number of references to an instance

import pygame.time # Necessary for pygame.time.get_ticks()

# load and store config dict as cfg.config
# here necessary for loading paths
import pyrpg.constants.config as cfg 

import pyrpg.core.engine as engine

from pyrpg.core.components.assets import TileModel, EntityModel
#from assets import Assets # Necessary for calling Assets for getting model data
#from engine import Engine # Necessary for work with Engine.maps and ENgine.screens and calling of Engine.send_event

class MapEntity:

	def __init__(self, model_type):
		""" Initiate all variables common for map entities - map, position and
		model specifying all texture parameters and collision information common
		for given MapEntity type.
		"""

		# Instance specific
		self.id = None
		self.map = None
		self.pos = None
		self.name = None
		self.state = 'default'				# State defines the status if the Item - move left, move right, etc...
		self.quests = []

		self._last_frame = 0
		self._last_time = pygame.time.get_ticks()
		
		# Type specific - it is cached in class EntityModel
		self.model = EntityModel(cfg.config.get('paths').get('model_path'), model_type + '.json')

	def setup(self, params={}):
		""" Setup the empty instance by data provided in the dictionary params.
		Put MapEntity to the requested map and position.
		"""
		self.id = params.get('id', None)
		self.map = params.get('map', None)
		self.pos = params.get('pos', None)
		self.name = params.get('name', None)
		self.state = params.get('state', 'default')

	def update(self):
		""" Update is managing situation when MapEntity does something PROACTIVELLY
		without external impulse. For example memory execution, arrows update, ...
		Also reading the input from keyboard can be done here!
		"""
		pass

	def on_interact(self, source, nature):
		""" On_interact is managing situation when item REACTS to some external
		action (specified in nature). For example somebody wants to talk to the
		MapEntity or attack it.
		"""
		pass

	def clear_resources (self):
		self.unregister_model()
		self.unregister_map() # this also deletes from Map.entities dictionary
		self.unregister_screen()


	def unregister_model(self):
		""" Throw away reference to Model and references to inventory, wearables, 
		arrows etc.
		"""
		self.model = None


	def register_map(self):
		""" Register the entity at the map whose map_id is stored in self.map
		"""
		# Register only if MapEntity is placed on some map
		if self.map is not None:
			map_ref = engine.maps.get(self.map)
			map_ref.register_entity(self)

	def unregister_map(self):
		""" Register the entity at the map whose map_id is stored in self.map
		"""
		# Unregister only if MapEntity is placed on some map
		if self.map is not None:
			map_ref = Engine.maps.get(self.map)
			map_ref.unregister_entity(self)

	def register_screen(self, screen_id):
		""" Register the entity at the screen with screen_id
		"""
		# Register only if MapEntity is owner of some screen
		if screen_id != '':
			
			assert(screen_id in engine.screens)		
			engine.screens.get(screen_id).register_entity(self)

	def unregister_screen(self, screen_id):
		""" Unregister the entity at the screen with screen_id
		"""		
		pass

	def send_event(self, event):
		""" Method generates event and invokes EventDispatcher (Engine class)
		for distributoi of this event to relevant event handlers (quests, maps,
		screens, ...)
		"""
		Engine.send_event(event)

	def get_frame(self):
		""" Return the current frame for draw function based on state. In case that
		state is dynamic, it checks time that passed since last frame. In case that
		state is static, it returns current frame in sequence.
		This call is used in draw function. In move function we will proactively change
		the frame forward
		"""
		
		# Get information about current action of the cell
		state_frames = self.model.tex_length.get(self.state)
		state_dynamic = self.model.tex_dyn.get(self.state)

		# Get the delay time on the current frame
		current_frame = self.model.tex.get(self.state)[_last_frame]
		frame_delay = current_frame.get('duration')
		
		# If delay (current time - last time) is greater than duration of the frame, 
		# then change the frame
		if (pygame.time.get_ticks() - self._last_time > frame_delay) and frame_delay > 0:
			
			# Remember time of change
			self._last_time = current_time

			# Shift to the next frame
			if self._last_frame == state_frames: self._last_frame = 0
			else: self._last_frame += 1

		# Return frame that needs to be shown
		return self._last_frame

	def move(self, move_vector):
		"""
		1/	Set the proper State based on move vector - move_up, move_down, move_left, move_right.
			If no proper state exists, use default state.
		2/	Set the last frame - if state is static then shift to the next frame, otherwise do nothing
		3/	Calculate new position on the map. 
				Check if wall is hit and compensate. - call some function ()
				Check if other MapEntity is hit abd compensate. - call on_interaction('walk')

		this function incorporates set_walk_action, get_next_frame and more
		"""

	def draw(self, map_screen, mode='2D_PLAIN'):
		""" Draw entity on the map_screen plane.
		"""
		pass

	def __str__(self, level=0):
		
		tabs = '\t' * level
		
		return f'{tabs}*Instance of {self.__class__.__name__} ({hex(id(self))}) [{ctypes.c_long.from_address(id(self)).value}]:\n\
				{tabs}\tId:\t\t({hex(id(self.id))}) [{ctypes.c_long.from_address(id(self.id)).value}]:\t{self.id}\n\
				{tabs}\tName:\t\t({hex(id(self.name))}) [{ctypes.c_long.from_address(id(self.name)).value}]:\t{self.name}\n\
				{tabs}\tPos:\t\t({hex(id(self.pos))}) [{ctypes.c_long.from_address(id(self.pos)).value}]:\t{self.pos}\n\
				{tabs}\tMap:\t\t({hex(id(self.map))}) [{ctypes.c_long.from_address(id(self.map)).value}]:\t{self.map}\n\
				{tabs}\tModel detail:\t\t{self.model.__str__(level+1)}\n'


class Item(MapEntity):
	
	def __init__(self, model_type):

		# Initiate, model, id, map, name and position
		super().__init__(model_type)

	def setup(self, params={}):

		# Initiate id, pos, map, name from dictionary
		super().setup(params)		

	def unregister_model(self):
		""" Throw away reference to Model and references to inventory, wearables, 
		arrows etc.
		"""
		super().clear_resources()		


class Wearable(Item):
	
	# List of wearable types. Other are not possible
	types = ['head','torso','legs','hands','boots','weapon','arrow']

	def __init__(self, model_type):

		# Initiate, model, id, map, name, action and position
		super().__init__(model_type)

	def setup(self, params={}):
		# Initiate id, pos, map, name from dictionary
		super().setup(params)	

	def unregister_model(self):
		""" Throw away reference to Model and references to inventory, wearables, 
		arrows etc.
		"""
		super().clear_resources()		


class Projectile(Item):
	pass


class Teleport(Item):
	pass


class Character(MapEntity):
	
	def __init__(self, model_type):

		# Initiate, model, id, map, name, action and position
		super().__init__(model_type)

		# Inventory - contain items and wearable is newly an item. Newly should be dictionary
		self.inventory = {
			'head' : None,
			'torso': None,
			'legs' : None,
			'hands' : None,
			'boots' : None,
			'weapon' : None,
			'arrow' : None,
			'projectile' : None,
 			'other' : []
		}

		# Characters scripting memory
		self.memory = None

	def setup(self, params={}):

		# Initiate id, pos, map, name from dictionary
		super().setup(params)	

		# Fill inventory with items and wearables
		for inv_key, inv_value in params.get('inventory', {}).items():

			# Wearable items
			if inv_key in Wearable.types:
				# Extract the type of wearable
				wear_type = inv_value.get('type')
				# Create Wearable object
				inv_obj = Wearable(wear_type)
				# Check that it is weared on correct place
				if inv_obj.model.wear_type != inv_key:
					raise ValueError('Specified wear type does not match model.wear_type')
				# Assign necessary instance parameters like ID
				inv_obj.setup(inv_value)
				# Put the wearable into the inventory
				self.inventory.update( { inv_key : inv_obj } )

			# Normal inventory
			elif inv_key == 'other':
				# Iterate the list of dictionaries
				oth_inv = []
				for item in inv_value:
					# Extract the type of the item
					item_type = item.get('type')
					# Create item object
					inv_obj = Item(item_type)
					# Assign necessary instance parameters like ID
					inv_obj.setup(item)
					# Put the new item into the inventory
					oth_inv.append(inv_obj)
				# Update the inventory
				self.inventory.update({ 'other' : oth_inv })


		# Create new memory with data from the list
		# self.memory = Memory(self, params.get('memory', []))

	def unregister_model(self):
		""" Throw away reference to Model and references to inventory, wearables, 
		arrows etc.
		"""
		super().clear_resources()	

		self.inventory = None
		self.memory = None


class Player(Character):
	
	def update(self):
		""" Read the keyboard here in this function. Same as in original Game!
		Reading of keyboard does not need to be in the main loop!!
		"""
		pass