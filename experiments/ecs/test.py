''' Experiments with ECS

Requirements
	-	esper - https://github.com/benmoran56/esper

Features and TODOs

	-	First simple one screen, no scrolling objects
	-	Can Camera be implemented as entity or as a component?
	-	Can map tile be implemented as an entity?
		-	Tile can have Transform (position) and Renderable (sprite) Components
		-	Some tiles can have COllision component
		-	RenderProcessor can look for entity that has Camera Component
			-	based on position of Entity with Camera component then
				-	put on screen all renderable components that fit on the screen
				-	to speed up cache all entities on the map into 2D field upon every movement change?

	Notes
		-	I want to achieve 4 players with 4 screens in the window, each screen running different map
			-	map and its properties is outside ECS
				-	collision data
				-	tileset data
			-	screen is defined fully in Camera component. i.e. Camera is screen
			-	RenderProcessor
				-	reads the Transform entity - which contains Map ID
				-	reads the Camera entity - which contains information about the screen
				-	based on map data + transform position + screen data draws the scene
			-	Camera component can be together with Transform component in other than Player entity
				and can be moved independently from the player (Input component)

	- TODO 
		-	How to implement teleportation
		-	How to implement Quests
		-	How to implement sending and receiving events
		-	How to implement Cutscenes
		
		-	reimplement coordinates - floats

	#############################################################################################
	Entity
		-	 Instead, an entity is a unique ID, and all components that make up an entity 
		will be tagged with that ID. The entity is an implicit aggregation of the components 
		tagged with its ID.

		-	Rock (Position, Sprite)
		-	Crate (Position, Sprite, Health)
		-	Sign (Position, Sprite, Text)
		-	Ball (Position, Velocity, Physics, Sprite)
		-	Enemy (Position, Velocity, Sprite, Character, Input, AI)
		-	Player (Position, Velocity, Sprite, Character, Input, Player)

	Components
		-	TRANSFORM - Has a position in the world
			-	world position (x,y)
		-	MOTION - Can move (velocity, acceleration)
			-	velocity, acceleration
		-	SPRITE - Should display on screen
			-	file to use spreadsheet, sprite
		-	COLLISION - Colides with other objects
			-	size of collision box
		-	HEALTH - Has health, can take damage
			-	current health, max health
		-	FOLLOW - Controll, should follow another enity
			-	who to follow (entity)
		-	JOYSTICK (INPUT) - Control - should move based on arrow keys
			-	key information
		-	AI - 
			-	boolean doLeft, doRight, doShoot, ...

		Movement (Position, Velocity) - Adds velocity to position
		Gravity (Velocity) - Accelerates velocity due to gravity
		Render (Position, Sprite) - Draws sprites
		PlayerControl (Input, Player) - Sets the player-controlled entity's input according to a controller.  Adding an empty Player component will tag the entity for the PlayerControl system so that the Input data will be populated based on controller inputs.
		BotControl (Input, AI) - Sets a bot-controlled entity's input according to an AI agent
		
	Component managers
		-	merge components of the same type together due to performace (memory position)
		-	https://medium.com/@savas/nomad-game-engine-part-2-ecs-9132829188e5

	Systems(Processors)
		-	MOVEMENT SYSTEM
			-	TRANSFORM + MOTION - Updates position based on velocity
		-	INPUT SYSTEM
			-	JOYSTICK + MOTION - Changes velocity based on arrow keys pressed
		-	COLLISION SYSTEM
			-	COLLISION + TRANSFORM - Checks for collisions and resolves them
		-	FOLLOW SYSTEM
			-	TRANSFORM + MOTION + FOLLOW - Changes velocity based on where player is
		-	RENDER SYSTEM
			-	TRANSFORM + SPRITE - Render the sprite on the screen
		-----------
		-	GAME LOGIC?
			-Player sends I am here by calling SendMessage
'''
import esper
import pygame
import random
import time
import math

########################################################
### Components
########################################################

class Component:
	def __init__(self):
		pass


class Transform(Component):
	''' TRANSFORM - Has a position in the world
			- world position (x,y)
	'''
	def __init__(self, x=0.0, y=0.0):
		''' Coordinates are map coordinates, i.e. 1,1 means top left corner of the cell 
		in second column and second row.
		'''
		super().__init__()
		# Map coordinates
		self.x = x
		self.y = y
		#
		self.cell_x, self.map_x = math.modf(x) 
		self.cell_y, self.map_y = math.modf(y)
		self.map_x = int(self.map_x)
		self.map_y = int(self.map_y)
		#
		self.lastx = None
		self.lasty = None


