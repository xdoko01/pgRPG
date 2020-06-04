''' Module containing all components
'''
import functools		# for cache decorator - Memoize RenderableModel class
import json				# necessary to parse json file with model
import ctypes			# to show number of references to an instance

import sys 				# for getting size of instance object and sys path
import pygame 			# for Camera component
import pygame.freetype 	# for CanTalk component

if __name__ != '__main__':
	import core.config.config as config  # For renderable component IMAGE_PATH
	import core.engine as engine # For checking the engine._entity_map - if component has entity as a str as a parameter (HasInventory) + engine._maps
	import core.models.model as model # For cached animated model in RenderableModel entity

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
	'Teleport', 'Teleportable', 'Motion', 'RenderableModel', 'State', 'Wearable',\
	'CanWear', \
	'Weapon', 'HasWeapon', 'Damageable', 'Damaging', 'Temporary', 'Container',\
	'Factory', 'LinearMotion']

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

	# Return entity and the new component
	return (entity, comp_inst)

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


class LinearMotion(Component):
	'''
	'''
	__slots__ = ['speed']

	def __init__(self, *args, **kwargs):
		'''
		'''
		super().__init__()
		
		# Change of position
		self.speed = kwargs.get('speed')

		# Assert that dx, dy are numbers
		try:
			assert isinstance(self.speed, int) or isinstance(self.dx, float), f'Movement speed is not a number for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError


class Factory(Component):
	'''
	- Factory component
		- prescription for the new entity
		- muze si pamatovat kolik muze vygenerovat entit
		- position of the new component??? doda funkce create entity HasWeapon
		- reference to projectile container??? doda funkce create entity HasWeapon
		- factory component by mohla mit metodu generate
		- vstupem pro uspesne vygenerovani musi byt pozice (volitelna) a kontainer(volitelny)

	{"type" : "Factory", "params" : {"prescription" : "arrow.json", "units" : 5}},

	'''

	__slots__ = ['prescription', 'units']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Factory component.
		'''
		super().__init__()

		# Either define prescription as a json text or as a json entity file
		self.prescription = kwargs.get('prescription')
		
		# Unlimited number of units in case no units passed in the argument
		self.units = kwargs.get('units', None) 
	
		try:
			assert isinstance(self.prescription, dict), f'Prescription must be in a form of dictionary'
			assert isinstance(self.units, int) or self.units == None, f'Units must be integer or None(unlimited)'
		except AssertionError:
			raise ValueError

	def create_entity(self, owner=None, pos=None, container=None, reg_at_engine=False):
		''' Create entity from the prescription dictionary
		'''
		# If we want to register generated entity on engine level, we need to generate
		# an uniq name for it.
		if reg_at_engine:
			id_str = f'{self.prescription.get("id", "")}OWN{owner}ORD{self.units}TS{pygame.time.get_ticks()}'
			self.prescription.update({"id": id_str})
		
		new_entity = engine._create_entity(
			self.prescription,
			
			# Do not register in engine global variable _entity_map - not needed
			register=reg_at_engine
		)

		# Add position component pos = (pos_x, pos_y, pos_dir, pos_map)
		if pos:
			(pos_x, pos_y, pos_dir, pos_map) = pos
			engine.world.add_component(new_entity, Position(x=pos_x, y=pos_y, dir=pos_dir, map=pos_map))
		
		# Add container component
		if container:
			engine.world.add_component(new_entity, Container(contained_in=container))

		return new_entity


class Container(Component):
	''' Component containing back reference to the
	master component.
	'''

	__slots__ = ['contained_in']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Container component.
		'''
		super().__init__()

		self.contained_in = kwargs.get("contained_in", None)


class Temporary(Component):
	''' Component that can be assigned to the entity that has
	limited timespan. After that entity disappears. For example, 
	projectile is temporary (arrow).
	'''

	__slots__ = ['ttl', 'creation_time']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Temporary component.
		'''
		super().__init__()

		# How long the entity with this components should live
		# default is 5 seconds.
		self.ttl = kwargs.get("ttl", 5000)

		# When was the component created - in order to determine 
		# destruction time
		self.creation_time = pygame.time.get_ticks()


class Damaging(Component):
	''' Entity containing this component is hurting 
	entities upon collision - for example projectile.
	'''

	__slots__ = ['damage']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the Damaging component.
		'''
		super().__init__()

		self.damage = kwargs.get("damage", 10)


