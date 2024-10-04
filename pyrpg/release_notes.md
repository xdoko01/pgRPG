### advantages and disadvantages of using events in behavioral tree definition
  1. Using events
    - Pros
      - easier and leaner behavior tree
      - do_paralel having only 2 commands, one checking the change on the blackboard and other for actual behavior
      - can define in processors how many cycles should be skipped for processing the events, hence can tune the performance
    - Cons
      - cannot use blackboard values in handlers definitions (^ character is only evaluated for commands in command manager)
      - more text to write
      - additional processors for event handling
  
  2. Using custom test commands
    - Pros
      - less text
      - can use blackboard values everywhere
      - no additional processors
    - Cons
      - complicated do_parallel command having many commands inside
      - must implement many test commands instead of just processing the event


### 2024-06-28 First prototype of behavior tree using events to modify the Brain's blackboard value
  - Now, the behavior of the NPC can be changed upon receiving the event. For that to happen, handler for that event must be defined to change the blackboard value of the NPC's brain. NPC's brain must contain tests that are checking the blackboard value for changes and processor for handling the needed events must be set. Example of such scene is `guard_and_fight_back_if_ambushed_using_events.jsonc`.
  - The definition of such behavior is more complicated, but it is more universal and does not require specific commands for specific tests.

### 2024-06-25 Handlers now can be defined as a part of component parameters
  - To make the definition of handlers more readable, it is now possible to include handlers deinition also into the component `params` dictionary. It is good to have event handlers defined on the same place as `BrainAI` definition so that the behavior tree and event handlers that are modifying the blackboard are in the same place in quest specification.

### 2024-06-25 New get_coll_value function to search values in the collection
  - The function is located in `pyrpg.functions.dict_utils` package and is capable of returning values from collections as an generator.
  - It was developed to facilitate getting and loading handlers from different places in the quest definition (used in `engine` module).

### 2024-06-21 New test_damaged and test_can_see commands inplemented
  - the `test_can_see` commands is using the `CanSee` entity for getting the list of entities in sight. If there is desired entity in sight (command parameter) then the command succeeds. Can be used in behavior tree inside the `do_parallel` command to check for enemies during movements and consequent attack or running away - check also the test quest `guard_and_attack_on_sight`.
  - the `test_damaged` command is using `FlagWasDamagedBy` to determine if the entity was damaged and by whom. The attacking entity can be stored on the blackboard and further use in the brain logic. Check aslo the test quests `test_damaged` and `guard_and_fight_back_if_ambushed`

### 2024-06-07 New test_bb_value and log commands implemented
  - the `test_bb_value` command lets you test the content of the global blackboard using the json expression such as `["!=", ["VAR", "target_ent"], 0]` (if the value target_ent on the blackboard differs from 0 (true) then return `SUCCESS`. Else, return `FAILURE`)
  - the `log` command simply puts any text on the console output. It is usefull when debugging a command generators

### 2024-06-07 New do_parallel command that enables parallel execution of multiple commands
  - Newly, there is the new `do_parallel` command that can take definition of many commands as the argument and the mapping of results to expected result.

### 2024-05-17 Commands can use path finding that is distributed in several game cycles
  - Newly, there is a new `PathfindManager` that registeres all the requests for calculation of some path, gathers all the requests in a queue and calculates the paths in organized way. It can be for example set, that only specified amount of path search cycles can be performed within one game cycle in order to avoid freezing of game due to large calculations.
  - Newly, there is new processor in the `CommandSystem` called `PerformPathfindingCalculationProcessor`. This processor invokes `continue_search` method of the `PathfindManager` and hence calculates part of the paths.
  - Newly, commands can request calculation of the path (typically in their `init` part) and ask in the `process` part whether path calculation is finished or is still running. Once it is finished, they can use it. CHeck the `move_to` command implementation for an example.

### 2023-09-30 Fixed usage of aliases in all quest definitions
  - Previously, it was not possible to use alias in the quest file definition, if the entity representing this alias was not yet created (was defined lower in the quest file than in was used).
  - Newly, alias can be used anywhere in the quest file. Even if the entity is defined last in the quest file, it can be referenced by the entity that is defined first in the quest file.

### 2023-09-07 Commands and Command Generators Redone
  - Newly, logic can be defined by `btree` or `blist`. Commands can be used in both structures. Both structures follow `CommandGenerator` prototype. In future, no problem to add more structures that will follow `CommandGenerator` prototype.
  - Newly, `Command` namedtuple consists of `name`,`params` and `entity_id` attribtes. Those 3 attributes reflect the information from the `quest` definition. Specifically, `entity_id` marks the optional parameter specified in the quest on which entity the command must be executed. It is hence possible for the player entity to issue commands (for example via `Controllable` Component) to other entity such as NPC. Useful for global brain entity that can issue commands to different entities and hence orchestrate the action in the game.
  - Newly, all commands have as a parameter `Command`, `CommandContext` blackboard and `ECSmanager` that contains functions for manipulating the game world.

