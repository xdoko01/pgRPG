import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

import math # for calculation of square root move_to

import pygame.time # pygame.ime

########################################################
### Package init commands
########################################################

if not pygame.get_init(): pygame.init()

# TODO - commands for implementation
#	move to x,y
#	move to entity

def cmd_attack(*args, **kwargs):
	''' Pass whatever information you think are necessary for the command
	and let the command utilize them or not

	- Projectile
		- ttl
		- owner entity

	- Damaging
		- damage

	- Weapon
		- type
		- action - automatically filled
		- max_projectiles
		- projectiles collision zones (up, down, left, right)
		- damage
	
	- some Weapon entity
		-	Weapon
		-	RenderableModel

		---- in order to pick the weapon
		-	Position (optional)
		-	Collidable (optional)
		-	Pickable (optional)
		

				, RenderableModel
				- projectile - prepare projectiles - entities
				- {up: entity, down: entity, left: entity, right: entity}
				- components - Projectile, Collidable, Damaging (no position or position -100, -100)
				- max projectiles ... 1 on smashable, pikeable weapons, many on arrows
			 
	- HasWeapon - rename to CanAttack??

		- weapon, - read from weapon on init
					- action, - read from Weapon on init

		- has attacked - status - important for action animation

		- projectiles = []

		- method create_projectile (weapon on input, position component on input - in order to generate the correct position)
			- check if more projectiles can be created
			- read weapon
			- create new entity based on description in Weapon - Projectilem Collidable Position Damaging
			- add it into projectiles



					- projectile_dict = {up, down, left, right} - read from Weapon on init
						- Projectile
						- Collidable - from Weapon
						- Position - -100,-100
						- Damaging

					- projectiles_active = []
					
					- has_attacked

	- Attack command
		- call HasWeapon, create_projectile - here position is important

	- CollisionGenerator
		- should generate collisions with Projectiles - no change needed

	- CollisionProjectileProcessor
		- new processor that checks only Projectile, Collidable
		- if entity hit then adjust health component + remove Collidable component - hit was done and no more
					
	- ClearTemporaryEntityProcessor
		- new processor
		- iterate every projectile OR iterate HasWeapon.projectiles_active
			- check ttl on projectile and destroy it


					- tile to attack - how long the projectile exists

						- is created by action command - only if such entity does not exist
							- Projectile, just a tag
							- Position - based on position of character,s entity and character's collision zone
							- Collidable - take from weapon component
							- Damaging - how much healt is taken on collision with damageable component
						- is destroyed - after some period of time?
	- Action command
		- get HasWeapon, Position component
		- wet weapon component
		- check if projectile = None
			- if yes, check direction entity is facing - position.direction
			- take the projectile entity from weapon get(direction)
				-	get position component of projectile
				-	update it
				- assign it to HasWeapon


	'''
	# Get parameters for movement
	entity = kwargs.get("entity")
	
	# Get HasWeapon component
	# Check if has_weapon.projectile is None
	#	if yes, 
	#		
	# get HasWeapon component
	# get HasWeapon action
	# set status component of the entity to action

	# if HasWeapon component does not exist on entity then error is not raised
	try:
		# Get the HasWeapon component from the entity - TODO COllidable component must be optional
		has_weapon = engine.world.component_for_entity(entity, (components.HasWeapon))

		#position = engine.world.component_for_entity(entity, (components.Position))

		#collidable = engine.world.component_for_entity(entity, (components.Collidable))

		#state = engine.world.component_for_entity(entity, components.State)
		has_weapon.has_attacked = True

		#has_weapon.create_projectile(entity, position, collidable)
		# set status component of the entity to action
		#state.state = has_weapon.action

		print(f'Attack command successfully added. Entity {entity}')
		return 0

	except KeyError:
		print(f'Attack command error. Entity {entity}')
		return -1