class Damageable(Component):
	''' Entity has some health, i.e. is damageable 
	'''

	__slots__ = ['health']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the  Health component.
		'''
		super().__init__()

		self.health = kwargs.get("health", 100)


class Weapon(Component):
	''' Entity is a weapon if having this component.
	Weapon has its parameters determined by weapon type.
	'''

	WEAPONS = {
		'bow' : { 'action' : 'shoot', 'idle' : 'idle_shoot' },
		'spear' : { 'action' : 'stab', 'idle' : 'idle_stab' },
		'sword' : { 'action' : 'swing', 'idle' : 'idle_swing' },
		'spell' : { 'action' : 'cast', 'idle' : 'idle_cast' }
	}
 
	__slots__ = ['action', 'idle', 'type']

	def __init__(self, *args, **kwargs):

		super().__init__()

		# Read the weapon attributes
		try:

			# Weapon type
			self.type = kwargs.get('type')

			# Weapon animation for attack action
			self.action = Weapon.WEAPONS.get(self.type).get('action')
			
			# Weapon animation for idle action
			self.idle  = Weapon.WEAPONS.get(self.type).get('idle')
			
			# Weapon can generate max projectiles
			self.max_projectiles = kwargs.get('max_projectiles', 1)
			
			#self.projectile_collision_zones = kwargs.get('projectiles', {}).get('projectile_collision_zones', {})

			# Weapon causes damage - default 10 points
			#self.damage = kwargs.get('projectiles', {}).get('damage', 1)

			#self.projectile_ttl =  kwargs.get('projectiles', {}).get('ttl', 100)

			#self.projectile_speed =  kwargs.get('projectiles', {}).get('speed', 100)

		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that weapon type exists in list of WEAPONS
		try:
			assert isinstance(self.type, str) and self.type in Weapon.WEAPONS, f'Unknown weapon type "{self.type}" for {self.__class__} component.'
			assert isinstance(self.action, str) and self.action in model.Model.ACTIONS, f'Unknown animation action "{self.action}" for {self.__class__} component.'
			assert isinstance(self.idle, str) and self.action in model.Model.ACTIONS, f'Unknown idle animation "{self.idle}" for {self.__class__} component.'
			assert isinstance(self.max_projectiles, int), f'Max no. of projectiles must be an integer "{self.max_projectiles}" for {self.__class__} component.'
			#assert isinstance(self.damage, int), f' Damage must be an integer "{self.damage}" for {self.__class__} component.'
			#assert isinstance(self.projectile_ttl, int), f' Projectile ttl must be an integer "{self.projectile_ttl}" for {self.__class__} component.'
			#assert isinstance(self.projectile_speed, int), f' Projectile speed must be an integer "{self.projectile_speed}" for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError


class HasWeapon(Component):
	''' Entity can pickup and carry a Weapon 

	Used by:
		-	CollisionWeaponProcessor

	Tests:
		>>> c = HasWeapon()
	'''

	__slots__ = ['weapons', 'has_attacked', 'projectiles', 'weapon_in_use']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new HasWeapon component. 
		'''

		super().__init__()

		# By default component does not store any weapons
		default_weapons = {
			"sword" : {"weapon" : None, "generator" : None},
			"spear" : {"weapon" : None, "generator" : None},
			"bow" : {"weapon" : None, "generator" : None},
			"spell" : {"weapon" : None, "generator" : None}
		}

		# By default no weapon is selected
		self.weapon_in_use = kwargs.get('weapon_in_use', None)

		# Is set to True if attack action is in progress (command Attack was triggered)
		self.has_attacked = False

		try:
			# Join input parameters with default weapons
			self.weapons = { **default_weapons, **kwargs.get('weapons', {}) }

			# Translate the values (Weapon, generator) to Entity instance if necessary
			for w_key, w_value in self.weapons.items():
				
				# Translate entity id name to entity id number if needed
				weapon_ent = w_value.get('weapon')
				weapon_ent = engine._entity_map.get(weapon_ent) if isinstance(weapon_ent, str) else weapon_ent

				# Translate entity id name to entity id number if needed
				generator_ent = w_value.get('generator')
				generator_ent = engine._entity_map.get(generator_ent) if isinstance(generator_ent, str) else generator_ent

				# TODO - check that generator has factory component!!

				# Save the new values in weapons dictionary
				self.weapons.update({w_key : {"weapon" : weapon_ent, "generator" : generator_ent}})

			# Remember the projectiles - set of ints representing entities
			self.projectiles = set()

		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Problem with initiating a weapon for the entity')
			raise ValueError
	
	def set_weapon_in_use(self, type):
		''' Switches to weapon that is used
		'''
		self.weapon_in_use = type if type in self.weapons.keys() else None
	
	def get_weapon_in_use(self):
		''' Returns currently used weapon entity
		'''
		return self.weapons.get(self.weapon_in_use, {}).get('weapon', None)
	
	def get_generator_in_use(self):
		''' Returns currently used generator entity
		'''
		return self.weapons.get(self.weapon_in_use, {}).get('generator', None)

	def get_weapon_action_anim(self):
		''' Get the name of attack animation for the weapon that is currently 
		in possesion of the entity.
		'''
		# TODO - wouldnt it be easier to store action and idle action in weapons dictionary??
		return engine.world.component_for_entity(self.get_weapon_in_use(), Weapon).action
	
	def get_weapon_idle_anim(self):
		''' Get the name of idle animation for the weapon that is currently
		in possesion of the entity.
		'''
		return engine.world.component_for_entity(self.get_weapon_in_use(), Weapon).idle
	
	def remove_projectile(self, entity):
		''' Removes projectile from the list of projectiles
		that is implemented as a set.
		'''

		self.projectiles.remove(entity)
		print(f'Projectile {entity} deleted. List of projectiles {self.projectiles}')


	def create_projectile(self, owner_ent, pos_comp, coll_comp):
		''' Creates projectile - taking information from the generator of projectile - character entity position and collision
		closely coupled with GenerateProjectile processor
		'''
		
		# If no weapon ot generator do not create projectile
		try:
			# Get weapon component from the weapon
			weapon = engine.world.component_for_entity(self.get_weapon_in_use(), Weapon)
			factory = engine.world.component_for_entity(self.get_generator_in_use(), Factory)
		except KeyError:
			return None

		# Check if more projectiles can be created and continue, if yes
		if len(self.projectiles) < weapon.max_projectiles:
			
			# calculate position for the new projectile
			(ent_col_x, ent_col_y) = (coll_comp.x, coll_comp.y) if coll_comp else (0, 0)
			(pos_x, pos_y, pos_map) = (int(pos_comp.x + (pos_comp.direction[0] * (ent_col_x + 30))), int(pos_comp.y + (pos_comp.direction[1] * (ent_col_y + 30))), pos_comp.map)
			
			# Calculate collision zone for the new projectile - OBSOLETE - collision component is created by the factory
			#(col_x, col_y) = (weapon.projectile_collision_zones.get(pos_comp.dir_name)[0], weapon.projectile_collision_zones.get(pos_comp.dir_name)[1])

			# Create new entity for the new projectile - TODO the parameters of projectile need to be taken from the weapon
			#new_projectile = engine._create_entity(
			#	{
			#		"id" : "projectile_" + "owner_" + str(owner_ent),
			#		"components" : [
			#			{"type" : "Temporary", "params" : {"ttl" : 100}},
			#			{"type" : "Collidable", "params" : {"x" : col_x, "y" : col_y}},
			#			{"type" : "Position", "params" : {"x" : pos_x, "y" : pos_y, "map" : pos_map}},
			#			{"type" : "Damaging", "params" : {"damage" : 10}},
			#			{"type" : "Debug", "params" : {}},
			#			{"type" : "Container", "params" : {"contained_in" : self}} # reference to has_weapon instance
			#		]
			##	# Do not register in engine global variable _entity_map - not needed
			#	register=False)
			
			new_projectile = factory.create_entity(owner=owner_ent, pos=(pos_x, pos_y, pos_comp.dir_name, pos_map), container=self, reg_at_engine=False)

			# Increase count of active projectiles
			self.projectiles.add(new_projectile)
			print(f'Projectile {new_projectile} created. List of projectiles {self.projectiles}')
			
			return new_projectile


