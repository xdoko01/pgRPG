## Current
  - [ ] - new test for arming and disarming a weapon using command ()
  - [ ] - implement some graphics to see the weapons
        - part of inventory render if HasWeapon component exists
        
  - [ ] - `arm_ammo` command and flow + disarm
  - [ ] - prepare some helping function that receives Position and Collidable component for 2 entities on input and returns if those collide or not. Similar for collisions with the map.

  - [ ] - implement `arm_ammo` command + disarm ammo processors
  - [ ] - finish the inventory and arming weapons. After that try to fix Sokoban collision zones. After that collision with the walls must be flawless. After it improve the speed of generation of the map on the screen. After that client/server game.
  - [ ] - is it really necessary to have ecs_mng being passed to every command? Importing ecs_manager and checking if it is initiated should work just as well...

  - [x] - `ITEM_DROP` event enhance same parameters as `ITEM_PICK`
  - [x] - function to remove entity id from `HasInventory` categories - created in `dict_utils` function `del_dict_value`
  - [x] - BUG - Error in `test_arm_weapon_02` after arming by command, the entity is permanently walking - this was caused due to missing animation processors `PerformActionAnimationProcessor` and `PerformActionIdleAnimationProcessor`.
  - [x] - BUG - find out why there is no idle image for the bow - the action: idle was defined in the model, but it was pointing to empty image tile in the model spritesheet. Some spritesheets are special and need to be handled manualli in the Tiles SW. 
  - [x] - BUG - find out why attacking is never stopping - `RemoveFlagDoAttackProcessor` was missing
  - [x] - PREREQ is not halting when defined processor is missing. Why? - Because it was only logging warning and nothing else. Now I have changed the logic of `ecs_manager.create_processor` to raise `ValueError`.
  - [x] - missing some pictures in inventory (idle)
  - [x] - Divide the render inventory processor to 2 parts - command part (mouse) and render part
  - [x] - BUG - find out why in `test_pickup_03.jsonc` I can pickup more than 10 items
  - [x] - BUG - find out why the items are dropped on each other and not next to each other in `test_pickup_03.jsonc`
  - [x] - implement dropping of weapon/ammo that is armed - and for all inventory items - similar system to `pickup` system
        - `FlagIsAboutToDropEntity` + `HasInventory` -> `PerformDropProcessor` -> `FlagWasDroppedBy` + `FlagHasDropped` + event `ITEM_DROP`

  - [x] - change the `test_pickup_02` scene to the proper scene using templates for entities.
  - [x] - proper dropping of inventory items
  - [ ] - Transfer the bug reports to the GitHub functionality.
  - [x] - Implement pause button to demonstrate the processor groups. SOme preocessors running and some stopped.
  - [ ] - Naming functions in `ecs_manager` can be better.
  - [x] - Finish getting key feedback into the `Controllable` component so that `toggle_control` can support it.
  - [x] - implement `PerformDisarmWeaponProcessor` and corresponding components and events

  - [x] - algorithm to find some free area to drop! for `PerformDropProcessor`
        - 8 positions for drop - randomly select one from it - sort them randomly
        - iterate all entities with Position component and Collidable component.
        - for all those check if the candidate position is colliding with some entity
        - additionally check if colliding with some tile
        - if all above is ok, place drop the entity there
        - if one of above is wrong, select from the next 7 positions and return the above
        - if you are at the last posiition and it cannot be used, place it there anyways.

  - [x] - BUG `test_pickup_02` scene. In case that 2 items are dropped and their collision areas overlap then there is brutal slow down. How to find out which processor is causing the slow down effectivelly? `GameEventsExProcessor` is the problem -> `event_manager._event_queue` is getting bigger and bigger. Console Command for seeing stats of `event_manager` and other managers as well.
        -  Every collision generates a record in `event_manager._event_queue` and the queue keeps on growing due to constant collision happening somewhere on the map. IMPLEMENT: that event queue must have some max capacity or events must have some TTL.
        - IMPLEMENT into console header/footer KPI the length of the event queue.
        - REVISIT the `process` and `ignore` mechanism of the `event_manager`. If process=SCENE_START then probably only these events should be in the event queue.
 
  - [ ] - BUG - `Position` component `x` and `y` can have float value in it, why???? Fix to int only
  - [ ] - Automate prep of configuration of fonts - now must be named one by one to add the path. Shoudl be automatic. Same with `init_fonts()`
  - [x] - Command `load_from_template` that will load any template with components on the entity.
  - [x] - BUG - Once unimplemented attack action button is pressed, all controll stops working for some reason  - `test_pickup_02` scene. Something wrong in the attack command - resolved: was missing `RemoveFlagDoAttackProcessor` and hence `FlagDoAttack` components that prevents movement was always there.
  - [x] - BUG - Fix the `collect_coins` game - currently it is reaching maximum of inventory items.
  - [x] - Some mechanics in `Controllable` component to switch between more profile of keys - one for controlling the character, other for controlling the movements in inventory. Resolution: `toggle_controls` command where you can define new set of commands for keys.
  - [x] - Pressing ESC in main menu leads to exit dialog
  - [ ] - in ECS manager change `delete_component` to `ecs_remove_component` to distinguish that this is Esper call and not my call
  - [x] - fix the debug font as there is no space between letters
  - [ ] - initialized for ECS manager and then use ECS manager imports for scripts/console scripts instead of main. But checking the initialized global first.
  - [x] - fork old version of esper and modify it (2025-07-15)
  - [x] - add logging to Esper, move component class into the ecs (2025-07-15)
  - [ ] - for state screens prepare some layout base on resolution config
  - [x] - prepare some dummy pytest file 
  - [ ] - `gui.py` refactor, maybe use GUIContext to represent window, window_manager, etc. 
  - [ ] - translations - json key:value in file, based on config, the specified file will be used print(trans("Some_text"))
  - [x] - multiple flow for processors (processor groups) depending on game state (so that inventory can be implemented) (2025-07-15)
  - [ ] - Refactor all `core/scripts/*`. Import not `main` but `ECSmanager`. In `initalize` function check that ecs_manager is initialized. Import `main` only where it is really used, for example `exit` command.
  - [ ] - BUG - debug information upon hover raises error when trying to render the frame
  - [x] - GitHub actions clean pytest, doctest and Lint issues.
  - [ ] - Make messagess work. Sript `add_msg` is corrupted. Plan the necessary processors handling message queue.
  - [x] - Change the scenes that are single screended to use `screen_fill` parameter of `Camera` component in order to keep whole screen filled after resolution change. (2025-07-07)
  - [ ] - Settings screen option running in some dialog and having some Apply button. Problem that CHeckBox within UIWindow hiding is raising exception.
  - [x] - How to go back from the settings screen to the Game? resume button. (2025-07-07)
  - [ ] - dict_utils including getting dict from file as a package
  - [ ] - main.reinit() function do it more universal - select what all you want to reinit
  - [ ] - make the check of state changes optional with only warnings being displayed and not preventing the change of state completely.
  - [x] - adjust the progress bar based on the window resolution
  - [x] - rename `engine.new_game` to `load_scene`
  - [x] - pass progress bar form `load_scene` to `load_scene_from_file` to `load_scene_from_def`
  - [ ] - clear the `engine` code from unused things
  - [x] - rename `QUEST_START` event to `SCENE_START` event (2025-07-07)
  - [ ] - parameter that decides whether to show the loading progress - was there some time ago already, now gone
  - [ ] - console command that just toggles off the console + implement parameters to the commands not to toggle off console at the end to use with more complicated console scripts.
  - [ ] - toggle console without animation effect in an instance, one cycle without console and then back to the console - how to call all processors for one cycle
  - [x] - Start into empty console and run console script that loads the scene and everything - the complete load managed by the console script
  - [x] - prepare `load_scene` console command
  - [x] - prepare empty scene and load into it - just showing background picture
  - [ ] - Console hight should be dynamically calculated min(displayable_lines, display_lines from config)
  - [x] - BUG - After calling console_command `change_res` the exit screen is not displaying the exit dialog (the MENU)- chaos in states and menus (2025-07-16)
  - [x] - BUG - logs are emptied after the console `change_res` console command
  - [x] - BUG - console command `get_components` does not work properly
  - [x] - BUG - console command `get_processors` does not work properly
  - [x] - BUG - console command `set_value` does not work properly
  - [x] - Get rid of displaying console welcome message when console is re-initiated during for example changing of resolution.
  - [x] - BUG - after executing change_res console command, the state of the game is START_PROGRAM, also the console is not toggled off.
  - [x] - BUG - toggle console causing automatic keypresses after the console is toggled again - fixed by clearing the console keypressed cache during toggling.
  - [x] - BUG - `exit` console command does not end the game - fixed by allowing transfer from CONSOLE to END_PROGRAM state
  - [x] - BUG - `list` console command - registered commands go away after reinit of console
  - [x] - Console commands as script file - similar to game commands - initialize, keep list of commands ... Probably part of the Console solution ...
  - [ ] - comment properly the COnsole code - changing the app leading to revidion of text_params in the header and footer
  - [x] - get rid of timed - should be part of the config and not passed around as a parameter
  - [x] - change width of the console from separate function
  - [x] - implement reload in console - changing CLI, Paths, ... maybe just adjust the same init function ... using _INIT ...
  - [x] - remove WIDTH and HEIGHT, keep only resolution
  - [x] - GUI manager after calling init is deleting the background with the game - do it so that background is kept
  - [x] - console manager after init is deleting all history from console. Probably do some separate function `on_display_changed`
  - [x] - after reinit of the console, history is kept but the lines ar not divided correctly according to the width