def cmd_move_to(*args, **kwargs):
	''' Move to certain x,y position on the current map.
	Returns exception until the destination is reached. So it needs to be
	redirected to itself in order to repeat this command until destination is reached. 

	TODO - change direction not immediatelly but after some time or number of steps
	'''

	# Who (entity) needs to move
	entity = kwargs.get("entity")
	
	# Get the target coordinates
	tx = kwargs.get("x", None)
	ty = kwargs.get("y", None)

	# Get the coordinate of the entity and the target 
	position = engine.world.component_for_entity(entity, components.Position)
	motion = engine.world.component_for_entity(entity, components.Motion)

	sign = lambda x: 1 if x>0 else (-1 if x<0 else 0)

	# If the distance is close, close the gap and end
	if math.sqrt( (tx - position.x)**2 + (ty - position.y)**2 ) < 10:
		position.x = tx
		position.y = ty

		return 0
	
	# If gap is big, continue
	else:
		# Create movement so to minimise the distance between entity and the target
		if abs(tx - position.x) > abs(ty - position.y):
			# Close on x-axis
			cmd_move(entity=entity, dx=sign(tx - position.x) * 120)
		else:
			# Close on y-axis
			cmd_move(entity=entity, dy=sign(ty - position.y) * 120)			

		return -1

def cmd_disable_talk(*args, **kwargs):
	''' Finish speaking when global brain wants to run cinematics
	'''

	# Get entity to stop speaking
	talk_ent = kwargs.get("entity", None)

	# Get CanTalk component for the entity
	try:
		can_talk = engine.world.component_for_entity(talk_ent, components.CanTalk)

		# Set text to empty string
		can_talk.text = ''
		
		# Successful finished
		return 0

	except KeyError:
		
		# Entity does not have component CanTalk
		return -1

def cmd_set_quest_phase(*args, **kwargs):
	''' In the game cinematics processor, it may come to the point when I want to proceed
	to the next phase of the game.
	To enable that from global game cinematics processor, I can see 2 ways:
		-	I can invoke command that change the phase
		-	I can invoke event from the global brain command and let the quest to change the phase
	
	Let's go with the first option and see
	
	TODO - this is dirty - accessing engine quest dict directly
	'''

	# Get quest id and the new phase id
	quest = kwargs.get("quest", None)
	phase = kwargs.get("phase", None)	

	# Update the quest's phase
	try:
		engine._quests.get(quest, None).set_phase(phase)
		
		# Everything went smoothly
		return 0
	except:
		# Error occured
		return -1

def cmd_add_screen(*args, **kwargs):
	''' Input
		-	entity to which I want to add the screen
		-	screen parameters
	'''

	# Get entity of for the new screen
	focus_ent = kwargs.get("entity", None)

	# Get the Camera 
	screen_pos_x = kwargs.get("screen_pos_x", 0)
	screen_pos_y = kwargs.get("screen_pos_y", 0)
	screen_width = kwargs.get("screen_width", 300)
	screen_height = kwargs.get("screen_height", 300)

	# Create the camera
	engine.world.add_component(focus_ent, components.Camera(screen_pos_x=screen_pos_x, screen_pos_y=screen_pos_y, screen_width=screen_width, screen_height=screen_height))

	# Successful finished
	return 0

def cmd_remove_screen(*args, **kwargs):
	''' Input
		-	entity from which I want to remove the screen
		-	screen parameters
	'''

	# Get entity of for the new screen
	focus_ent = kwargs.get("entity", None)

	# Try to Remove the camera
	try:
	
		engine.world.remove_component(focus_ent, components.Camera(screen_pos_x=screen_pos_x, screen_pos_y=screen_pos_y, screen_width=screen_width, screen_height=screen_height))
	
		# Successfully removed
		return 0

	except KeyError:
		
		# entity or component does not exist
		return -1