class Wearable(Component):
	''' Entity is wearable by other entity that has CanWear component

	Used by:
		-	CollisionWearableProcessor

	Tests:
		>>> c = Wearable()
	'''

	__slots__ = ['bodypart']

	BODYPARTS = ['head', 'hands', 'feet', 'belt', 'legs', 'torso']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Wearable component. Component has
		one arguments describing on which part of body the entity should be weared.
		'''

		super().__init__()

		# Read the bodypart
		try:
			self.bodypart = kwargs.get('bodypart')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that bodypart exists in list of BODYPARTS
		try:
			assert isinstance(self.bodypart, str) and self.bodypart in Wearable.BODYPARTS, f'Unknown bodypart "{self.bodypart}" for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError


class CanWear(Component):
	''' Entity can pickup and wear Wearable entities

	Used by:
		-	CollisionWearableProcessor

	Tests:
		>>> c = CanWear()
	'''

	__slots__ = ['wearables']

	BODYPARTS = ['head', 'hands', 'feet', 'belt', 'legs', 'torso']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new CanWear component. 
		'''

		super().__init__()

		# Initiate the wardrobe
		self.wearables = {
			'head' : None,
			'hands' : None,
			'feet' : None,
			'belt' : None,
			'legs' : None,
			'torso' : None
		}

		# Try to wear the entity
		try:
			for w_key, w_value in kwargs.items():
				
				# Translate the value (Wearable) to Entity instance if necessary
				wearable_entity = engine._entity_map.get(w_value) if isinstance(w_value, str) else w_value

				# If it is possible to wear the entity (known bodypart and empty slot for wearable) then wear it
				if w_key in CanWear.BODYPARTS and not self.wearables.get(w_key):
					self.wearables.update({w_key : wearable_entity})

		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Problem with wearing of the entity')
			raise ValueError