### 2023-05-05 New Argument for Processors - step
  - Newly, the processor does not need to run every time. There is new optional parameter `step` (by default set to `1`) that marks the frequency of processor execution. (1 means every cycle, 2 means every second cycle, 5 means every 5th cycle).
  - This might become handy, if the processor is resource heavy and does not need to run real-time. For example, processor for checking if the entity has reached the destination position
  - Example of processor definition: `["position_system.perform_check_on_target_position_processor:PerformCheckOnTargetPositionProcessor", {"step": 1000}]`

### 2023-02-20 Behavioral trees support templates
  - Sub-tree of behavior tree can be stored in a file or in the `template` section of the quest and loaded from there. Those templates can be called with parameters that are dynamically added to the template definition upon the load (similar to entity templates).

### 2023-01-12 Initial implementation for usage of behavioral trees for AI logic
  - New component `BTree` created - analogous to `Brain` component
  - New processor `generate_command_from_btree_processor` created - analogous to `generate_command_from_brain_processor`
  - New core package `pyrpg.core.btrees` created. Contains classes for individual btree nodes and functions
  - Behavior tree in pyRPG implementation contains in the leaf behavior nodes actions and conditions represented by command name and command parameters as a strings/dict. The logic which behavior leaf node is selected is guided by the other parent nodes in the btree. The command is then passed to the command manager which changes it to function call and returns the result back to the behavior tree.

### 2022-11-20 Possibility to copy components from one entity to other entity within the definition in the quest file - EXPERIMENTAL
  - Similarly to creating the entity from template it is now possible to create new entity from existing entity by copying its component from existing entity.
  - This can be achieved by putting entity alias in `templates` list with `#` prefix. E.g. `"templates": ["#crate01"]`
  - This feature is only experimental. It is using `copy.copy` method for creation of the components on the new entity. Later changes in source entity component can affect also the destination entity component (sharing the same memory location).

### 2022-11-20 Possibility to delete component from entity from within the definition in the quest file

### 2022-11-13 Possibility to additionally add components on the existing entity with definition in the quest file
  - This feature allows to add/rewrite components on one entity several times in the quest file(s)
  - This is useful when the game is spread accross multiple files and in new level (new quest file) we need to add additional feature to our entity (and not create a new one).
  - E.g. player entity is created in the first quest file and in the next quest file (level) we need to adjust starting position of the player. So we can simply add new position component to player01 that will override the original position.

### 2022-08-04 Templates with parameters, templates loaded from within the quest definition as well as from the files

### 2022-07-01 Adjustments in ECS_MANAGER. Entities are not loaded before components, so entity alias can be used anywhere in the quest JSON!

### 2022-06-27 Implemented confirmation dialog as a form of script. After clicking on OK, custom event with custom parameters is generated and can be further processed by standard event handling logic.

### 2022-06-24 Implemented category of Pickable entities - now we can test the event on number of items in any given category in HasInventory

### 2022-06-24 Event handling logic was rewritten to json logic

### 2022-06-14 ProgressBar screen implemented
  Now, there is a new class `ProgressBar` that is initiated in `Main` class and passed to `Game` class. In the `new_game` method, new thread is created that calls `ProgressBar.run` function that draws progress bar in the separate thread. The status of the progress is updated by calling `ProgressBar.update` function. Once the progress is done and no more progress bar should be displayed, `update(finished=True)` needs to triggered. This effectivelly stops the `run` method from execution and hence the thread operation ends.

### 2022-06-07 New ScriptManager prepared
  The `ScriptManager` is responsible for loading and execution of the script. Script is single python module that can be dynamically specified within quest specification.

### 2022-06-02 Extension of PREREQ on Processors to support logical operations while evaluating the prerequisities

### 2022-05-24 Score System Implemented
  New `Score System` was implemented and new components `HasScore`, `ScorableOnDamage`, `ScorableOnNoHealth` were introduced.

### 2022-05-22 Damage system implemented
  New `Damage System` was implemented and new components `Damaging` and `Damageable` introduced.

### 2022-05-06 All components have JSON schema

### 2022-05-03 Collision System - adjustment of logic for accept_fix and pos_fix_oth
  Fixing the logic of those 2 boolean variables passed with every collision.
    * `accept_fix` ... entity moved answers the question if entity moved can be moved by entity other. So better name for this var will be `accept_fix` (is determined by the whitelists of moved entity).
    * `apply_fix` ... entity other answers the question if entity moved can be moved by entity other. So better name for this var will be `apply_fix` (is determined by the whitelists on other entity).