class Motion(Component):
	'''	MOTION - Can move (velocity, acceleration)
			-	velocity, acceleration
	'''

	def __init__(self, x=0.0, y=0.0):
		super().__init__()
		self.x = x
		self.y = y
		# Remember last move and if we have moved
		self.lastx = None
		self.lasty = None
		self.has_moved = False


class Renderable(Component):
	''' SPRITE - Should display on screen
			-	file to use spreadsheet, sprite
	'''

	def __init__(self, image):
		super().__init__()
		self.image = image
		self.w = image.get_width()
		self.h = image.get_height()


class Health(Component):
	''' HEALTH - Has health, can take damage
			-	current health, max health
	'''

	def __init__(self):
		super().__init__()
		self.hp = 100


class Follow(Component):
	''' FOLLOW - Controll, should follow another enity
			-	who to follow (entity)
	'''
	def __init__(self, entity_to_follow):
		super().__init__()
		self.entity_to_follow = entity_to_follow


class Input(Component):
	''' JOYSTICK (INPUT) - Control - should move based on arrow keys
			-	key information
	'''

	def __init__(self, control_keys={}):
		super().__init__()
		
		default_keys = {
			"left" : 276,
			"right": 275,
			"up" : 273,
			"down" : 274
		}
		
		self.control_keys = {**default_keys, **control_keys}
	

class Collision(Component):
	''' COLLISION - Colides with other objects
			-	size of collision box
	'''
	def __init__(self, x, y):
		super().__init__()
		self.x = x
		self.y = y


class Brain(Component):

	def __init__(self, fr, to):
		super().__init__()
		self.fr = fr
		self.to = to 


class Camera(Component):

	def __init__(self):
		super().__init__()

class Command:
	def __init__(self):
		super().__init__()
		self.attack = False
		self.defend = True


class Projectile:
	def __init__(self):
		super().__init__()
		self.size = 10
		self.lifespan = 100



########################################################
### Systems / Processors
########################################################

class MovementProcessor(esper.Processor):
	''' MOVEMENT SYSTEM
			-	TRANSFORM + MOTION - Updates position based on velocity
	'''
	def __init__(self, minx, maxx, miny, maxy):
		super().__init__()
		self.minx = minx
		self.maxx = maxx
		self.miny = miny
		self.maxy = maxy

	def process(self, *args, **kwargs):

		# This will iterate over every Entity that has BOTH of these components:
		for ent, (transform, motion) in self.world.get_components(Transform, Motion):
			# Save last position
			transform.lastx = transform.x
			transform.lasty = transform.y
			# Update the Renderable Component's position by it's Velocity:
			transform.x += motion.x
			transform.y += motion.y
			# Recalculate map and cell positions
			transform.cell_x, transform.map_x = math.modf(transform.x) 
			transform.cell_y, transform.map_y = math.modf(transform.y)
			transform.map_x = int(transform.map_x)
			transform.map_y = int(transform.map_y)

			# An example of keeping the position inside screen boundaries. Basically,
			# adjust the position back inside screen boundaries if it tries to go outside:
			transform.x = max(self.minx, transform.x)
			transform.y = max(self.miny, transform.y)
			transform.x = min(self.maxx, transform.x)
			transform.y = min(self.maxy, transform.y)
			# Save info if entity has moved True/False
			transform.has_moved = ((transform.lastx != transform.x) or (transform.lasty != transform.y))
			print(f'New position:[{transform.x}, {transform.y}]')