class Debug(Component):
	''' Display debug information on entities that are tagged by this component.

	Used by:
		-	RenderDebugProcessor
	
	Tests:
		>>> c = Debug()
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

	Tests:
		>>> c = Brain()
		>>> c.commands
		[]
		>>> c.enabled
		False
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

	Tests:
		>>> c = CanTalk()
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
		self.font = kwargs.get('font', config.FONT_PATH + 'FiraCode-Regular.ttf')
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

	Tests:
		>>> c = Labeled()
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

	Tests:
		>>> c = Pickable()
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

	Tests:
		>>> c = HasInventory()
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

# TODO - is self.direction necessary? is not enough dir_name?
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

	Tests:
		>>> c = Position()
	'''

	__slots__ = ['x', 'y', 'map', 'direction', 'dir_name']

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
			self.dir_name = kwargs.get('dir', 'down')
		except KeyError:
			# Notify component factory that initiation has failed
			print(f'Mandatory parameters are missing.')
			raise ValueError

		# Assert that map exists in the global list of all initiated maps engine
		try:
			assert self.map in engine._maps.keys(), f'Map {self.map} is not initialized for {self.__class__} component.'
			assert isinstance(self.x, int), f'Position x is not an integer for {self.__class__} component.'
			assert isinstance(self.y, int), f'Position y is not an integer for {self.__class__} component.'
			assert self.dir_name in ('up', 'down', 'left', 'right'), f'Position direction is not defined for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Direction SOUTH (0,1) NORD (0,-1) WEST (-1,0) EAST (1,0)
		# Necessary for correct rendering of sprites and text boxes etc.
		
		if self.dir_name == 'down': self.direction = (0, 1)
		if self.dir_name == 'up': self.direction = (0, -1)
		if self.dir_name == 'left': self.direction = (-1, 0)
		if self.dir_name == 'right': self.direction = (1, 0)

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

	Tests:
		>>> c = Teleport()
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

	Tests:
		>>> c = Teleportable()
	'''

	__slots__ = []

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Teleportable component.
		'''
		super().__init__()