### 2022-05-02 Added new function `get_components_opt` into ESPER framework
  This new function returns `None` or `Component` entity based on information if optional component exists or not. This is useful to omit *ifs* in the processors and I plan to use it in 
    - *Collision System* to implement weight or push factor
    - *Attack System* for calculation of position of the projectile

### 2022-04-22 Optimization of performance of collision processor
  Originally, the collision generation processor has time complexity N^2. Newly this was changed to N*(N-1)/2

### 2022-03-22 Solving problem with entities with IsDestroyed component that are not deleted from the ECS game world immediatelly

  #### Context
  There is a component called `DestroyOnCollision`. Entities having this component should be assigned `IsDestroyed` component after collision. Consequently, `PerformDestroyEntitiesProcessor` processor should delete from the ECS game world all entities with `IsDestroyed` flag. Typical scenario is an arrow entity that should cease to exist in the world after it hits the target.

  #### Description of the problem
  At the moment, there is a situation when arrow hits the target and is assigned `IsDestroyed` component. However, the arrow is not deleted from the world immediatelly by `PerformDestroyEntitiesProcessor` processor and stays in the game for small number of upcoming game cycles. It can be demonstrated in the log below:

  Entity 6 represents the arrow that hitted the target in the cycle 2371 but was destroyed 3 cycles later.

  ```
  ❯ grep perform_destroy_entities_processor processors.log
  perform_destroy_entities_processor.py         - (2371) - Entity 6 - get_ticks 11578, destroyed_time 11578, ttl 0
  perform_destroy_entities_processor.py         - (2372) - Entity 6 - get_ticks 11633, destroyed_time 11633, ttl 0
  perform_destroy_entities_processor.py         - (2373) - Entity 6 - get_ticks 11683, destroyed_time 11683, ttl 0
  perform_destroy_entities_processor.py         - (2374) - Entity 6 - get_ticks 11744, destroyed_time 11743, ttl 0
  perform_destroy_entities_processor.py         - (2374) - Entity 6 was deleted from the world.
  ```

  This situation results in generation of multiple unnecessary explosion effects (instead of one) and multiple overlapping sound effects. Both those effects happen based on collision. Normally, arrow should be destroyed upon the first collision in the cycle 2371, but it is not. Hence, further collisions occur with entity that has `IsDestroyed` component assigned.

  #### Possible Ways of investigation
  1. Most straightforward solution might be not to allow collisions with entities that have `IsDestroyed` flag assigned.
  2. I feel that the bahavior of deleting entities needs to be investigated in order to prevent surprices in further development. I feel that this has something to do with the ESPER ECS caching logic.

  #### Final solution
  Probably there was a bug in `PerformDestroyEntitiesProcessor` - particularly in the way the elapsed time was calculated. After fixing of the condition it seems that the deletion from the ECS game world is done in the cycle when IsDestroyed flag is assigned.

### 2022-03-04 Adding support for YAML quest files definition
  Newly, pyRPG supports loading quest in YAML file format. It can be more readable for some people than json.

### LOGGING implemented
   - Configuration of the logging is happening in pyrpg.main. The configuration itself is part of the `config.py`. 
   - There are 3 handlers for logging 
     - `console` - for logging to the standard output / text console
     - `in_game_console` - for logging to the graphical console that is available directly from the game. In order to enable this logic, there needs to be write function implemented in some module. For now the module is `pyrpg.core.config.console` but might be different one in the future as this is not elegant enough.
     - `file_handler_proc` - for logging of processor logs into the file. This file can be filtered by `grep` tool if looking for particular cycle/entity
   - The `root` logger is mapped to text console, but just few logs should be there as other logs are filtered out and sent to other handlers
   - The `pyrpg` logger catches all logs that are not processed by the child loggers (child entities) and prints them to the game console
   - The `pyrpg.core.ecs.processors` logger prints logs from processors to the file where those can be easily filtered

### JSONs that are describing the game are now supporting C-style comments
  - Previously, JSON file was not supporting any comments. As defined by JSON standard, everything in JSON is data.
  - Newly, by using of `re` library and removing of strings starting with `//` before JSON processing, it is possible to have comments in game JSONs and hence improve the readibility of the code.