def cmd_add_to_inventory(*args, **kwargs):
	''' Input
		-	receiver's entity
		-	item's entity
	'''

	# Get entity of the receiver and of the item
	receiver_ent = kwargs.get("entity", None)
	item_ent = kwargs.get("item", None)

	# First try to find value based on key in _entity_map. If nothing found, use item (integer)
	# If entity nod defined by integer, raise error
	item = kwargs.get("item", None)
	item_ent = engine._entity_map.get(item, item)
	assert(isinstance(item_ent, int), f'Entity {item} is not defined and/or must be an integer')
	
	# Get HasInventory component for receiver entity - if it has one
	try:
		has_inventory = engine.world.component_for_entity(receiver_ent, components.HasInventory)

		# If the item is passed, add it to the inventory
		if item_ent: has_inventory.inventory.append(item_ent)
		
		print(f'Entity {item_ent} successfully added to the inventory')
		# Successful finished
		return 0

	except KeyError:
		return -1

def cmd_remove_from_inventory(*args, **kwargs):
	''' Input
		-	giver's entity
		-	item's entity
	'''

	# Get entity of the giver and of the item
	giver_ent = kwargs.get("entity", None)
	item_ent = kwargs.get("item", None)

	# First try to find value based on key in _entity_map. If nothing found, use item (integer)
	# If entity nod defined by integer, raise error
	item = kwargs.get("item", None)
	item_ent = engine._entity_map.get(item, item)
	assert(isinstance(item_ent, int), f'Entity {item} is not defined and/or must be an integer')

	# Get HasInventory component for giver entity - if it has one
	try:
		has_inventory = engine.world.component_for_entity(giver_ent, components.HasInventory)

		# If the item is passed, remove it from the inventory
		if item_ent in has_inventory.inventory: 
			has_inventory.inventory.remove(item_ent)
		
		print(f'Entity {item_ent} successfully removed from the inventory')
		# Successful finished
		return 0

	except KeyError:
		return -1

def cmd_toggle_control(*args, **kwargs):
	''' Disable/enable any user input for given entity - used in cinematics so that 
	the user cannot break it with movements.

	Example (0,	commands.cmd_toggle_input, {"enable" : False})
	-	above disables user input on entity
	'''

	# Get entity whose brain we need to freeze from cmd parameters
	entity = kwargs.get("entity", None)

	# Get on/off control information - default is enabled
	toggle = kwargs.get("enable", True)

	# Get Cotrollable component for this entity - if it has one
	try:
		control = engine.world.component_for_entity(entity, components.Controllable)

		# Disable the brain
		control.enabled = toggle

		# Successful finished
		return 0

	except KeyError:
		return -1

def cmd_toggle_brain(*args, **kwargs):
	''' Stop/Start brain of given entity for the purposes of global game
	processor.

	This command should not have usually exception handling defined.
	Exception is thrown when component does not have Brain entity.

	'''

	# Get entity whose brain we need to freeze from cmd parameters
	entity = kwargs.get("entity", None)
	toggle = kwargs.get("enable", True)


	# Get brain component for this entity - if it has one
	try:
		brain = engine.world.component_for_entity(entity, components.Brain)

		# Disable the brain
		brain.enabled = toggle

		# Successful finished
		return 0

	except KeyError:
		return -1

def cmd_toggle_motion(*args, **kwargs):
	'''
	'''

	# Get entity whose motion we need to freeze from cmd parameters
	entity = kwargs.get("entity", None)
	toggle = kwargs.get("enable", True)


	# Get motion component for this entity - if it has one
	try:
		motion = engine.world.component_for_entity(entity, components.Motion)

		# Disable the motion
		motion.enabled = toggle

		# Successful finished
		return 0

	except KeyError:
		return -1

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

	# Read the pressed keys
	keys = pygame.key.get_pressed()	

	current_time = pygame.time.get_ticks()

	# time for every character to display
	d_char = time / len(text) if len(text) != 0 else 0

	# If text displayed long enough or SPACE is pressed then end
	if (current_time - brain.cmd_first_call_time >= time) or keys[pygame.K_SPACE]:
		
		# Text has been shown long enough - continue without exception and reset the text
		# in can_talk component (as a result it will not be drawn by the render function)
		can_talk.text = ''

		return 0
	else:
		# There is still some time to display the text - return exception

		# Only show for the first time it is called last_idx <> next_idx condition
		if brain.last_cmd_idx != brain.next_cmd_idx:
			can_talk.text = text
			(can_talk.text_surf, can_talk.text_rect) = can_talk.font_object.render(can_talk.text, (0,0,255), None)

		# Display text as animated effect
		# each character must be displayed time/length
		#char_to_show = (current_time - brain.cmd_first_call_time) // d_char

		#can_talk.text = text[:int(char_to_show)]
		#(can_talk.text_surf, can_talk.text_rect) = can_talk.font_object.render(can_talk.text, (0,0,255), None)

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