class Motion(Component):
	'''	Entity can move.

	Used by:
		-	MovementProcessor

	Tests:
		>>> c = Motion()
	'''
	
	__slots__ = ['dx', 'dy', 'enabled', 'last_move']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Motion component.

		Parameters:
			:param dx: X-axis delta movement component.
			:type dx: float

			:param dy: Y-axis delta movement component.
			:type dy: float

			:raise: ValueError - in case movement params are not numbers.
		'''
		super().__init__()
		
		# Change of position
		self.dx = kwargs.get('dx', 0.0)
		self.dy = kwargs.get('dy', 0.0)

		# Assert that dx, dy are numbers
		try:
			assert isinstance(self.dx, int) or isinstance(self.dx, float), f'Movement dx is not a number for {self.__class__} component.'
			assert isinstance(self.dy, int) or isinstance(self.dy, float), f'Movement dy is not a number for {self.__class__} component.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Entity movement can be freezed by command - used in scripted cinematics
		self.enabled = True

		# Remember last move and if we have moved
		self.has_moved = False

		# Remember time when the entity last moved
		# Necessary to know when to reset the direction of the entity due to rendering
		self.last_move = pygame.time.get_ticks()


class Renderable(Component):
	''' Entity is displayable on the game screen.

	Used by:
		-	RenderWorldProcessor
		-	RenderDebugProcessor

	Tests:
		>>> c = Renderable()
	'''

	__slots__ = ['image', 'w', 'h', 'd_h', 'd_w']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Renderable component.

		Parameters:
			:param image_file: Name of the image stored in IMAGE_PATH directory, including suffix
			:type image_file: str

			:raise: ValueError - in case image file is not found
		'''

		super().__init__()

		# Image and its parameters
		try:
			self.image_file = kwargs.get("image", "")
			assert isinstance(self.image_file, str), f'Image file name {self.image_file} is not valid.'

			self.image = pygame.image.load(config.IMAGE_PATH + self.image_file).convert()
		except FileNotFoundError:
			print(f'Image file {config.IMAGE_PATH + self.image_file} not found')
			# Notify component factory that initiation has failed
			raise ValueError
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

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

		Parameters:
			:param pos: Position on the map in pixels.
			:type pos: tuple, list
			
			:return: Position of the topleft corner of the image as a tuple.
		'''
		return (pos[0] - self.d_w, pos[1] - self.d_h)

	def pre_save(self):
		''' Prepare component for saving - remove all nreferences to
		non-serializable objects
		'''
		self.image = None
		self.w = self.h = self.d_h = self.d_w = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		self.image = pygame.image.load(config.IMAGE_PATH + self.image_file).convert()
		
		self.w = self.image.get_width()
		self.h = self.image.get_height()
		
		self.d_w = self.w / 2
		self.d_h = self.h / 2		


class RenderableModel(Component):
	''' Entity is displayable as animated model on the game screen.

	Used by:
		-	RenderModelWorldProcessor

	Tests:
		>>> c = RenderableModel()
	'''

	__slots__ = ['model', 'last_frame', 'last_time', 'is_last_frame', 'action']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new RenderableModel component.

		Parameters:
			:param model_name: Name of the model stored in MODEL_PATH directory
			:type model_name: str

			:param action: Initial animated action of the model
			:type action: str
			
			:raise: ValueError - in case model file is not found or has problem
		'''

		super().__init__()

		# Get the model name
		model_file = kwargs.get('model', '')

		# Get the initial action of the model
		self.action = kwargs.get('action', 'default') 

		# Check the model name and the action name for validity
		try:
			assert isinstance(model_file, str), f'Model file name {model_file} is not valid.'
			assert isinstance(self.action, str) and self.action in model.Model.ACTIONS, f'Action "{self.action}" is not allowed animation.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Initiate new model
		try:
			self.model = model.Model(model_file)
		except:
			print(f'Something went wrong during initiation of the model {model_file}')
			# Notify component factory that initiation has failed
			raise ValueError

		# Time and frame must be remembered for animation
		self.last_frame = 0
		self.last_time = pygame.time.get_ticks()

		# In order to launch projectile, I need to know the last frame of animation
		self.is_last_frame = False

		print(self.model)

	def set_action(self, action):
		''' Check if action is supported and set it - reset the frame and time.
		If action is not supported then set action to 'default' action.
		'''
		# In case of non-supported action, change to default
		if action not in self.model.texture_actions: action = 'default'
		
		# In case of action change - reset the anim variables
		if action != self.action:
			self.action = action
			self.last_frame = 0
			self.last_time = pygame.time.get_ticks()

	def topleft(self, pos):
		''' Returns correction of coordinates to display the sprite correctly

		Parameters:
			:param pos: Position on the map in pixels.
			:type pos: tuple, list
			
			:return: Position of the topleft corner of the image as a tuple.
		'''
		return (pos[0] - self.model.d_w, pos[1] - self.model.d_h)

	def get_current_frame(self, direction, action=None, frame_id=None):
		''' Only get the frame, do not do any animation shifting
		In case frame does not exist, return empty frame.
		'''
		try:
			return self.model.texture_data.get(self.action if action is None else action).get(direction)[self.last_frame if frame_id is None else frame_id].get('tile')
		except:
			return self.model.no_tile
	
	def update_frame(self, direction):
		''' Update the animation of the model based on time 
		Just update the frame and that is it.
		'''

		# Get no of the animated frames for given action and direction
		anim_length = self.model.texture_length.get(self.action).get(direction)
		
		# Fix the last_frame so it is always within 0 .. anim_length
		#self.last_frame = self.last_frame % anim_length

		# Get dictionary describing the current frame
		curr_frame = self.model.texture_data.get(self.action).get(direction)[self.last_frame]

		# If action is animated - then shift based on time
		if self.model.texture_dynamic.get(self.action).get(direction):

			# Get the currect time and measure the delay from last_time
			current_time = pygame.time.get_ticks()
		
			# if delay is greater move to the next frame and reset timer
			if current_time - self.last_time > curr_frame.get('duration'):
				self.last_time = current_time
				self.last_frame = (self.last_frame + 1) % anim_length
				
				# Set the flag if animation is on the last frame. Important for emitting projectiles
				self.is_last_frame = True if self.last_frame == anim_length - 1 else False

			else: 
				# Set the flag to False, I want to have it True only once when the animation changes
				self.is_last_frame = False


	def get_frame(self, direction, action=None, frame_id=None):
		''' This is OBSOLETE function
			Get the current frame for display. It is taking into account animated frames.
		'''
		# Get length of the animation and use it for modulo on last_frame.
		# This is needed because if action/direction is changed, last frame can be bigger
		# than number of frames in the animation - hence causing error.
		# TODO - Alternativelly, reset last_frame to 0 with every change of direction/action
		#	- but where is the right place to do it??
		
		####### check that tile exists for given action, direction and frame
		
		## If action is not specified, use action from component
		if not action: action = self.action

		########
		# In case of particular frame (used with Wearables to be synchronized with animation)
		if frame_id:
			# In case that action / direction does not exist for the model, do nothing
			try:
				return self.model.texture_data.get(action, {}).get(direction, [])[frame_id].get('tile')
			except:
				return self.model.no_tile
		########

		try:
			# Get no of the animated frames for given action and direction
			anim_length = self.model.texture_length.get(action).get(direction)
			
			# Fix the last_frame so it is always within 0 .. anim_length
			self.last_frame = self.last_frame % anim_length

			# Get dictionary describing the current frame
			curr_frame = self.model.texture_data.get(action).get(direction)[self.last_frame]

			# If action is animated - then shift based on time
			if self.model.texture_dynamic.get(action).get(direction):

				# Get the currect time and measure the delay from last_time
				current_time = pygame.time.get_ticks()
			
				# if delay is greater move to the next frame and reset timer
				if current_time - self.last_time > curr_frame.get('duration'):
					self.last_time = current_time
					self.last_frame = (self.last_frame + 1) % anim_length
					
					# Set the flag if animation is on the last frame. Important for emitting projectiles
					self.is_last_frame = True if self.last_frame == anim_length - 1 else False

				else: 
					# Set the flag to False, I want to have it True only once when the animation changes
					self.is_last_frame = False

			return self.model.texture_data.get(action).get(direction)[self.last_frame].get('tile')
		except:
			return self.model.no_tile

	#def set_next_frame(self, action, direction):
	#	''' Set the next frame for animation '''
	#	self.last_time = pygame.time.get_ticks() 
	#	self.last_frame = (self.last_frame + 1) % self.model.texture_length.get(action).get(direction)

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects
		'''
		self.model = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		try:
			self.model = model.Model(self.model_file)
		except:
			raise ValueError	


class Controllable(Component):
	''' Entity can be controlled by the keyboard commands.

	Used by:
		-	InputProcessor

	Tests:
		>>> c = Controllable()
	'''

	__slots__ = ['control_keys', 'enabled', 'control_cmds']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Controllable component.

		Parameters:
			:param control_keys: Dictionary containing mapping 
				of movement and action keys to keyboard keys
			:type control_keys: dict

			:param control_cmds: Dictionary containing mapping
				of movement and action keys to commands
			:type control_cmds: dict

			:raise: ValueError - in case of incorrect keys/commands definition

		'''
		super().__init__()

		# Possibility to disable input for the global processor
		self.enabled = True

		# Control keys definition - keyboard arrows + 'z' key for attack
		default_keys = {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122}
		control_keys = kwargs.get("control_keys", default_keys)

		# Control commands definition
		default_cmds = { 'left' : 'move', 'right': 'move', 'up' : 'move', 'down' : 'move', 'attack' : 'attack'}
		control_cmds = kwargs.get("control_cmds", default_cmds)

		try:
			assert isinstance(control_keys, dict), f'Control keys must be passed in a form of dictionary.'
			assert isinstance(control_cmds, dict), f'Control cmds must be passed in a form of dictionary.'

			# Does control_keys dictionary contain at least one valid key key?
			assert bool(set(default_keys.keys()).intersection(set(control_keys.keys()))), f'Control keys are not properly defined'

			# Does control_cmds dictionary contain at least one valid command key?
			assert bool(set(default_cmds.keys()).intersection(set(control_cmds.keys()))), f'Control commands are not properly defined'

		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Merge defaults with defined
		self.control_keys = {**default_keys, **control_keys}

		# Merge defaults with defined
		self.control_cmds = {**default_cmds, **control_cmds}


