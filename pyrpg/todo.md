
  - [x] - get rid of timed - should be part of the config and not passed around as a parameter
  - [ ] - change width of the console from separate function
  - [ ] - implement reload in console - changing CLI, Paths, ... maybe just adjust the same init function ... using _INIT ...
  - [x] - remove WIDTH and HEIGHT, keep only resolution
  - [ ] - GUI manager after calling init is deleting the background with the game - do it so that background is kept
  - [ ] - console manager after init is deleting all history from console. Probably do some separate function `on_display_changed`
  - change video component to take resolution
  - prepare console command that changes the resolution
    - display.init()
    - gui_manager.init()
    - updates all video components in the game

  Features
  - [x] BUG - DISPLAY["SHOW_FPS"] is not taking configuration from config.jsonc
  - [ ] new `ALL` option for cleanup actions - some new wrapper functions will be needed
  - [ ] Some problem with `tests/12_ai/simple/do_parallel.jsonc` when enemy approaches
  - [ ] Show FPS also i fullscreen mode (config parameter)
  - [ ] Branch - Fix console and make it more usable. It contains very old descriptions.
  - [ ] Branch - Fix running in 1920x1080 fullscreen - how to tell video component to get the system configuration - to cover the full screen?

# To Do
 
  - [ ] BUG - Why the FPS rate is decreasing in time... collisions???
  - [ ] Progress bar is showing `number / None` - fix is problematic for unknown reason

  - [ ] `do_parallel` to support skipping of cycles so that some commands run once per some amount of ticks and meanwhile return some default value
  - [ ] prepare `test_bb_value_in` and `test_bb_value_not_in` as a faster alternatives to `test_bb_values` that is using potentionally slow json logic
  - [ ] blackboard having implicit value `self` referencing the entity ID or name - can be then used in all handlers
  - [ ] new command based on experience with `do_parallel` - `do_if_bb_test_true`
  - [ ] Behavior Tree and Behavior list - implementation of restart function - tree/list starts again from scratch. Useful for restart of the whole tree if some event comes.
  - [ ] Make scripts runnable from the console
  - [ ] Rename scenes to scenes. Scene is more common name for what the engine is defining in the json files.
  - [ ] Every game/test using scenes should be defined outside of pyRPG folders and only import pyRPG and use its parts. No direct changes in pyRPG folders and files.
  - [ ] Make scripts more nice - now they are using main, is it ok? Missing logging, missing description. Missing concept when to use commands and when to use scripts, make them work from console...
  - [ ] finish tests and json definitions for new commands

## Bugs
  - [ ] BUG - move_to command makes the NPSs to walk through the tiles
  - [x] BUG - entity is moving to the second point in the path not the first point in the path! That is causing problems when only chekcpoints are moved. Entity is not avoiding obstacles under those circumstances.
  
  - [ ] BUG - move_to_pos_target_vect - direction of movement (facing of entity is not being changed)
  - [ ] BUG - Problem with pushing entities into walls - eventhough map collisions are enabled. To be fixed.
  - [ ] BUG - debug processor works onlywith one camera
  - [ ] BUG - when restarting scene in the `collect_coins` game, there is loading screen in the background

  - [x] BUG - The configurations are not properly merged when merging nested dictionaries - fix needed
  
  - [x] BUG - Template from existing entity using # ... add entities also into storage=self._template_definitions

  - [x] BUG - Updating of existing entity (created in some scene before) does not work. Instead, completely new entity is created!
  - [x] BUG - When collect coins or sokoban ends it cannot start again for some error - fix it
  - [x] BUG - at the moment cannot controll other entity as the `entity` parameter is poped from the command `params`. As `params` is mutable dictionary, it is removed everywhere. As a fix, either add `entity_id` into the `Command` namedtuple or do not `pop` the entity parameter, just read it.
  - [x] BUG - seems that `ECSManager` does not translate references to aliases that are lower in the scene file. It would be needed to add new item to the `engine.load_scene_def_fncs` that will call some `create_empty_entity` over all entities first and then calles `update_entity` over all (2 step process, now it is just one step).
  - [x] BUG - Dialogs stopped working - because engine.py imports QuestManager and QuestManager imports Scene scene.py imports scripts  (for get_script_fnc) and there are all scripts imported - we need to have script same as processor - define it at JSON string
  - [x] BUG - when shooting arrow the entity moves down - fixed by adding `accept_pos_fix_from_denylist=["ALL"]`
  - [x] BUG - NPC is destroyed but the brain still works - as a result it is lying dead and moving forward
  - [x] BUG - when there is no command assigned to ACTION button, the controlls freeze after pressing z button - None command must be assigned in Controllable component
  - [x] BUG - on the map the second layer is not transparent but has black background - update pyTMX helped
  - [x] Bug - btree problem when the tree should run again - for example with usage of the `Repeater` node. Fixed. It was caused by the `btree._action_node` not reseting to None when the `Repeater` reset the whole tree to run it again.
  - [x] BUG - fix `play_commands_01.jsonc`