def cmd_wait_key(*args, **kwargs):
	''' Wait until key specified in parameter is pressed. Then continue.
	'''

	continue_key = kwargs.get("key", None)

	# Get the pressed key from global - CommandProcessor
	keys = pygame.key.get_pressed()
	if keys[pygame.K_SPACE]:
		return 0
	else:
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
	print(f'None command executed')
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
		# What if there are several commands in the queue for motion - like move 5x to the left?
		# In that case, what is written below will not work

		#motion.dx = dx if dx else motion.dx
		#motion.dy = dy if dy else motion.dy

		# This is more correct as it is not ignoring multiple movement commands for one entity
		motion.dx = motion.dx + dx if dx else motion.dx
		motion.dy = motion.dy + dy if dy else motion.dy

		return 0

	except KeyError:
		
		return -1

def cmd_disable_collision(*args, **kwargs):
	'''
	'''
	entity = kwargs.get("entity")
	engine.world.remove_component(entity, components.Collidable)		

def cmd_face_entity(*args, **kwargs):
	''' Change the direction of the entity so that it faces other entity.
	'''

	# Get the entity whose direction needs to be changed
	entity = kwargs.get("entity")
	
	# Get the entity towards the entity should face
	face_to = kwargs.get("face", None)

	face_ent = engine._entity_map.get(face_to, face_to)
	assert(isinstance(face_ent, int), f'Entity {face_ent} is not defined and/or must be an integer')

	# Sign function
	sign = lambda x: -1 if x<0 else (1 if x>0 else 0)

	try:
		# Get the Position component from the entity
		pos_entity = engine.world.component_for_entity(entity, components.Position)
		
		# Get the Position component from the Face to entity
		pos_face = engine.world.component_for_entity(face_ent, components.Position)
		
		# if possitive, pos_entity must face Right
		x_dir = pos_face.x - pos_entity.x
		# if positive, pos_entity must face Down
		y_dir = pos_face.y - pos_entity.y

		# turn left or right
		if abs(x_dir) > abs(y_dir):
			pos_entity.direction = (sign(x_dir), 0)
		# turn up or down
		else:
			pos_entity.direction = (0, sign(y_dir))

		# Direction successfully updated
		print(f'Face CMD: Direction of entity {entity} changed to {pos_entity.direction }')
		return 0

	except KeyError:
		
		# Error, direction not updated
		return -1

###
def get_cmd_fnc(cmd_str):
	''' Returns the function implementing command that is represented by the string.
	In case the command is not recognized, empty command is returned
	'''
	return CMD_DICT.get(cmd_str, cmd_none)

CMD_DICT = {
	'loop' : cmd_loop,
	'wait' : cmd_wait,
	'wait_key' : cmd_wait_key,
	'goto' : cmd_goto,
	'none' : cmd_none,
	#####
	'move_to' : cmd_move_to,
	#####
	'face_entity' : cmd_face_entity,
	'disable_talk' : cmd_disable_talk,
	'add_screen' : cmd_add_screen,
	'remove_screen' : cmd_remove_screen,
	'toggle_control' : cmd_toggle_control,
	'toggle_brain' : cmd_toggle_brain,
	'toggle_motion' : cmd_toggle_motion,
	'show_dialog' : cmd_show_dialog,
	'move' : cmd_move,
	'attack' : cmd_attack,
	'disable_collision' : cmd_disable_collision,
	'remove_from_inventory' : cmd_remove_from_inventory,
	'add_to_inventory' : cmd_add_to_inventory,
	'set_quest_phase' : cmd_set_quest_phase
}