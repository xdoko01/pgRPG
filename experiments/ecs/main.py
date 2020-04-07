''' Experiments with ECS

Requirements
	-	esper - https://github.com/benmoran56/esper

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


	- TODO 
		-	Simple quest
			^^^^^^^^^^^^
			- Scenario overview
				- Player hits NPC
				- Player and NPC have linear conversation
				- At the end of the conversation NPC gives item to the player (key)
				- NPC waits until task is done
				- Using the key, player can enter to the other map

			- Scenario tech details
				- Player hits NPC (NPC has key item in the inventory)
					- define collision event between player and NPC
				- Player and NPC have linear conversation
				- At the end of the conversation NPC gives item to the player (key)
					- collision event triggers following actions
						- Fill GlobalBrain with following commands
							- Stop Brain processing to both Player and NPC (cmd_disable_brain)
							- Stop Controlls to the PLAYER and NPC (cmd_toggle_control)
							- Show text bubble to Player - 'HI, do jou have some job for me?'
							- Wait for any key
							- Show text buble to NPC - 'Sure, I need to get rid of those bloody rats.'
							- Wait for any key
							- Show text bubble to Player - 'No, problem. Where can I find them?'
							- Wait for any key
							- Show text buble to NPC - 'They are in the cellar. Here is the key'
							- Wait for any key
							- NPC gives item to Player(Key) (cmd_add_to_inventory, cmd_remove_to_inventory)
							- Show text buble to Player - 'Thanks.'
							- Wait for any key
							- Add camera component to the NPC (cmd_add_screen)
							- Resume Brain processing for Player and NPC (cmd_enable_brain)
							- Resume Controlls to the Player and NPC (cmd_toggle_control)
				- NPC waits until task is done
					- change quest phase from 1 to 2 (cmd_set_quest_phase)
					- collision event definition (if collision with NPC and phase = 2)
						- Fill GlobalBrain with following commands
							- Stop Brain processing to both Player and NPC (cmd_disable_brain)
							- Stop Controlls to the PLAYER and NPC (cmd_toggle_control)
							- Show text bubble to Player - 'Hi, its harder than I though'
							- Wait for any key
							- Show text buble to NPC - 'Go on, finish them all'
							- Wait for any key
							- Resume Brain processing for Player and NPC (cmd_enable_brain)
							- Resume Controlls to the Player and NPC (cmd_toggle_control)
				- Using the key, player can enter to the other map
					- collision event with teleport - condition is that Player has the key 






		-	Implement global brain - entity that can rule everyhting in the world using
			commands.
			- It can be entity with just BRAIN component. But every command must have parameter
			entity specified because if it is not specified then the command is trying to be executed
			on the source entity (which does not make sence for the global Script processor)
		

		-	How to implement translation from entity_id to game_id in quest event processing

		-	How to implement showing conversation between characters and the player
			- player hits the character
			- character stops
			- player pops a message (Get out of my way)
			- player cannot move when the message is displayed
			- message is displayed for 5 seconds or until space is pressed
			- after that character pops a message (Mind your own business)
			- message is displayed for 5 seconds or until space is pressed
			- both player and character can move now
			------------------------------------------
			- hit event reaction
			- function to prevent movement and function to enable movement (parameter in Input component. When disabled, space is enabled)
			- function for displaying message based on TRANS of the entity - create temp component text message (CanSpeak) with texts to speak??? Yes.
				- by doing this way, I only adjust render function to take into account CanSpeak ...
			- 5 sec delay or space - delay can be in CanSpeak component or must be govern by event actions - display text -> wait or space -> display text
			

		-	How to implement that global cinematics script processor - i.e. player is out of control, just watching and pressing space on text dialogs
		-	How to implement dialog and then adding some new item to the inventory of the player
		-	How to implement that teleport works only 3 times and then it stops working.
		

		-	How to implement Quests
		-	How to implement Cutscenes
		-	How to add some cinematics into teleportation? Fadeouts etc???

		
		-	Improve speed
		-	Implement comand to stop and wait for specific key to press
		-	Move speed implement as a parameter of some processor
		-	Implement pygame.math.Vector2 for all positions used in the game
		-	Implement tile_res=64 as a parameter of render processor for all (defaut 64)
		-	Improve collision with the map
		-	Improve collision amongst entities
		-	Improve rendering speed 
'''

import core.engine

# Run the game
core.engine.main()