### New *MOVEMENT SYSTEM*
  Aim is to support following features - be able to assign any command to controll keys, be able to generate flag in case that in the cycle entity has moved (so that other processors can have the condition on entity movement without the need of some specific boolean parameter and unnecessary ifs), be able to move diagonally also with NPC using brain commands.

  - Currently, `Controllable` component is not generic enough and `InputProcessor` presumes that for up/down/left/right actions there is always `move` command uses (processor uses parameters applicable for `move` command only and no other commands).
  - Newly, the input component is truly universal and accept any command for control keys. Following has been done.
    - New `Controllable` component has been prepared
      - Newly, `control_cmds` dict defines not only command for given action but also parameters of the command. For example `('move', {'moves' : ['up']})` is a cmd defined as a tuple
      - This also supports multiple commands, for example `[('move', {'moves' : ['up']}), ('move', {'moves' : ['left', 'right']})]`
      - **if some command would require execution through several cycles, `modify_brain` command can be used**. For example `["modify_brain", {"commands" : [[null, "moveto", {"position": "cursor"}]` can take you to the position where the cursor is at the moment of left-click. For those kind of commands `Brain` component is always needed.
    - New `GenerateCommandFromInputProcessor` processor prepared
      - Processor can process command and its parameters defined in `Controllable` component (including multiple commands)
    - New `new_move` command family has been introduced
      - Current `move` command is using `Motion` component to remember where to move
      - Newly, `Movable` component stores `velocity` and `accelerate` - no longer the information about vector of movement.
      - Newly, new `FlagDoMove` component is introduced, containing all the information about the vector of movement. For example `FlagDoMove(vector=[5, 10])`
    - New `PerformMovementProcessor` exists
      - takes `Position` + `Movable` + `FlagDoMove`
      - remembers last position on `Position` component
      - remembers last move time on new `Movable` component
      - updates `Position`
    - New command `new_move_auto` was introduced. This command has no parameters and it moves the entity in the current direction. This command is expected to be usefull for auto-movements of projectiles. This command should be placed in the `Brain` of the projectile and hence substitute the currently existing `LinearMovementProcessor` processor.
    - component `Movable` and processor `PerformMovementProcessor` newly supports also acceleration. This again is expected to be useful for accelerated auto_movement of projectile.

### Processors used in the game are now configurable within JSON describing the quest
  - Previously, the construction of processors and their adding into the world was hardcoded in `engine.create_processors` function.
  - Newly, the list and order of processors is fully configurable within JSON file describing the quest.
    - there is new list defined in the quest JSON (on quest level) called `processors`
    - the format of the item from `processors` list looks as follows `["ExampleProcessor", {"example_argument" : arg_value}]`
    - there is new function is `processors.__init__.py` called `get_processor(proc_str)`. Based on the name of the processor on the input, the function returns tuple containing reference to the class of given processor + list of names of class __init__ parameters (excluding `self` parameter)
    - there is new `engine._create_processor(proc_str)` function that takes the list of 2 items (processor name + processor additional parameters in form of a dict), creates the new processor and registers it in the game world.
    - there is new code in `Quest.__init__` consrtuctor that parses the quest JSON `processors` list and calls `engine._create_processor` for every item in `processors` list. By doing so, all the processors are created in the game world.

### New destroy score generation system (several processors and temporary flags)
  Aim of this system is to be able to generate Score flag `FlagAddScore` upon destroyed entity (no health). The flag is further processed by *SCORE COUNTING SYSTEM* in order to add the score to the correct entity.

  - *INPUT Dependency* - system generating `FlagNoHealth` - *DAMAGE SYSTEM*
  - *OUTPUT Dependency* - system consuming `FlagAddScore` - *SCORE COUNTING SYSTEM*

  - new component `ScorableOnDestroy`. Entity having this component is providing score points upon its damage
  - new processor `GenerateScoreDestroyProcessor`
    - looks for `FlagNoHealth` + `ScorableOnDestroy` + `Collidable` (to get list of all that have collided thys cycle with the entity)
    - add `FlagAddScore` to all 

### New damage score generation system (several processors and temporary flags)
  Aim of this system is to be able to generate Score flag `FlagAddScore` upon damage. The flag is further processed by *SCORE COUNTING SYSTEM* in order to add the score to the correct entity.

  - *INPUT Dependency* - system generating `FlagAddDamage` - *DAMAGE SYSTEM*
  - *OUTPUT Dependency* - system consuming `FlagAddScore` - *SCORE COUNTING SYSTEM*

  - new component `ScorableOnDamage`. Entity having this component is providing score points upon its damage
  - new processor `GenerateScoreDamageProcessor`
    - looks for `FlagAddDamage` + `ScorableOnDamage` + `Collidable` (to get list of all that have collided thys cycle with the entity)
    - add `FlagAddScore` to all 