class RenderProcessor(esper.Processor):
	''' RENDER SYSTEM
			-	TRANSFORM + RENDERABLE - Render the sprite on the screen	
	'''

	def __init__(self, window, tile_res=64, clear_color=(0, 0, 0)):
		super().__init__()
		self.window = window
		self.clear_color = clear_color
		self.tile_res = tile_res
		self.camera_pos = None

	def process(self, *args, **kwargs):

		# Clear the window:
		self.window.fill(self.clear_color)

		
		# Find the entity with Camera and use its position - 
		for ent, (camera, _) in self.world.get_components(Transform, Camera):
			self.camera_pos = camera


		# Imagine that your entity is in the centre of the screen and decide which tiles to display
		# On which tile is the camera
		#camera_tile_pos_x = transform.map_x
		#camera_tile_pos_y = transform.map_y

		# Calculate what part of map is relevant to generate on the screen. It
		# is calculated based on player's position on the map and the constant
		# that defines maximal number of cells that can be displayed on the
		# screen based on screen dimensions and cell dimensions (pixelPerStep).
		minScreenMapY = int(self.camera_pos.map_y - 3)
		maxScreenMapY = int(self.camera_pos.map_y + 3)
		minScreenMapX = int(self.camera_pos.map_x - 3)
		maxScreenMapX = int(self.camera_pos.map_x + 3)

		print(f'{minScreenMapY} {maxScreenMapY} {minScreenMapX} {maxScreenMapX}')
		print(f'Camera pos:[{self.camera_pos.x}, {self.camera_pos.y}]')
		# Correct the ranges so that only Cells defined by the map are iterated
		#if minScreenMapY < 0: minScreenMapY = 0
		#if maxScreenMapY > self.mapHeight: maxScreenMapY = self.mapHeight
		#if minScreenMapX < 0: minScreenMapX = 0
		#if maxScreenMapX > self.mapWidth: maxScreenMapX = self.mapWidth

		# Take 3 tiles up down left right and generate them
		# This will iterate over every Entity that has this Component, and blit it:
		for ent, (renderable, transform) in self.world.get_components(Renderable, Transform):

			# Stupid - take the closest tiles
			if (maxScreenMapX > transform.map_x > minScreenMapX and
				maxScreenMapY > transform.map_y > minScreenMapY):

				# Top left corner pixel position of the Map Cell j,i
				scrMapX = round( (400)
					- ( self.camera_pos.cell_x
						* self.tile_res
					)
					+ ( (transform.map_x - self.camera_pos.map_x)
						* self.tile_res
					)
					)

				scrMapY = round( (400)
					- ( self.camera_pos.cell_y
						* self.tile_res
					)
					+ ( (transform.map_y - self.camera_pos.map_y)
						* self.tile_res
					)
					)

				#print(f'Map:[{transform.map_x}, {transform.map_y}]. Screen:[{scrMapX}, {scrMapY}]')
				self.window.blit(renderable.image, (scrMapX, scrMapY))


class InputProcessor(esper.Processor):
	''' INPUT SYSTEM
			-	INPUT + MOTION - Changes velocity based on arrow keys pressed
	'''

	def __init__(self):
		super().__init__()
		#self.key_events = key_events

	def process(self, *args, **kwargs):
		
		# Extract events from parameter kwargs
		events = kwargs.get('events',[])

		# Get all entities that are waiting for the input and can move
		for ent, (inp, motion) in self.world.get_components(Input, Motion):

			# For each entity check if control keys were pressed and move them accordingly
			for event in events: #pygame.event.get():

				if event.type == pygame.KEYDOWN:
					
					# Move up
					if event.key == inp.control_keys.get('up'):
						motion.y = -0.1

					# Move down
					elif event.key == inp.control_keys.get('down'):
						motion.y = 0.1

					# Move left
					elif event.key == inp.control_keys.get('left'):
						motion.x = -0.1

					# Move right
					elif event.key == inp.control_keys.get('right'):
						motion.x = 0.1
				
				elif event.type == pygame.KEYUP:

					if event.key in (inp.control_keys.get('up'), inp.control_keys.get('down')):
						motion.y = 0
					elif event.key in (inp.control_keys.get('left'), inp.control_keys.get('right')):
						motion.x = 0


class CollisionProcessor(esper.Processor):
	''' -	COLLISION SYSTEM
			Checks for collisions and resolves them
			-	COLLISION + MOTION - Only entities that has moved are checked for collision
			-	COLLISION + TRANSFORM - Above entities are checked against Collision and Transform.
	'''
	COLLISION_TYPES = ['ALL']

	def __init__(self, collision_type='ALL'):
		super().__init__()
		self.collision_type = collision_type if collision_type in CollisionProcessor.COLLISION_TYPES else 'ALL'
		
	def process(self, *args, **kwargs):
		
		if self.collision_type == 'ALL':

			start_time = time.time()
			# Get all entities that have Motion and Collision (only those can activelly hit something) - i.e. that could have moved and iterate those
			for ent_moved, (coll_moved, trans_moved) in self.world.get_components(Collision, Transform):
				# Compare that all collision + transform entities - DUMMY WAY
				for ent_other, (coll_other, trans_other) in self.world.get_components(Collision, Transform):
					
					# Heuristic no.-1 - Test only those that have Motion component
					#if not self.world.has_component(ent_moved, Motion): continue

					# Heuristic no.0 - Test only those that have moved component
					#if not self.world.component_for_entity(ent_moved, Motion).has_moved: continue

					# Heuristic no.1 - Skip if testing itself
					if ent_moved == ent_other: continue

					# Heuristic no.2 - Test only those in close distance
					#if abs(trans_moved.x - trans_other.y) > 200 or abs(trans_moved.y - trans_other.y) > 200: continue 

					# Heuristic no.3 - Do not test twice the same double of entities, i.e. 1,3 and 3,1
					
					# AABB comaprison
					if(trans_moved.x - coll_moved.x < trans_other.x + coll_other.x and
						trans_moved.x + coll_moved.x > trans_other.x - coll_other.x and
						trans_moved.y - coll_moved.y < trans_other.y + coll_other.y and
						trans_moved.y + coll_moved.y > trans_other.y - coll_other.y):
						
						# Fix position for the entity that has moved
						trans_moved.x = trans_moved.lastx
						trans_moved.y = trans_moved.lasty
						#print(f'Collision between {ent_moved} and {ent_other}')

			end_time = time.time()
			duration = end_time - start_time
			print(f'Collision type: {self.collision_type}')
			print('Duration: %1.10f ' % duration)