## Features - to rearange
  - [x] Implement handlers into behavior tree definitons - handlers will just put some value from the event on the blackboard. Done - now handlers can be part of components (or basically anywhere in the scene definition. Only the engine code needs to be slightly adjusted). Script `set_bb_key` was prepared to set blackboard value and can be used in the handlers.

  - [ ] Move the processors that are removing the temporary Flag components before the processors that generate Flag components. To ensure that the Flag component is available for all processors, even for those that are before the generator processor.
  - [ ] Instead of ecs_mng return group of functions from the engine - not only for ECS manipulation but for other purposes as well. For example for executing commands, processing events, getting path from the map or pathfind manager etc.
  - [ ] When some command is internally calling other command, all ctx.locals are put on one place - that can be chaotic. It would be great to have some way to distinguish in which command the ctx variable was created.
  - [ ] COnsider changing of notation on command variables - camel case instead python snake case - for clarity.
  - [ ] implement AStar algorithm for pathfinding and DFS algorithm.
  - [ ] possible to load any map, not only 64x64 and use it with any textures of characters - 128*128. Pixel space vs. tile space vs xxx
  - [ ] redo rendering of the tileset - quick algorithm that is using maximum of what has been developed in previous frame and only renders changes.
  - [ ] AI kill them all game
  - [x] path finding using checkpoints on the map and BFS from source and target
  - [ ] doctest on command files - process tests calling always `init` as prerequisite
  - [ ] tile_to_px function and px_to_tile function store somewhere and use it universaly - now haviong it in commands and debug processor at least.
  - [ ] adjust BFS pathfinding so it prefers right-left up-down movement based on the greater distance to the target.
  - [ ] write test to `move_to_target`, `face_entity`, `test_bb_value`, `set_bb_value` commands, then merge the branches


  - [ ] Make universal loader that takes full path, partial path, with or without suffix - all possible options - RenderableModel path, templates path, SOund path, vfx path
  - [ ] Extend sound effects - SoundFXOnGeneration - generator produces sound - shooted arrow
  - [ ] Person can generate many sound effects at once - damage and no health and collision and footsteps - how to stop playing damage sound when no health?
  - [ ] Extend Visual FX - VisualFXOnGeneration - for weapons, VisualFXOnCreation, VisualFXOnDamage, VisualFXOnNoHealth
  - [ ] Implement post-requisities on processor and change the process of processor loads - 1st load all processors without checks, 2nd check prerequisities for all proc 3rd check post-requisities for all proc
  - [ ] there is many managers - what about having list of managers and every manager inherits from some abstract class things like `clear()` or `register()` methods. By doing that clearing will be easier done by iterating the list and also can be part of the progress bar.
  - [ ] maybe the ProgressBar might be created in the Game class only and not in the Main class. By doing that, I will pass one less argument to the engine.
  - [ ] option not to scale-up the render models to 64x64
  - [ ] optimize  `map.get_tile_images_by_rect(layer, camera.map_screen_rect)` function. there are unnecessary calculation being done every cycle - tiles to show
  - [ ] Revise usage of `dict.get()` because it is always returning None if value is not found. Sometimes I want the `KeyError` when the key does not exist and not `None`.
  - [ ] Rename create_entity_ex to create_entity
  - [ ] Implement smooth camera moves. When player stops the camera slowly slows down till centred on the player
  - [ ] Implement ordering of displaying of entities based on their Y position. Entities with lower Y should be generated on the display before entities with higher Y
  - [ ] How to implement that some map layer elements are displayed before entities and some behind entities
  - [ ] find all places where we are loading a dictionary and use functions.get_dict and functions.get_dict_params functions
  - [ ] Implement `ALL`, `` into the cleanup at the beginning of the scene definition - ideally some pre_processing that will substitute keyword ALL with all the processors in the
  - [ ] Possibly substitute 'id' key from scene file on entities for 'alias'. To make things more readable in the code and not to mismatch
  - [ ] schema validation path to every test scene
  - [ ] Unit tests for BTree and BList
  - [ ] implement `toml` format for easy scene definitions (same as currenlty used `yaml` and `json`)
  - [ ] implement test scenes for testing of the new commands with the command context.
  - [ ] Implement new component `CanHear` that will specify what the entity can hear and will hold list of entities that are being heard.
  - [ ] it would be nice to have left mouse click and right mouse click mapable in the `Controllable` component to some commands. For example by left click, there will be new brain sequence that will move the character to the target.
  - [ ] btree_test.py failing - try to fix the error with templates
  - [ ] dialogs to be more easily used as a templates
  - [ ] Bug in `test_arm_ammo_01.json` - once you press attack, no other commands are processed
  - [ ] `FAILSAFE_TREE` and `FAILSAFE_LIST` put into config file outside of `Component` classes. Also, unify with default key_commands - those should be in configuration probably as well.
  - [ ] create tests for recording and playback of commands - put out generator value, it is not important.
  - [ ] Add JSON schema definition to all new movement commands px, tile, move_to
  - [ ] Add tests to all new movement commands px, tile, move_to
  - [ ] Revise map class - using pygame.Vector2 instead tuple and list
  - [ ] Position component to use Vector2 from pygame and all game to use Vector2 for pos_px and pos_tile variables
  - [ ] pygame.Vector2 to be used everywhere where possible
  - [ ] Try to implement `move_to` command as a `btree` rather then encapsulate all logic and path points into the command itself. Then compare those 2 approaches. 
  - [ ] Write more mocs to components and managers
  - [ ] Consolidate the packages so instead of the `from pyrpg.core.ecs.components.new.position import Position, PositionMock` we can import as `from pyrpg.core.ecs.components import Position, PositionMock`
  - [ ] In case of error, load some mock - test map instead of real map, test sound instead of real sound, test model instead of real model, test AI instead of real AI
  - [ ] Change of map rendering - do not always generate all the tiles from scretch but - re-use the pane and only draw the tiles that are new + re-draw the animated tiles if needed.
  - [ ] How to solve the problem when AI follows some path and is attacked? The easier way is probably to reset the BT as a part of event handler, not sure.
  - [ ] ECS manager will provide only `_game_functions` to processors and commands and nothing else. Thus, we would need to pass the whole `ecs_mng` reference to the commands but only `ecs_mng._game_functions` (dict of references)

  - [x] Is quest manager used? remove it
  - [x] Rename `quest` to `scene` everywhere
  - [x] Get rid of new and dots in configs below "MODULEPATHS": {"SCRIPT_MODULE_PATH" : "core.scripts.new.", "COMMAND_MODULE_PATH" : "core.commands."
  - [x] Implement logger also for the configurations 
  - [x] reduce number of files in `collision_system` delete some of them and merge necessary version of classes to the existing files `generate_collisions_processor.py` and/or `resolve_collisions_processor`
  - [x] update collision processor according to the new concept and document it
  - [x] write documentation how to add new component/processor class without the need to change all the dependencies - multiple classes in the files
  - [x] Solve creation of arrow/sword swing so that it does not move player and the player does not need to have accept_pos_fix_from_denylist set to [ALL]
  - [x] Prepare all weapons in some test scene - to test the factory functionality
  - [x] JSON schema - every component can have one 
  - [x] JSON Schema for the whole scene
  - [x] Prereq extension so that it supports `and`, `or`, `oneOf`, `anyOf`

  - [x] Prepare script module that implements YES/NO decision + IF json logic - custom event generation and catching the event in the event handler
  - [x] Prepare script that restarts the scene - clear all scene and loads specific scene
  - [x] Reimplement QuestManager so it manages the loading of all scenes data and distribution to other Managers, 
  - [x] *Also reimplement EventManager to manage all the handlers loaded from the scenes*.
  - [x] rewrite conditions and actions upon events into JSON logic format
  - [x] loading game on GUI using threading library
  - [x] implement Sokoban-like game - moving the boxes is ok, when box is landed to the correct spot, it changes??? How to implement that?
  - [x] rewrite commands so that code in the package is not needed and commands register themselves with the command manager
  - [x] implement that the processors are not running in every cycle - some nice implementation for all processors in esper probably would be nice

  - [x] Template not only from files but also from previous entities definition in the scene file - implement copy entity method, maybe on esper level. Then use it in scene definition.
  - [x] Load all entities synonyms at the beginning so that entity names can be used in all component definitions
  - [x] Rewrite all event handling conditions in tests to JSON LOGIC.
  - [x] Fix the map layers that are not transparent - Upgrade to new pyTMX version helped
  - [x] Possibility to update entities in the scene definition - adding new components to already existing entities.
  - [x] Possibility to update entities in the scene definition - deleting components on existing entities.

  - [x] Remake ecs manager so that it contains some get processor function that translate processor string into class. And redo load processor and delete processor to use this new function
  game. By doing it this way it will not be necessary to modify the logic of ecs_manager's delete_processor.
  - [x] Redo prereqs in the scene manager - the load is ugly
  - [x] Implement new component `CanSee` that will specify what the entity can see and will hold list of entities that are being seen.

  
  - [x] in `generate_command_from_XXX_processor` there is repetitive part that is extracting entity_id from the parameters or from the brain owner and putting the command into the queue - this common part can be abstracted into separate function and called separatelly. Alternativelly it can be transfered from processors to `command_manager.add_command` function. 
  - [x] problem that the first movement eventhough by small step is doing huge leap by using `FlagDoMove()` this is because the first `dt` is huge. Has been solved by redoing the first `dt` calculation directly from the `max_fps` value and moving the `dt` calculation at the end of the `main.run` procedure.
  - [x] implement a new FlagDoMove feature that does not take into account `dt` value and always moves by specific amount of pixels, steps. Prepare also new command for that. It is useful for movements of NPCs because using of `dt` correction might lead to unpredicted steps/jumps in the NPC path.

  - [x] Every command should hae its JSON schema definition

  - [x] redo doctests for all commands (cmd_ctx was substituted by ctx) - `move_to.py` and onwards
  - [x] redo `CommandContextMock` so that it does not need to be initiated as `CommandContextMock(globals=ContainerMock(), locals=ContainerMock())` but as `CommandContextMock()`
  - [x] move_to_target command - that is calculating the path
  - [x] move to range and attack with arrows example using path finding and attack command.