class Collidable(Component):
	''' Entity collides with other collidable entities.

	Used by:
		-	RenderDebugProcessor
		-	CollisionMapProcessor
		-	CollisionEntityGeneratorProcessor
		-	CollisionTeleportProcessor
		-	CollisionItemProcessor
		-	CollisionEntityProcessor
		-	CollisionCorrectorProcessor	

	Tests:
		>>> c = Collidable()
	'''

	__slots__ = ['x', 'y', 'collision_events']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Collidable component.

		Parameters:
			:param x: X-axis collision zone +- from the x-centre of the entity in pixel coordinates
			:type x: int

			:param y: Y-axis collision zone +- from the y-centre of the entity in pixel coordinates
			:type y: int

			:raise: ValueError - in case of incorrect collision borders
		'''

		super().__init__()
		
		# With and height of the collision zone - from the center +/-x and +/-y
		self.x = kwargs.get('x', 0)
		self.y = kwargs.get('y', 0)

		try:
			assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as positive int.'
			assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as positive int.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError		

		# Keep track with whom the entity collided
		self.collision_events = set()


class Camera(Component):
	''' Entity is in focus of a camera that is displayed in form of a screen
	in the game window.

	Used by:
		-	UpdateCameraOffsetProcessor
		-	CollisionItemProcessor
		-	RenderMapProcessor
		-	RenderWorldProcessor
		-	RenderDebugProcessor
		-	RenderMapProcessorFullScan (OBSOLETE)

	Tests:
		>>> c = Camera()
	'''

	__slots__ = ['always_centre', 'map_screen_rect', 'offset_x', 'offset_y', 'screen_pos_x', 'screen_pos_y' \
				'screen_width', 'screen_height', 'screen_width_half', 'screen_height_half','screen']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new Camera component.

		Parameters:
			:param screen_pos_x: X-axis position of the topleft screen corner in the game window.
			:type screen_pos_x: int

			:param screen_pos_y: Y-axis position of the topleft screen corner in the game window.
			:type screen_pos_y: int

			:param screen_width: Width of the screen window.
			:type screen_height: Height of the screen window.

			:raise: ValueError - in case of incorrect screen window parameters.
		'''
		
		super().__init__()
		
		# Rectancle (top-left and bottom-right positions in pixels) of the map that is displayed on
		# camera.screen surface. It is used for rendering of map on the screen. Rectancle is calculated
		# by the UpdateCameraOffsetProcessor.
		self.map_screen_rect = (0,0,0,0)

		# Offset variables necessary for camera functionality - Offset is calculated by the 
		# UpdateCameraOffsetProcessor
		self.offset_x = 0
		self.offset_y = 0

		# Should the camera be always centered on the entity - default is False 
		# If False then camera stops centering when entity is close to map edges
		self.always_center = kwargs.get('always_center', False)

		# Topleft position of the Camera screen
		self.screen_pos_x = kwargs.get('screen_pos_x', 0)
		self.screen_pos_y = kwargs.get('screen_pos_y', 0)

		# Width and height of the Camera screen
		self.screen_width = kwargs.get('screen_width', 100)
		self.screen_height = kwargs.get('screen_height', 100)

		# Check the parameters for correctness
		try:
			assert isinstance(self.always_center, bool), f'Incorrect camera mode parameter - {self.always_center}.'

			assert isinstance(self.screen_pos_x, int) and self.screen_pos_x >= 0, f'Incorrect position of the camera screen window - {self.screen_pos_x}.'
			assert isinstance(self.screen_pos_y, int) and self.screen_pos_y >= 0, f'Incorrect position of the camera screen window - {self.screen_pos_y}.'

			assert isinstance(self.screen_width, int) and self.screen_width > 0, f'Incorrect width of the camera screen window - {self.screen_width}.'
			assert isinstance(self.screen_height, int) and self.screen_height > 0, f'Incorrect height of the camera screen window - {self.screen_height}.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Half of width and height is precalculated to avoid repetitive calculations /2
		self.screen_width_half = int(round(self.screen_width / 2))
		self.screen_height_half = int(round(self.screen_height / 2))

		# Camera screen surface on which map is blitted
		self.screen = pygame.Surface((self.screen_width, self.screen_height))
	
	def apply(self, pos=(0,0)):
		''' Applying camera offset to some position. Returns new position
		of the object and hence enables scrolling effect.

		Parameters:
			:param pos: Position on which camera offset will be applied
			:type pos: tuple
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

########################################################
### Not Used anymore
########################################################

class State(Component):
	''' Represent state of the entity
	idle, walk, attack, ...
	'''

	__slots__ = ['state']

	STATES = ['idle', 'walk', 'idle_stab', 'idle_swing']

	def __init__(self, *args, **kwargs):
		''' Initiate State component

		Parameters:
			:param state: State of the entity (default = idle)
			:type state: str

			:raise: ValueError - in case state is not defined/allowed
		'''
		
		try:
			self.state = kwargs.get('state', 'idle') 
			assert isinstance(self.state, str) and self.state in State.STATES, f'State {self.state} is not allowed state'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

########################################################
### For Standalone execution
########################################################

if __name__ == '__main__':
	
	# Test the module
	from doctest import testmod
	testmod()
	print(f'Tests finished')