## Features
  - [ ] Implement some shaders based on the video from DaFluffyPotato on youtube
  - [ ] Implement Showing weapons in the game
        - Once you go into inventory and select a weapon and press ACTION button, the weapon is automatically selected and armed.
        - Once you go into inventory and select an ammo pack and press action button, the ammo pack is automatically armed.
        - Create a new command for arming in Inventory.
         - But first recognize in RenderInventory if Weapon and if AmmoPack.

        - [ ] Implement `FlagShowWeaponary` with details about the displaying
        - [ ] Upon having `HasWeapon` component show the slots - for weapon and for generator
        - [ ] Upon having `WeaponInUse` component, show which weapon is selected
        - [ ] Drag weapon (`Weapon`) and generator (`AmmoPack`) from Inventory to weaponary

  - [ ] Implement inventory 
        - [x] Possibility to have different set of processors for different States
        - [x] Implement new component `FlagShowInventory`
          - can calculate the dimensions of inventory window based on `Camera` component (+reinit)
        - [x] Implement new command `toggle_inventory` that after pressing an inventory key creates/deletes `FlagShowInventory` component + manipulates the `Controllable` component - disabling the controls or assigning different commands to them
          - [x] in order to toggle inventory, I must be able that some keys should react on key up and not key down event. Otherwise the command will create and delete FlagShowInventory component many times before I lift my finger off the key.
        
        - [x] Prepare new command `toggle_controls` to enable/disable/exchange commands behind pressing of the keys
        - [x] Prepare new scene to test the inventory
        - [x] HasInventory must have also information about displayed inventory - apart from set also a list with 10 positions filled with `None`s.
          - [x] Modify `HasInventory` to have the information in a form of a list.
        - [ ] How to prevent pickable entity from being picked immediatelly after it was dropped?
        - [ ] Throw item out of inventory
          - [ ] Implement remove function in HasInventory to safely remove from categories. Add it to dict utils.
        - [ ] Show information about the item in the footer
        - [x] Prepare commands for moving around the items in inventory using the arrow keys.
           - [x] `toggle_controls` command must support also change in the key feedback schema 
        - [x] Drag also to the empty slots
        - [x] Adjust control component to support switching for alternate controls and control the inventory with arrows
          - [x] new methods in `Controllable` component. `set_control_cmds` and `revert_control_cmds`
        - [x] - Change the inventory so that `load_from_template` new command is used for change of controls. Prepare new templates for game controls and inventory controls.
        - [x] Do not show the debug information while dragging
        - [x] Show picture of item while dragging centered on the cursor

  - [ ] many custom ProgressBars available and can be sellected in the scene file by configuration - for example
  	`"progress_bar": ["gui:SimpleProgressBar", {"background": "splash_pyRPG.png", "bar": true}], // example how progress bar could be configured`

  - [x] BUG - DISPLAY["SHOW_FPS"] is not taking configuration from config.jsonc
  - [ ] new `ALL` option for cleanup actions - some new wrapper functions will be needed
  - [ ] Some problem with `tests/12_ai/simple/do_parallel.jsonc` when enemy approaches
  - [x] Show FPS also i fullscreen mode (config parameter)
  - [x] Branch - Fix console and make it more usable. It contains very old descriptions.
  - [x] Fix running in 1920x1080 fullscreen - how to tell video component to get the system configuration - to cover the full screen?