### New score counting system (several processors and temporary flags)
  Aim of this system is to be able to count Score. The aim is not to generate the score events represented by `FlagAddScore`. That is the aim of score generator systems such as *damage score generator system*, *kill score generator system*, *pickup score generator system*

  - *INPUT Dependency* - systems generating `FlagAddScore` - *DAMAGE SCORE GENERATION SYSTEM*, *DESTROY SCORE GENERATION SYSTEM*
  - *OUTPUT Dependency* None

  - new component `HasScore` on entity marking entity as the one that can have score
    - component has `delegate` that contains entity_id in case score needs to be delegated to some other entity. For example after arrow hits NPC, the score goes to the player and not to the arrow.
  - new processor `CalculateScoreProcessor`
    - takes `FlagAddScore` + `HasScore`
    - calculates new `HasScore.score`
    - generates `SCORE` event
  - new processor `RemoveFlagAddScoreProcessor` that removes the `FlagAddScore` at the end of the cycle

### New destroy system (several processors and temporary flags)
  - *INPUT Dependency* on Damage System - `FlagNoHealth` (needs to be planned after `CalculateDamageProcessor`)
  - *OUTPUT Dependency* towards `RenderableModelAnimationActionProcessor` (usage of `IsDestroyed` component)

  - new processor `HandleDestroyedEntitiesProcessor` that does the following
    - search all entities with `FlagNoHealth` component
    - triggers `KILL` event
    - assigns permanent `IsDestroyed` component to the dead entity so that the `RenderableModelAnimationActionProcessor` processor properly processes it
    - removes movement and other features from the entity
    - assigns `Temporary` component so that entity disappears after some time

### New damage system (several processors and temporary flags) implementation
  - *INPUT Dependency* on Collision System - `Collidable`, `Damageable` (needs to be planned after `CollisionEntityGeneratorProcessor`)
  - *OUTPUT Dependency* towards `HandleDestroyedEntitiesProcessor` (usage of `FlagNoHealth` component)

  - new component `FlagAddDamage` that denotes that entity has colided with damaging and collidable entity entity
  - adjusted processor `CollisionDamageProcessor`
    - filter for `Damaging` and `Collidable` and add `FlagAddDamage` to all
    - component `FlagAddDamage` has `src_entity` parameter that marks the source entity that caused the damage
    - the `FlagAddDamage.src_entity` value is derived from `Damaging.parent` entity in case it exists
  - new processor `CalculateDamageProcessor` after `CollisionDamageProcessor`
    - filter for `Damageble` and `FlagAddDamage`
    - calculate the damage
    - create damage event
    - generate `FlagNoHealth` if the health is 0
  - new processor `RemoveFlagAddDamage`
    - removes the flag at the end to prevent multiple calculation of damage
  - new processor `RemoveFlagNoHealth` - if other system wants to use this for handling of destroyed entities
    - the other processor that handles destroyed entities handles it `HandleDestroyedEntitiesProcessors`

### Component classes are using engine for translation of alias to id - get rid of those back referencing
  - at the moment, during initiation `import pyrpg.core.engine` is importing also `pyrpg.components` which is importing all components, even those that are again importing `pyrpg.core.engine`. This is probably why this is cyclic import and I would like to get rid of this in order to keep the loose coupling.
  - WHY? to translate entity alias to entity id. Entity alias is stored in `engine.alias_to_entity` dictionary. This can be omitted by implementing translation from entity alias to entity id in `create_component` method that is part of `pyrpg.core.ecs.components` package init code.
  - Component function `has_weapon.create_projectile` was using `engine` reference for creation of new entities that were representing projectiles. This functionality was moved to `generate_projectile_processor` and reference to `engine` removed from the component. As a side effect, the list of entities generated by the factory was moved from `HasWeapon` component to more generic `Factory` component.

### New functionality for displaying in-game windows
 - even pause window implemented as a dialog!

### Init quest created that is always loaded before any other quest
  - This quest is **always** loaded on the pyRPG start and contains game definitions that are common for the whole game - first example is definition of PAUSE dialog.
  - There is still possibility that quests (game definitions) that are loaded later can overrule the *init* quest definitions by specifying its objects in *cleanup* section of the quest definition.

### Console configured to be available anytime, not only in game, and to display system messages
  - Console is always loaded and part of the game. Whether system messages are showed and console poped is determined by the parameter in `pyrpg.main.init` function called `cons_enabled`. Value of this parameter is stored as `pyrpg.main.show_cons_on_sys_msg` variable for further use.
  - Console can be toggled from every game state by pressing `K_CONSOLE_TOGGLE` button.
  - Functions that are serving the console are executed in every game cycle for every game state. By doing so, we can achieve rolling-out effect even if the game state has no longer value `CONSOLE`.
  - In order to always keep the console transparent, a copy of a screen is taken once console is enabled, and blitted before the console. For capturing the game screen, new function has been introduced in `pyrpg.core.engine` module called `save_screen_copy()`. The function stores the copy of the screen in `pygame.core.engine.screen_copy` variable.
  - In order to disable any functional keys for controlling the game/menus when the console is enabled, new game state `CONSOLE` has been introduced. While being in this game state, only console is consuming all the inputs.
  - There is new function `pygame.main.update_console(text)`. The aim of this function is to be available for every part of the game to push system notifications to the console. In order to achieve that, reference to this function is stored in engine module as `pyrpg.core.engine.cons_update_fnc`. Every part of the game can then push text on console by calling `pyrpg.core.engine.cons_update_fnc(text)`. If this function is called and `pyrpg.main.show_cons_on_sys_msg` is set to `True`, console is forcefully displayed. If set to `False`, the message is written to the console but the console remains hidden. 

