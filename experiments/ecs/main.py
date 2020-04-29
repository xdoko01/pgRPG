''' Experiments with ECS

Requirements
	-	esper - https://github.com/benmoran56/esper

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
			- Camera component is represented by separate game screen on the main game window where entity is in the centre of this screen
			- Render component facilitates correct updating of all camera screens
			- New screen can be dynamically added/removed by adding/removing camera component to any entity that I want
				- command that adds/removes Camera component to any entity must be called for that

		-	Scrolling implemented
			^^^^^^^^^^^^^^^^^^^^^
			- CameraProcessor updates camera offset based on position (Transform) of the entity that has Camera component
			- RenderProcessor iterates all entities with Camera component and draws the screen into Camera componet variable sceen that is blitted on the window.

		-	Teleports implemented
			^^^^^^^^^^^^^^^^^^^^^
			- 2 options
			
			- 1st option - remember collision entities on Colision components (list of entities with whom the entity has colided)
				- CollisionEntityGenerator processor records collision entities on Collision component
				- CollisionTeleport processor iterates all teleports and resolves collisions that are recorder on the collision component
				- CollisionCorrector processor resolves all the outstanding collisions that were not handled by Teleport and/or Item processor
			
			- 2nd option - generate and save collision event
				- CollisionEntityGenerator processor creates collision event and saves it to the collision queue (Global array)
				- CollisionTeleport processor consumes the event concerning teleport
				- CollisionCorrector processor consumes the rest
			
			- I prefer the first option as there is no need to step out of the ECS world
			- On the other end we need to step out of the ECS world due to Quests

		-	Quest event (simple) processing implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- New GameEventProcessor created. The processor takes as a parametr global (engine) function that is event handler
			- New processor is planned into the other processors
			- The engine handler function is called and takes the list of events and passes it to all quests
			- Each quest has event processor that processes the event based on conditions and actions
			- Those conditions and actions are specified in json file specifying the quest
			- Conditions can be specified in 3 ways that can be combined
				- by comparing the event.params to condition params
				- by evaluating python condition in form of the string
				- by executing function that returns boolean
			- Actions are specified as a list of functions
				- execute_function function can be used to invoke arbitrary python code or taking the code from file or other json element
				- modify_brain function - resets brain of any entity with commands from Command class
				- other functions - shake screen, fadein/fadeout, ...

		-	Picking items implemented
			^^^^^^^^^^^^^^^^^^^^^^^^^
			- very similar to Teleports implementation

		-	Global brain implemented (Global Script processor)
			^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			- It is implemented as just entity with just BRAIN component. 
			- Every command must have parameter entity specified because if it is not specified then the command is trying to be executed
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
			- First all engine global objects are put into the dictionary called game_state (command queue, event queue, maps, quests and ecs world)
			- pygame.Surface objects are not serializable, so before saving it was necessary to set every such reference to none (on both components
				and processors)
			- After saving those references must be refreshed in order to keep the game going - it is done using pre_save and post_load methods
				and the logic happens in save_game and load_game functions.
			- During the game, pressing F1 saves the game and pressing F2 loads the game

	- TODO

		-	clear and comment the 
		
		-	document - diagrams
			-	event processing
			-	command processing
			-	collision processing - whenever you move, use commands!!!


		-	command move to place, move to entity, search etc

		-	Implement pygame.math.Vector2 for all positions used in the game
		
		-	Show text command to have time parameter but also to disapear when space is pressed (or action key)

		-	Text buble aligment of the text (wrapping)

		-	Some command that will have the whole dialog on input as dictionary/list and will rule the whole conversation
	
		-	How to add some cinematics into teleportation? Fadeouts etc???

	- BUGS

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