## To Do

  - [ ] `do_parallel` to support skipping of cycles so that some commands run once per some amount of ticks and meanwhile return some default value
  - [ ] prepare `test_bb_value_in` and `test_bb_value_not_in` as a faster alternatives to `test_bb_values` that is using potentionally slow json logic
  - [ ] blackboard having implicit value `self` referencing the entity ID or name - can be then used in all handlers
  - [ ] new command based on experience with `do_parallel` - `do_if_bb_test_true`
  - [ ] Behavior Tree and Behavior list - implementation of restart function - tree/list starts again from scratch. Useful for restart of the whole tree if some event comes.
  - [ ] Make scripts runnable from the console
  - [x] Rename quests to scenes. Scene is more common name for what the engine is defining in the json files.
  - [ ] Every game/test using scenes should be defined outside of pyRPG folders and only import pyRPG and use its parts. No direct changes in pyRPG folders and files.
  - [ ] Make scripts more nice - now they are using mainissing logging, missing description. Missing concept when to use commands and when to use scripts, make them work from console...
  - [ ] finish tests and json definitions for new commands

## Bugs
  - [ ] BUG - move_to command makes the NPSs to walk through the tiles
  - [x] BUG - entity is moving to the second point in the path not the first point in the path! That is causing problems when only chekcpoints are moved. Entity is not avoiding obstacles under those circumstances.
  
  - [ ] BUG - move_to_pos_target_vect - direction of movement (facing of entity is not being changed)
  - [ ] BUG - Problem with pushing entities into walls - eventhough map collisions are enabled. To be fixed.
  - [ ] BUG - debug processor works onlywith one camera
  - [ ] BUG - when restarting scene in the `collect_coins` game, there is loading screen in the background

  - [x] BUG - Progress bar is showing `number / None` - fix is problematic for unknown reason (closed 25.6.2025)
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
  - [x] Implement handlers into behavior tree definitons - handlers will just pu, is it ok? Mt some value from the event on the blackboard. Done - now handlers can be part of components (or basically anywhere in the scene definition. Only the engine code needs to be slightly adjusted). Script `set_bb_key` was prepared to set blackboard value and can be used in the handlers.

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

