''' Experiments with ECS

Requirements
	-	esper - https://github.com/benmoran56/esper

	Features
		-	Camera implemented
			- CameraProcessor updates camera offset based on position (Transform) of the entity that has Camera component
			- RenderProcessor iterates all entities with Camera component and draws the screen into Camera componet variable sceen that is blitted on the window.

		-	Teleports implemented
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
			- On the other end we need to step out of the ECS world due to Quests - 

		-	Quest event (simple) processing implemented
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
				- other functions



		-	Picking items implemented
			- very similar to Teleports implementation


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
				and can be moved independently from the player (Controllable component)

	- TODO 
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

		-	reimplement coordinates - floats

		-	Implement collision zones properly - position of the entity is the centre of the sprite
		-	Implement constatnt time in the main loop
		-	Implement diagonal movement
		-	Improve collision with the map
		-	Improve collision amongst entities
		-	Improve rendering speed 
'''

import core.engine

# Run the game
core.engine.main()