### Showing the messages during the game (not stopping the game)- things like 'item picked', 'NPC died', 'new phase changed'
  - New global variable `engine.message_queue` stores message objects to be displayed (or any other action)
  - New module `core.messages.messages` that defines the message object (position, text, ttl and time of creation) and defines `messages.process` function that blits all the messages on the game window.
  - Adjustment done in `core.events.Event` class. Every event type has now predefined format to be printed as event string - read from config file.
  - New function `core.engine.process_game_messages` that exclude all no longer valid messages from `engine.message_queue` and calls `messages.process` to print the valid messages on the game window.
  - New processor `GameMessagesProcessor` that only callse `core.engine.process_game_messages` and nothing else
  - Messages can be generated from anywhere in the code. Now, they can be generated by following means:
    - by event processor - i.e. function `engine.process_game_events` - every event that is processed is automatically put into the message queue. Based on configuration it is decided if message should be shown or not and in what format.
    - by script function - i.e. function `core.scripts.add_msg` - this can be used when generating message as an quest event handler action
    - by command function - i.e. function `core.commands.add_msg` - this can be used from brain component

### Game windows that can be shown as actions for quest or quest phase start (stopping any other action from happening)
  - New events *QUEST_START* and *PHASE_START* were created. Those events are automatically added to the event queue on every quest init and phase init (hardcoded).
  - Quest definition json contains even handler that handles *QUEST_START* and *PHASE_START* events. 
  - In the *condition* of the even handler there is definition of phase that we want to have linked with displaying of the game window, i.e. `"conditions" : {"script" : "self.phase_id == 'phase01'"}`
  - In the *action* of the event handler there is `show_dlg_window` script being called. The `show_dlg_window` script function uses `utils.dialog` to draw window on the screen. While `show_dlg_window` is executed, the rest of the game is frozen.

### Keys are defined as config parameters and as entity templates
  - There is a new dictionary in `core.config.config` module called KEYS. The KEYS dictionary consist of list of key profiles, individual key profiles and other keys. Key profile is dictionary of keys that can be used to manipulate game entity (character, NPC, camera, ...). Every key profile has up, down, left, right and action key. The particular keyboard key is defined as a string that must follow the same convention as pygame keys. For example the string 'K_UP' represents `pygame.K_UP` key.
  - Default profiles and assigned keys are hardcoded in the `core.config.config` module and those are overwritten by settings present in the `config.json` file.
  - There is a new `core.config.keys` module. This module holds the actual key values that are used in the game. On the module init, keys are read from `core.config.config.KEYS` dictionary and translated to real pygame key values.
  - If  some part of the game wants to work with keys, it must import the `core.config.keys` module and use the constant that represent the keys from this module. For example, if I want to reference the key that toggles game console, I refer to that key as `core.config.keys.K_CONSOLE_TOGGLE`. If I want to refer to key profile 'up' key, I can do it by calling `core.config.keys.K_PROFILE['key_controls_1']['up']`.
  - In order to be able to assign different key profiles to different game entities (for example each of 2 players will have different key profile assigned), I can create `Controllable` entity with parameter refereing to a key profile that should be used - `{"type" : "Controllable", "params" : {"key_profile" : "key_controls_1"}}`.
  - To make the functionality easier to use, there have been created *key control json definition entities* as a part of entity hierarchy (key_controls.json, ...). If we want to define new game entity that should be controllable by keys defined in key_controls_1 it is enough to say that this entity inherits from template `key_controls_1`. By doing so, `Controllable` component referencing `key_controls_1` config keys will be added to such entity.

### Support for dynamic text dialogs
  - `CanTalk` component has new attribute `text_speed` that is managing the speed of displaying text for the particular entity (NPC/player).
  - `show_dialog` module has now 2 functions `show_dialog_static` and `show_dialog_dynamic`. Static fcion is the original function whereas the dynamic is the new one.
  - Based on elapsed time from the first command call, the command is showing portion of the text. `frame_surf` is static and generated only on the first call of the command wherease the `test_surf` is generated every time the command is called internally. Hence, it is slower than `show_dialog_static` function.
  - The command remains the same, i.e. `show_command`. The decision if dynamic or static function is to be used must be done in commands package mapping.