class BrainProcessor(esper.Processor):

	def __init__(self):
		super().__init__()

	def process(self, *args, **kwargs):
		for ent, (transform, motion, brain) in self.world.get_components(Transform, Motion, Brain):
			motion.x = random.randint(brain.fr, brain.to)
			motion.y = random.randint(brain.fr, brain.to)

########################################################
### Main program
########################################################

def run():

	# Initialize Pygame stuff
	pygame.init()
	window = pygame.display.set_mode((850,850))
	pygame.display.set_caption("Esper Pygame example")
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1, 1)

	#####
	# Initialize Esper world
	#####
	world = esper.World()

	#####
	# Initiate entities with components
	#####

	# Define map ground floor
	map_ground_layer = [
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
	]

	# Define map walls
	map_wall_layer = [
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
	]

	# Create Map Ground floor entites
	for i in range(len(map_ground_layer)): # Y - coordinate
		for j in range(len(map_ground_layer[0])): # X - coordinate
			if map_ground_layer[i][j] != 0:
				ground_tile = world.create_entity()	# just plain integer ID
				world.add_component(ground_tile, Transform(x=j+0.5, y=i+0.5))
				#world.add_component(static_tile, Motion(x=0, y=0))
				#world.add_component(static_tile, Input(control_keys={'up': pygame.K_w, 'down' : pygame.K_s, 'left' : pygame.K_a, 'right' : pygame.K_d}))
				world.add_component(ground_tile, Renderable(image=pygame.image.load("experiments/ecs/images/ground_tile.png")))
				#world.add_component(static_tile, Collision(32,32))
				#world.add_component(static_tile, Brain(-1,1))
				map_ground_layer[i][j] = ground_tile

	# Create Map Wall floor entites
	for i in range(len(map_wall_layer)): # Y - coordinate
		for j in range(len(map_wall_layer[0])): # X - coordinate
			if map_wall_layer[i][j] != 0:
				wall_tile = world.create_entity()	# just plain integer ID
				world.add_component(wall_tile, Transform(x=j+0.5, y=i+0.5))
				#world.add_component(static_tile, Motion(x=0, y=0))
				#world.add_component(static_tile, Input(control_keys={'up': pygame.K_w, 'down' : pygame.K_s, 'left' : pygame.K_a, 'right' : pygame.K_d}))
				world.add_component(wall_tile, Renderable(image=pygame.image.load("experiments/ecs/images/wall_tile.png")))
				world.add_component(wall_tile, Collision(0.5,0.5))
				#world.add_component(static_tile, Brain(-1,1))
				map_wall_layer[i][j] = wall_tile

	# Create player entity that can move
	player= world.create_entity()
	world.add_component(player, Transform(x=5.5, y=5.5))	# Player has position in the world
	world.add_component(player, Motion(x=0, y=0))	# Player can move, hence can have velocity that will change based on key inputs
	world.add_component(player, Input(control_keys={}))	# Player can be managed by pressing keys
	world.add_component(player, Renderable(image=pygame.image.load("experiments/ecs/redsquare.png"))) # Player has sprite
	world.add_component(player, Collision(0.5,0.5))
	world.add_component(player, Camera())

	#####
	# Initiate System processors
	#####
	
	# Movement processor updates entity position based on the velocity 
	movement_processor = MovementProcessor(minx=0, maxx=30, miny=0, maxy=30)

	# Render processor to place renderable entities with position on the screen
	render_processor = RenderProcessor(window=window)

	# Input processor to process keys pressed
	input_processor = InputProcessor()

	# Collision processor
	collision_processor = CollisionProcessor()

	# Brain processor
	# brain_processor = BrainProcessor()
	

	#world.add_processor(brain_processor)
	world.add_processor(input_processor)
	world.add_processor(movement_processor)
	world.add_processor(collision_processor)
	world.add_processor(render_processor)

	#####
	# The main loop
	#####
	running = True
	while running:

		# Read the keys pressed, mouse, win resize etc.
		key_events = pygame.event.get()

		# Check for End Game
		for event in key_events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

		# Update all the processors, pass key events as a parameter
		# Parameter will be passed to all processors. Those who want it
		# will process it.
		world.process(events=key_events)

		# Flip the framebuffers
		pygame.display.update()

		# Keep game at 30 FPS
		clock.tick(30)

if __name__ == "__main__":
	run()
	pygame.quit()