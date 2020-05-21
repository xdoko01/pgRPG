''' Experiments with ECS

Requirements
	-	esper - https://github.com/benmoran56/esper
	-	pytmx - https://github.com/bitcraft/PyTMX


	Solved situations
		-	Q: 	How to implement translation from entity_id to game_id in quest event processing?
			A: 	Keeping dictionary of entity names and entity ids on Engine module level.

		-	Q: 	How to fix moving into collision zone even if both entities have collision set?
			A: 	All movement (even corrective movements after collision) must be implemented as move command
				and pushed into command queue. Otherwise, by correction using lastx, lasty etc. entity will get stuck
				eventually.

	Features
		-	Architecture Design implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- Maps and Quests are out of esper.world
			- Maps and quests are accessed from Processors that have engine function as a input parameter
			  i.e. they know how to call outside the esper.world

			  - event handling - is achieved by calling to engine functions from esper.world processors
			  - command handling - is achieved by calling to engine functions from esper.world processors

		-	Multiple game screens implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- entity can have Camera component assign
			- Camera component is represented by separate game screen on the main game window
				where entity is in the centre of this screen
			- Render component facilitates correct updating of all camera screens
			- New screen can be dynamically added/removed by adding/removing camera component
				to any entity that I want
				- command that adds/removes Camera component to any entity must be called for that

		-	Scrolling implemented
			^^^^^^^^^^^^^^^^^^^^^
			- CameraProcessor updates camera offset based on position (Position component) of
				the entity that has Camera component
			- RenderProcessor iterates all entities with Camera component and draws the screen
				into Camera componet variable sceen that is blitted on the window.

		-	Teleports implemented
			^^^^^^^^^^^^^^^^^^^^^
			- 2 options

			- 1st option - remember collision entities on Colision components
				(list of entities with whom the entity has colided)
				- CollisionEntityGenerator processor records collision entities on
					Collision component
				- CollisionTeleport processor iterates all teleports and resolves collisions
					that are recorder on the collision component
				- CollisionCorrector processor resolves all the outstanding collisions that
					were not handled by Teleport and/or Item processor

			- 2nd option - generate and save collision event
				- CollisionEntityGenerator processor creates collision event and saves
					it to the collision queue (Global array)
				- CollisionTeleport processor consumes the event concerning teleport
				- CollisionCorrector processor consumes the rest

			- I prefer the first option as there is no need to step out of the ECS world
			- On the other end we need to step out of the ECS world due to Quests

		-	Quest event (simple) processing implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- New GameEventProcessor created. The processor takes as a parametr
				global (engine) function that is event handler
			- New processor is planned into the other processors
			- The engine handler function is called and takes the list of events and passes it to all quests
			- Each quest has event processor that processes the event based on conditions and actions
			- Those conditions and actions are specified in json file specifying the quest
			- Conditions can be specified in 3 ways that can be combined
				- by comparing the event.params to condition params
				- by evaluating python condition in form of the string
				- by executing function that returns boolean
			- Actions are specified as a list of functions
				- execute_function function can be used to invoke arbitrary python
					code or taking the code from file or other json element
				- modify_brain function - resets brain of any entity with commands from Command class
				- other functions - shake screen, fadein/fadeout, ...

		-	Picking items implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^
			- very similar to Teleports implementation

		-	Global brain implemented (Global Script processor)
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- It is implemented as just entity with just BRAIN component.
			- Every command must have parameter entity specified because if it is not
				specified then the command is trying to be executed
			on the source entity (which does not make sence for the global Script processor)

		-	Simple quest implemented
			^^^^^^^^^^^^^^^^^^^^^^^^
			- Scenario overview
				- Player hits NPC
				- Player and NPC have linear conversation
				- At the end of the conversation NPC gives item to the player (key)
				- NPC waits until task is done
				- Using the key, player can enter to the other map - teleport with the key

		-	Save and Load game implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- Using pickle library
			- First all engine global objects are put into the dictionary called
				game_state (command queue, event queue, maps, quests and ecs world)
			- pygame.Surface objects are not serializable, so before saving it was
				necessary to set every such reference to none (on both components and processors)
			- After saving those references must be refreshed in order to keep the game
				going - it is done using pre_save and post_load methods and the logic happens
				in save_game and load_game functions.
			- During the game, pressing F1 saves the game and pressing F2 loads the game

		-	Animated Characters implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- new component RenderableModel - substitution of static comp. Renderable
				- using new Model class that reads json tileset from Tiled sw
			- new processor RenderableModelWorldProcessor - substitution of RenderableWorldProcessor
			- new Status component
				- needed to represent different statuses for different animations - 'idle', 'walk', ...
			- new StatusProcessor processor
				- needed to correctly set the status for rendered animation character
				- uses motion.has_moved flag for setting up idle or walk status

		-	Processing only entities that are visible on the screen implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- filter function filter_only_visible
				- function is filtering based on position component x, y vars and
				camera screen rectancle. Entities that have position out of this
				camera rectancle are not being drawn.

		-	Picking up and Wearing clothes implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- new component Wearable - identification of wearable object
				- typically wearable object will also have RenderableModel, Pickable, Collidable components
				- component specifies bodypart to which it should be weared
			- new component CanWear - if entity can wear wearable component
				- component contains dictionary of entities that are weared
			- new processor CollisionWearableProcessor
				- must be planned before CollisionItemProcessor - first try to wear the item
					(CanWear mandatory), then pick it up as regular item
				- wearing item generates new event that can be scripted in quest - WEARABLE_WEARED
			- adjustment of processor RenderModelWorldProcessor
				- added check if entity has CanWear component and if yes - rendering the clothes



	- TODO
		
		- problem with last frame is not triggering the flar is caused that the flag is generated by get_frame and this is called
			once for every camera - i.e. in one run of the RenderModel world processor, several frames can be skipped.
		- fix by changing frame on every RenderableModel only once for all cameras.
		- REDO!!!
			- new RenderWorld processor????
			- BETTER Additional processor that changes the frame and ADJUSTED RenderWorld processor only takes the frame as it is with no shifting?
					- new function get_current_frame ... only returns the right picture from model dictionary
					- new function update_frame ... only sets last_frame and last time to the correct values based on time
				- this is ok but we need to implement new function that just returns image based on current values of last_frame, direction and action and no shifting done
				- this new processor must only shift frames on visible entities to spare processor time
					-	after camera offset update
					-	iterate cameras
						- for every renderable model on camera do the change and remember that the change has been done
						- do not repeat the change (call get_frame again) on those that were already changed
						

		- what is quicker - component_for_entity vs. try_entity

		- Weapon should contain prescription of how the projectile for the given weapon looks like - i.e. what components
			we need to create the projectile with.

		- Projectiles component that will act as a container for  projectile entities and nothing more?
			-	entity would need to have HasWeapon + Projectiles - make sense to have this probably only in HasWeapon component
		
		- HasWeapon having projectiles = Container ... new class that will contain list of entities, having add entity and remove entity
			functions??? Component ContainedIn can then refer to Container...

		- projectiles are generated only when second character is on the screen???? weird

		- why are sometimes generated and sometimes not?

		- why is the damage so big?

		- analyse possibilities of Container component

		- problem, Renderable model is staying on the last frame of action animation more then one cycle, hence generating multiple collision zones
		that are colliding with each other and causing processor load.

		- problem that is_last_frame is set to true after processor that generates the projectile. Then until the whole cycle is finished

		- Attack button pressed
		- Attack command
			- HasWeapon.has_attacked = True
		- RenderableModelState changed
			- to swing
			- has_attacked = False
		- RenderableModelGenerate
			- draws swing sprite while button is pressed - when released start from scratch
		
		- creating many projectiles instead of a few

		- GenerateProjectile processor
			- check last_frame - RenderableModel, HasWeapon, Position
				- last_frame = current frame and action is action
				- has_weapon. max number of projectiles 
				- create Projectile as temporary entity - position needed
					Temporary, Collidable, Damaging, FiredFrom (hasEntity component)

		- ClearTemporaryEntities processor


		- I need to generate entity when animation is on the last frame and keep it alive for some time
		- How to know that I am on the last frame?
		-------------------------------

		- if weapon is placed on position then display default action ...
			- get_frame ... if direction is empty then direction is down
			- if action is empty then action = default
			- get_frame(action=default) ... same as get_frame action=default, direction = down

		- document modification of esper - try_component .qq..


		- how to implement action button
			- new component Weapon - identification of weapon entity
				- Weapon will have renderableModel, Pickable, COllidable
				- component specifies type of the weapon (bow, pike, sword, magic)
				- component specifies the action corresponding to the weapon
					- bow ... action = shoot (up, left, down, right)
					- spear ... action = stab (up, left, down, right)
					- sword ... action = swing (up, left, down, right)
					- spell ... action = cast (up, left, down, right)
			- new component HasWeapon - if entity can pick up a weapon
				- component contains the weapon entity
			- new component CollisionWeaponProcessor
				- must be planned before CollisionWearableProcessor - first to try to take weapon
					if weapon already present, pik it as item to the inventory
				- picking up weapon generates new action WEAPON EQUIPED
			- adjustment of processor RenderModelWorldProcessor
				- added check if entity has HasWeapon component, if yes - render the weapon
			- HOW TO HIT THE ENEMY
				- action command
					- set HasWeapon.has_attacked = True
					- in State processor set state to swing or other attack state + reset has_attacked
				- Damageable component
					{"type" : "Damageable", "params" : {"health" : 100}},
				- Weapon
					- should have collision zone that extends character collision zone
				- if Attack 
					- enhance collision zone in the direction in the attack command
						- Collidable component change based on weapon component
						- Collision Weapon generator processor generates collision event
							- check all that HasWeapon
								- for each calculate new collision zone based on
									- position direction
									- collidable collision
									- weapon collision
									- has_weapon - has_attacked
							- check against all Damageable, position
							- in case of hit ...

						- Collision Entity processor
				- alternatively, create new entity representing projectile - swing
					- position is depending on parent entity position
					- collidable dependent on weapon
					- new component damaging
					- facing right, pushin attack button
						- new projectile entity is generated on the right side of the character
						- later it is destroyed again
						- Collision generator will notify the hit
						- New collisionProjectileProcessor will generate event and change healt and everything.
				- HasWeapon
					- weapon, action
					- projectile - entity that represents swing, arrow
						- is created by action command - only if such entity does not exist
							- Projectile, just a tag
							- Position - based on position of character,s entity and character's collision zone
							- Collidable - take from weapon component
							- Damaging - how much healt is taken on collision with damageable component
						- is destroyed - after some period of time?


				- New collision weapon processor
					- take components that have HasWeapon component
						- that have has_attacked = True


		- Controllable component - pass it also parameters of commands, currently those are filled in Input processor which is not
		flexible enough. If I want to map different command than move, it will not work

		- properly support default action if no other action exist in model - or have idle/down on all models????? or default/down???
			- if frame is not found, use default/down??

		- nice textboxes

		- every processor in separate file + create processors package

		- move to command - change so that it finds the way in graph, remembers the path and then follows the path
		
		- create graph from collision map on map init

		- initiate processors from json file not hardcoded

		- rewrite model
			- one set of pictures - so that one picture can be used by many animations
			- substitute default by idle
			- how to implement that some entity has all idle up down left right the same picture?
				- can I do this directly in Tiled - many properties
				- or just use default as a value if no idle is found<<
				
		- implement speed into the motion component - friendly NPCs should be slower than the player

		- fix save and load, probably some processors have problem

		- what is the FPS drop with anim. characters?
			- change processors and disable status processor and measure

		- fix problem - not changing position when face command is executed

		-	clear and comment
			- use private variable prefixes
			- use __slots__

		- how much memory is used by the map??
		- Render debug is slowing down the performance by circa 10 FPS

		- Speed
			- HW sprites? no,
			- Helps reducing bitdepht from 32 to 16
				window = pygame.display.set_mode((850,850), 0, 16)

			rename _entity_map to entity_map or mapping, it is global so it should not start by _

		-	implement animated entities

		-	implement in game windows for load and save game for example or inventory

		-	command move to place, move to entity, search etc

		-	Implement pygame.math.Vector2 for all positions used in the game
		
		-	Show text command to have time parameter but also to disapear when space is pressed (or action key)

		-	Text buble aligment of the text (wrapping)

		-	Some command that will have the whole dialog on input as dictionary/list and will rule the whole conversation
	
		-	How to add some cinematics into teleportation? Fadeouts etc???

	- BUGS

		-	Fix colision correction movement - now it is moving strangelly into the side
		-	Fix teleportation into the collision zone - it is impossible to move in this situation


	- IMPROVE

		-	Improve speed
		-	Implement comand to stop and wait for specific key to press
		-	Improve collision with the map
		-	Improve collision amongst entities
		-	Improve rendering speed
'''

import core.engine

# Run the game
core.engine.main()