### Support for transparent dialog bubble frames
  - `CanTalk` component adjusted by new parameters - `frame_surf`, `frame_dim` and `frame_text_offset` in order for `RenderTalkProcessor` to blit frame and text individually on the game screen (to achieve transparent frame but not transparent text).
  - `show_dialog` command adjusted to prepare both surfaces - for frame and for the text and save them both into `CanTalk` component

### Support for bitmap fonts and frames implemented
  - New package `utils` containing 2 modules - `bitmap_font` and `bitmap_frame`
  - New module  `core.config.fonts`/ `core.config.frames` initiating fonts/frames to be used within the whole game (e.g. debug font, player talk font)
  - New processor `RenderTalkProcessor` only blits preprepared surfaces from `CanTalk` component on the screen
  - Component `CanTalk` newly does not contain any font reference, just surface on which text can be blitted by command
  - Command `show_dialog` is only importing preprepared fonts from `core.config.fonts`/frames from `core.config.frames` and blits the text to `CanTalk` surface

### Deletion of entities upon collision implemented
  - New component *DeleteOnCollision* that is only a tag that indicates that entity should be deleted after processing of collisions
  - Adjustment of *Collidable* component that newly contains new flag has_collided (indicates if entity has collided with something in current processor loop)
  - Adjustment of *CollisionEntityGeneratorProcessor* processor
    - processor newly resets has_collided flag on all entities with Collidable component (at the beginning of collision processing)
    - processor newly sets has_collided flag to `True` on all entities for which some collision event was created 
  - New processor *CollisionDeletionProcessor* deletes entities that have component `DeleteOnCollision` and `has_collided` set to `True`

### Death implemented
  - Adjustment of *CollisionDamageProcessor* - after health is below 0, following happens:
    - New component *IsDead* is assigned to the entity 
    - Components *Brain*, *Motion*, *Camera*, *Collidable* are removed 
    - Component *Temporary* is added in order to remove the dead body after some time.

### Cached models (flyweight) implemented
  - Model stored in cached class Model. 
  - All images used for model animations are stored in images dictionary, where key is tile_id and value is surface containing the actual image.
  - All information about animation actions and directions are stored in frames dictionary - see example below

      {
        'walk' : {
            'up' : {
                'tiles' : [ # Reference to images dictionary
                    NamedTuple(tileid=102,duration=75),
                    NamedTuple(tileid=103,duration=75),
                    NamedTuple(tileid=104,duration=75),
                    NamedTuple(tileid=105,duration=75),
                    NamedTuple(tileid=106,duration=75)
                ],
                'repeat' : True, # TILED SW parameter - OPTIONAL - it is always True unless it is set to false in the json parameters - False means that it stops on the last frame
                'action_frame' : 3 # TILED SW parameter - OPTIONAL - on which of the frame generate action (swing object, arrow object generation). It is last frame unless stated otherwise by the parameter
            }
        }
     }

  - Following conditions must be met to successful load model from the tileset.
    - Action must be in the list of supported actions `Model.ACTIONS` - otherwise, error is raised
    - Action can have either None or all directions - otherwise, error is raised
    - Direction must be in the list of valid directions `Model.DIRECTIONS`
    - 'idle' action must always be present in the model (default game action)

### Picking up a weapon and attacking implemented
  - New component *Weapon* - identification of the weapon type - 4 types supported (sword, spear, bow, spell)
  - Typically, entity with *Weapon* will also have following components - *Pickable*, *Collidable*,*RenderableModel*.
  - New component *HasWeapon* - if entity can arm a weapon and use a weapon.
  - New component *Factory* - component that can generate other entities based on dict parameter 'prescription'.It is necessary to produce projectiles from the weapon (new entities).
  - New component *Container* - component that is keeping reference to some other component.
    - Necessary to keep reference on projectile to original *HasWeapon* component with list of generated projectiles.
  - New processor *RenderableModelAnimationUpdateProcessor*
    - updates animation frame only once for every entity that is displayed. Previous solution of *RenderWorldProcessor* was updating the frame of entity for every camera where this entity was present.
  - New processor *RenderableModelAnimationActionProcessor*.
    - updates the action of the entity - entity can be idle, walk, idle weapon and weapon action
  - Adjustment of processor *RenderableModelWorldProcessor*
    - newly the processor is calling `get_current_frame` fnction (no frame shifts) instead of `get_frame` function (frame shifts).
  - New command *attack*.
    - only sets `has_attacked` flag to True. The flag is used to decide of the action of the entity
  - Further notes:
    - last attack animation frame creates new entity (projectile) by calling HasWeapon -> Factory
    - there is new collision processor *CollisionDamageProcessor* that decreases health represented by *Damagable* component.

### Picking up and Wearing clothes implemented
  - New component *Wearable* - identification of wearable entity.
  - Typically, entity with *Wearable* component will also have *RenderableModel*, *Pickable*, *Collidable* components.
    - Component specifies bodypart to which it should be weared.
  - New component *CanWear* - if entity can wear wearable component.
    - component contains dictionary of entities that are weared.
  - New processor *CollisionWearableProcessor* created.
    - must be planned before *CollisionItemProcessor* - first try to wear the item (*CanWear* mandatory), then pick it up as regular item into the inventory.
    - wearing item generates new event that can be scripted in the quest - *WEARABLE_WEARED*
  - Adjustment of processor *RenderModelWorldProcessor* - added check if entity has CanWear component and if yes - rendering the clothes.

### Processing only entities that are visible on the screen implemented
  - New filter function filter_only_visible_on_camera implemented.
  - Function is filtering based on *Position* component x, y vars and camera screen rectancle. Entities that have position out of this camera rectancle are not being drawn.

### Animated Characters implemented
  - New component *RenderableModel* - substitution of static component - *Renderable*
  - New *Model* class that reads json tileset from *Tiled* 3rd party SW
  - New processor *RenderableModelWorldProcessor* - substitution of *RenderableWorldProcessor*
  - new *StatusProcessor* processor
    - used to correctly set the status for rendered animation character
    - uses motion.has_moved flag and hasWeapon.has_attached flag for setting up idle/walk/attack status

### Save and Load game implemented
  - Implementation using pickle library.

  1. All engine global objects are put into the dictionary called game_state (command queue, event queue, maps, quests and esper.world)
  2. pygame.Surface objects are not serializable, so before saving it was necessary to set every such reference to None (on both components and processors).
  3. After saving those references must be refreshed in order to keep the game going - it is done using pre_save and post_load methods and the logic happens in save_game and load_game functions.
  
  - During the game, pressing *F1* saves the game and pressing *F2* loads the game.

### Simple quest implemented
  - **Scenario overview**
    - Player hits NPC.
    - Player and NPC have linear conversation.
    - At the end of the conversation NPC gives item to the player (key).
    - NPC waits until task is done.
    - Using the key, player can enter to the other map - teleport with the key.

### Global brain implemented (Global Script processor)
  - It is implemented as a simple entity with just *Brain* component.
  - Every command must have parameter *entity* specified because if it is not specified then the command is trying to be executed on the source entity (which does not make sence for the global script processor).

### Picking items implemented
  - very similar to *Teleport* implementation

### Quest event (simple) processing implemented
  - New *GameEventProcessor* created. The processor takes as a parametr global (engine) function that is event handler.
  - The engine handler function is called and takes the list of events and passes it to all quests.
  - Each quest has event handler method that processes the event based on conditions and actions.
  - Those conditions and actions are specified in json file specifying the quest/phase.
  - **Conditions** can be specified in 3 ways that can be combined:
    - by comparing the event params to condition params
    - by evaluating python condition in form of the string
    - by executing function that returns boolean
  - **Actions** are specified as a list of functions
    - execute function can be used to invoke arbitrary python code or taking the code from file or other json element
    - modify_brain function - resets brain of any entity with commands from Command class
    - other functions - shake screen, fadein/fadeout, ...

### Teleports implemented
  - Record collision entities on *Collision* components (list of entities with whom the entity has collided).
  - *CollisionEntityGenerator* processor records collision entities on *Collision* component.
  - *CollisionTeleport* processor iterates all teleports and resolves collisions that are recorder on the *Collision* component.
  - *CollisionCorrector* processor resolves all the outstanding collisions that were not handled by *Teleport* and/or *Item* processor.

### Scrolling implemented
  - *CameraProcessor* updates camera offset based on position (*Position* component) of the entity that has *Camera* component.
  - *RenderProcessor* iterates all entities with *Camera* component and draws the screen into *Camera* componet variable sceen that is blitted on the window.

### Multiple game screens implemented
  - Entity can have *Camera* component assigned.
  - *Camera* component is represented by separate game screen on the main game window where entity is in the centre of this screen.
  - *Render* processors and *Camera* processors facilitates correct updating of all camera screens.
  - New screen can be dynamically added/removed by adding/removing *Camera* component to any entity that I want. Command that adds/removes *Camera* component to any entity must be called for that.

### Architecture Design implemented
  - *Maps and Quests* are out of esper.world.
  - *Maps and Quests* are accessed from Processors that have esper.world as an input parameter i.e. they know how to call outside of the esper.world.
  - *Event handling* is achieved by calling to engine functions from esper.world processors.
  - *Command handling* is achieved by calling to engine functions from esper.world processors.
