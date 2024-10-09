# ECS experiments on RPG example
 
####

## Requirements

####

### esper - https://github.com/benmoran56/esper
  - Changes done in ESPER
    - New esper function for exclusion of some components on entity - get_entities_ex
    - Changed try_entity so that it returns (originally it yealded)

### pytmx - https://github.com/bitcraft/PyTMX

### lupa - https://pypi.org/project/lupa
  - for lua scripting

## Some solutions

####



>**Q:** How to fix moving into collision zone even if both entities have collision set?
>**A:** All movement (even corrective movements after collision) must be implemented as move command and pushed into command queue. Otherwise, by correction using lastx, lasty etc. entity will get stuck eventually.




## BUG - double use of Command Command factory
  1. `Controllable` component - contains `Command` called `reset_brain`
  2.  `GenerateCommandsFromInputProcessor` processor - following `Command` `reset_brain` is added into the command queue
    - `Command(name='reset_brain', params={'new_ai_struct': {'blackboard': {}, 'cmd_list': [{'line': 0, 'type': 'Behavior', 'command': ['move_vect', {'vector': [10, 0]}]}]}})`
  3. `CommandManager` manager
    - adds to _cmd_queue
    - registers `reset_brain` and `reset_brain_init` at `CommandManager` 
    - executes command
  4. `reset_brain` command - first call is ok
    - `cmd_ctx=None, new_ai_struct={'blackboard': {}, 'cmd_list': [{'line': 0, 'type': 'Behavior', 'command': ['move_vect', {'vector': [10, 0]}]}]}`
  5. `blist` brain
    - New set of commands in BList before translation is `self.commands=[{'line': 0, 'type': 'Behavior', 'command': ['move_vect', {'vector': [10, 0]}]}]`
    - List of commands after transformation by the command factory: `self.commands=[{'line': 0, 'type': 'Behavior', 'command': Command(name='move_vect', params={'vector': [10, 0]})}]`

  X.  `GenerateCommandsFromInputProcessor` processor - incorrect following `Command` `reset_brain` is added into the command queue
    - `Command(name='reset_brain', params={'new_ai_struct': {'blackboard': {}, 'cmd_list': [{'line': 0, 'type': 'Behavior', 'command': Command(name='move_vect', params={'vector': [10, 0]})}]}})`

    probaly it is that Command is mutable and system works with references
     - as a solution, namedtuple is imutable and should be ok to work with him


## TODO - fill in values from blackboard into the command definition
  - `"move_to_target", {"target": "player01"}` ... translated on ecs_mng level to `"move_to_target", {"target": 1}`
  - `"move_to_target", {"target": "^enemy"}` ... translated on ecs_mng level to `"move_to_target", {"target": "^enemy"}` ... specifically look for `enemy` key in the blackboard ... I would like this key to be substituted before execution of the command so that command does not need to parse the arguments.
  - maybe at the moment of creation of the component BrainAI - but at that moment the `enemy` key does not need to exist.
  - `target=global_bb.get(target, target)` ... first try to look on the blackboard and if not found use the input value. This might be problematic.
  - in the first cycle read the `target` ... `target = target if target[0] != '^' else global_bb[target[1:]]` ... have this in every command?
  - or give it somehow to execute command command_manager ... has cmd_ctx.global_bb
    - check params values that start with `^` and try to substitute by cmd_ctx.global_bb value
  - or better during putting it to the command queue!!!
    
    - *Below is not relevant* - you can get information if the command is firstly called from the context if the context exists (tick_count == 1)
    - idea - it is not relevant 
      - `btree_preocessor` calls `btree.get_command``
      - `btree.get_command` returns command and information if it is the first call of the command (change of action node) - done
      - information about the first command call is pushed together with the command, entity_id and generator to the `command_queue`
      - in the `process_commands` method, pass the `is_first_call` information to the `execute_command` function
      - `execute_command` is looking for the registered command and executes it with parameters.
       - here probably execute some `init` function and then the command
         - `init` command will fill all command parameters into the cmd_ctx.locals_bb
         - `command_fnc` will then be called with `**cmd_ctx.local_bb` to fill in the parameters
     - or moving the init logic to `add_command` might be possible.

      - get from generator if the command is the first command call
      - if yes, 
        - translate the values using global_bb keys
        - store all parameters into local_bb
        - run the command init function that will fill additional information into local_bbs
        - run the command function with parameters **local_bb

     - it is now implemented but it is not elegant
     - try to use classes
       --> `btree`` is returning tuple with name and params
       --> component `BTreeAI` is creating tree with commands as objects using the factory
         --> probably `command_manager` will have function that creates and returns instance of `Command` object *this need some more thought - coupling component with command manager*
       --> `get_command` will return Command instance ... same
       --> `add_command` will put Command object into queue
       --> `process_commands` will pop command from queue
        --> if the command has some context
          --> `notify_command_start` will calculate the statistics of the tree ... same
          --> `execute_command`
            --> check blackboard for substitution ... ok
            --> run `init` - this can be handled internally, no specific code for that
              --> command class has separate `init` function, empty if not needed
                --> can call super.process() and upper class will identify the first run and execute the init code automatically
              --> no local_bb needed, everything is persisted in the instance
            --> run `command`
        --> if the command has no context????
          --> such command cannot call init function
          -->
  
  **NEXT STEPS**
    - probably continue finetuning the functional approach
      --> functions `init`, `process` and `initialize`
      --> solve how to recognize commands and their behavior with context and without context
        --> maybe additional functions `process_wo_ctx` and if not registered then show error that it cannot be run without ctx


  **ADVANTAGE**
    - implicit call of init() function within the Command parent class super.process() will check the context and the first tick
  **PROBLEMS**
  ??? Input commands will be objects???? How to make it work
    --> controllable component would need to have reference to command factory that will create the command
  ??? How to call such command from COnsole?
    --> factory will create command from text
    --> such command will be passed to queue

## Other idea - commands as classes
  - behavior tree node is parent class. Command is child of Behavior class and it is an instance.
  - command instance is created at the moment of creation of the tree
   - command instance has `tick()` method
   - on `btree.get_command` we return `behavior.tick()` method that is put into the command queue
   -

## TODO - Rethinking Commands - BTrees and Brain
  - `CommandContext` - abstract class representing context of currently running command
    - information from other commands from the same BTree
    - ticks and times
    - Context is valid for both Btree and Brain. BTree's context is called BTree blackboard, Brain's context can be different implementation. But always need to provide the information guaranteed and defined by the CommandContext class.
    - on init remove necessary sub-classing
    - ... ... ... ... ... ...
    - check that the tree is valid - all leaves are behavior nodes
    - Packages
      - Core
        - Commands
          - `cmd_generator.py`
          - `cmd_context.py`
          - `cmd_status.py`
          - Generators
            - BTree
              - `btree.py`
              - `blackboard.py`
            - BList (formal Brain)
              - `blist.py`
                - ListNode
                  -[(idx=0, on_fail_goto_idx=None, cmd='...'), ...]
              - `blackboard.py`
          - Commands
            - `dummy_command.py`
            - ...
  -`Btree` module -> used in BTree component

## TODOs
  - filters to be independent on component, so that those can be used also within commands and not only processors

## TODOs - Behavior Trees for AI implementation, commands and brain
  - special commands for init and for complete functions are problematic, because they return SUCCESS or FAILURE and by doing so, closing the whole node. Hence added result parameter for selected commands that would forcefully return RUNNING
  - rewrite commands so that no need of `__init__.py` - registration of the new command (same as scripts)
  - rethink using world variable within commands - better to use command_manager -> ecs manager for any manipulation with the world
  - think about commands to be available for usage in both Brain and BTree structures
  - change Brain so that it uses blackboard similarly to BTree
  - think about BTree as a template with variables
  - map manager to return path and to return visibility

## TODO

## GUARD behavior

### MoveAlongThePathUntilEnemySpoted tree command
  *Goal*
    - Moves entity along the path specified by points until enemy is spoted
  *Results*
    - `SUCCESS` - enemy has been spotted
    - `RUNNING` - moving along the path
    - `FAILURE` -
  *Params*
    - `enemy` - who should be considered as an enemy
    - `range` - how close must enemy get to be spotted
  *Steps*
   - Save enemy position component
   - Save entity position component


   - Check if the distance to enemy is short and facing the enemy
     - if YES, 
       - finish with `SUCCESS`
     - if NO,
       - finish with `RUNNING`


## HUNTER behavior 

### FindTarget command/tree
  *Goal*
    - Returns target entity and stores it to the bb as target_entity.
  *Results*
    - `SUCCESS` - target was found and saved on the bb
    - `RUNNING` - searching for target in progress
    - `FAILURE` - target not found

### Blackboard
  - ma scope urceny pro vsechny nody stromu
  - ma scope urceny pouze pro jeden konkretni behavior
  - bylo by super to nejak odlisit a ten prostor pro jeden konkretni behavior (running behavior jako samostatna trida?) automaticky cistit, v ON_COMPLETION
  
### MoveToTargetRange tree command
  *Goal*
    - Moves entity close to the target (defined by range) and faces the target
  *Results*
    - `SUCCESS` - target is in range
    - `RUNNING` - on the way to the target
    - `FAILURE` - cannot reach the target
  *Params*
    - `range` - how close to get to the target
    - `update_target_position_ms` - how often to ask about the targets new position, the shorter the time is the harder the opponent is.
    - `max_hunt_time` - how long to hunt the target, if longer, finish with the failure
  *Steps*
   - Save target position component
   - Save entity position component
   - Save the time of first call
   - Save the time of last update of the target position

   - Check if the `MoveToTargetRange` is running too long or target ceise to exist
     - if YES,
       - finish with `FAILURE`

   - Check if the distance is closed (you are in range)
     - if YES, 
       - `execute command` face the target
       - finish with `SUCCESS`
     - if NO, continue hunting the target
       - `execute command` move command
       - finish with `RUNNING`

### Attack command/tree
  *Goal*
    - Use weapon on the current position/direction for given time period
  *Results*
    - `SUCCESS` - time `attack_time_ms` is over
    - `RUNNING` - attack in progress
    - `FAILURE` - no more ammo or entity destroyed or target destroyed
  *Params*
    - `attack_time_ms` - how long to generate the attack commands
  *Steps*
    Save target health component
    Save entity health component

    Check, if entity/target destroyed
      - if YES,
        - finish with `FAILURE`

    Check, if within `attack_duration_ms`
      - if YES,
        - assign `FlagHasAttacked` component to entity
        - finish with `RUNNING`
      - if NO,
        - finish with `SUCCESS`

## Questions
  - [ ] should position fixing be part of collision system or in separate component/processors?

### Scene Manager
  - It issues commands to the other managers - serves as an input for them telling them what to load/delete.
  - From that perspecive QuestManager is not on the same level as the other managers. It is their boss.
  - Maybe the whole content of QuestManager should be part of the engine
  - QuestManager contains references to other managers even now 

### Scene/Phase as description and no class/object/instance
  *All is described in MIRO*
  - [x] Create `EventManagerEx` that processes the event actions
  - [x] Transform `scene` module to `QuestManagerEx` + start filling `EventManagerEx` with handlers
  - [x] ensure `engine` module is updated
  - [ ] `delete_processor` method should probably call finalize method of the processor
  - [x] `delete_template` method not implemented
  - [x] `delete_handler` not implemented in `EventManager`
  - [ ] check that prereq scenes are not loaded if those are already loaded

### Processing templates
  1/ Parse the scene file and store the templates there to the ecs_manager
    - store the dict with template into following dict `self._template_definitions[template_name]`
  2/ When creating entity and template is used:
    a/ Check, if template is already loaded in ECS manager and hence was part of the scene. If yes, use this template and continue.
    b/ If no such scene exists, try to load it from the `ENTITY_PATH`
    c/ check if () are part of the template name. If yes, expect parameters vars in the template definition. If vars not found, error.

### Fade-in Fade-out effect POC
  - based on event - script
  - based on global brain - command
  - as a processor (weather)

### Generate sound FX upon collision
  - [x] generate
  - [ ] document
  - [ ] find some sound files

### Generate music
  Music will start as reaction on some event. So we need to prepare a script that uses sound manager. Cannot be implemented as processor as processor is called many times and I want to start the music only once at the beginning and then change it upon some event.
  - [ ] implement script that starts music

### Load game screen
  When going from menu to the game - start of init game

### Re-doing of MAIN and ENGINE modules - Manager classes implemented
  **Outstanding TODOs**
    - [x] Correct ending of program
    - [x] Possibility to run the game without any console
    - [x] Pause game/menu when console displayed
    - [x] Save path once the game is loaded and start from that path when again selecting file
    - [x] Buttons and windows are active when console is displayed, need to be disabled
    - [x] Make nicer background animation implementation in the gui manager - rename, multiple folders, configurable paths, return number of animation frames from load_animation function, etc.
    - [x] Backup and clear the unused manager and main and engine classes
    - [x] Make console nicer - get rid of dummy data and display statistics from ECS manager + state + memory usage
    - [x] Make the diagram and implement Menu abstract class
    - [x] Retest all the test scenes
      - [x] for collision test 4 fix all the errors and dialogs are not displayed and not correctly cleared - RuntimeError: dictionary changed size during iteration
    - [ ] Document the changes in this document
    - [ ] Clear the console and menus upon exit
    - [ ] Get rid of debug as parameter starting in main and ending in processors
    - [ ] Think how to implement MenuManager
    - [ ] Spread managers to the respective directiries - MenuManager to the menus, QuestManager to scenes etc.

### Improve collisions - NPC entities can walk around each other while hitting themselves
  - Different Entities have different collision behavior
    `Collidable`
      - `ignore_position_fix`-> `do_not_generate_position_correction_for_others_except{}`... default `False` a.k.a. {empty set} ... only entities in the set will be corrected
      - `ignore_collision_with` ... default `[]`
      - `no_position_fix_for_self` ... default `False` a.k.a. {empty set} ... only entities in the set can push me

      - position correction can be either in straight or walkaround mode
        - Player should be in `straight` mode, i.e. not walking around enemies when colliding into them
        - Stone should be in `straight` mode, i.e. pushing the player straight when colliding into him/her
        - NPCs should be in `walkaround` mode, i.e. trying to avoid collision with obstcles proactivelly
      - `walkaround_position_fix_mode` ... default `True`

    1. Lava
      - must produce collisions so that damage can be processed
      - other entities must be able to walk on lava - correction in position must be ignored for other entities
      *Result*
        `Collidable`
        `DoNotGeneratePositionCorrectionForOthers` a.k.a. `Walkable` a.k.a. not `Pushable`
    2. Player
      - when other entities are colliding into Player, he stays steady and is not moving
      - when Player is colliding into other entities, those entities are moving, player is pushing them
      *Result*
        `Collidable`
        `DoNotGeneratePositionCorrectionForSelf` a.k.a. not `Pushable`
    4. Arrow
      - when arrow hits enemy the collision is recorded
      - when arrow hits Player no collision is recorded
      *Result*
        `Collidable`
        `IgnoreCollisionWithPlayer`
    3. Stone
      - when player collides into Stone, it moves
      - when other entity collides into stone, it stays steady
      - when player collides into stone, neither player nor stone are trying to walk around each other
      *Result*
        `Collidable`
        `GeneratePositionCorrectionOnlyFor[]` a.k.a. `PushableOnlyBy[]`


### Add debug processor - you will put any condition there and if the condition is fulfilled then the game will stop and you will be able to check the state

### Component classes can be data classes
  - either built-id @dataclass or pydantic(has verification of data functionality)
  - https://youtu.be/vRVVyl9uaZc

### Better loading of processors and components using plugin pattern and importlib
  - very nicely described in youtube video https://youtu.be/iCE1bDoit9Q
  - no longer adding imports when new component and/or processor is added - instead importlib can be used
    
    *Currently*
    - `scene.__init__` -> read the list of processors into scene.processors
    - `scene.__init__` -> for all processors `engine._create_processor(proc str)`

    *Newly*
    - `scene.__init__` -> read the list of processors
    - `scene.__init__` -> calls `engine.load_processors(list_of_processors)`
    - `engine.load_processors`
      - `for all processors`
        - get the processor class
        - `processor = importib.import_module(processor_class_module_path)`
        - get the call parameters
        - add to the world

    - read the list of processors from json
    - loader.load_processors(list_of_processors)
      - processor = importib.import_module(processor_name)
      - processor.initialize()
         - factory.register(proc name, proc class)


## NEW SYSTEMS - START ###################################################

BETTER

remove unnecessary pickup and Position should be removed now, not needed.

 - RenderDataFromParent(animation + position) - all part of Render system, nothing else needed

 -----

RenderPosition - position used for rendering the animations
Position - position on the map

All components with RenderableModel should have `RenderPosition(x, y, dir_name)`.
All components with RenderableModel and without Position component should have RenderPosition

 -> if entity has Position, it is used for Rendering -> `PerformRenderModelProcessor` - draws only real entities with position
 -> `NewRenderArmedWeaponProcessor` - draws WeaponIsUsedBy + RenderPosition
 -> before rendering add RenderPosition ->
   -> WeaponInUse + Position + HasWeapon + FlagDoMove -> on active weapon add `RenderPosition(x, y, dir_name)`




########################
### how to synchronize Render actions on Weapon from Fighter - Render System - NewGenerateSyncRenderActionProcessor, NewPerformSyncRenderActionProcessor, NewRemoveFlagSyncRenderActionProcessor

# Copy Render action info

## For Wearables - Iterate all entities with CanWear + RenderModel - assign render info to all clothes
CanWear + RenderModel -> iterate can_wear and get entitiy IDs -> for each assign FlagSyncRenderAction(render_model.action, render_model.last_frame)

## For Weapon - Iterate all entities with WeaponInUse + RenderModel - assign fighters render info to his active weapon
figher.WeaponInUse + fighter.RenderModel + fighter.HasWeapon -> weapon_in_use.type='bow' -> has_weapon.get('bow') -> bow_entity.add_component(FlagSyncRenderAction(render_model.action, render_model.last_frame)

## For Ammo - Iterate all entities with AmmoInUse + RenderModel - assign fighters render info to his active ammo
figher.AmmoInUse + fighter.RenderModel + fighter.HasWeapon -> ammo_in_use.type='bow' -> has_weapon.get('bow') -> bow_entity.add_component(FlagSyncRenderAction(render_model.action, render_model.last_frame)

# Make some processor that will synchronize the weapon RenderableModel with parent RenderableModel

## For Wearables - RenderableModel, FlagSyncRenderAction(action, last_frame) -> renderable_model.action =flag_sync_render_action.action, ...

## For Weapon - RenderableModel, FlagSyncRenderAction(action, last_frame) -> renderable_model.action =flag_sync_render_action.action, ...

## For Ammo - RenderableModel, FlagSyncRenderAction(action, last_frame) -> -> renderable_model.action =flag_sync_render_action.action, ...

##########################

### 1. TODO - Adjust Pickup System - keep Position, add IsPickedBy() - *DONE*
  - current `PerformPickupProcessor`
    - keep `Position` - *DONE*
    - create new `IsPickedBy` - *DONE*

### 2. TODO - Add Position System - to prepare NewIsPositionParentFor - *DONE*
  - new position system ???, new processor `NewGenerateParentPositionProcessor` - *DONE*
    - `HasInventory` + `FlagHasPicked` -> add `NewIsPositionParentFor(set)`

### 3. TODO - Adjust Collision System - to ignore IsPickedBy for collisions - *DONE*

### 4. TODO - Enhance Render System - do not display entities that have IsPickedBy() - *DONE*

### 5. TODO - Enhance Position System - to prepare NewIsPositionChildOf for armed weapons - *DONE*
  `FlagWasArmedAsWeaponBy` -> `NewIsPositionChildOf`
  - new processor to the position system `NewGenerateChildPositionProcessor`

### 6. TODO - Enhance Position System 
  - create new processor - `NewGenerateChildPositionUpdateProcessor`
    `FlagDoMove` + `IsPositionParentFor([2,3,4])` + `Position` -> assign `FlagAdjustChildPosition(new position)` for [2,3,4]

  - create new processor - `NewPerformChildPositionUpdateProcessor`
    `FlagAdjustPositionFromMaster(new position)` + `Position` + `UpdatePositionFromMaster()` -> change the position

  - create new processor `NewRemoveFlagAdjustChildPositionProcessor`

### 7. TODO - NewGenerateChildPositionUpdateProcessor - would be better if IsPositionParentFor contains only couple of entities that really need to be updated 

### 8. TODO - adjust init of components to create also other necessary components

### 8. TODO - update documentation of all systems

### 9. TODO - retest pickup

### 10. TODO - implement  renderer for weapon processor


### 2. TODO - Generate projectile

*Pickup system*
 - weapon in inventory

*Arm Weapon system*
 - Weapon(type) - > type translates to action and idle_action using Weapons static dictionary
 - FlagHasArmedWeapon(weapon entity)
 - `WeaponInUse(type)` - no longer a flag but permanent component on the fighter

*Arm Ammo system*
  - `AmmoInUse(entity)`?????

*Attack system*
 - command Attack -> new flag add `FlagDoAttack` *DONE*
  **GENERATE THE PROJECTILE AT GIVEN FRAME**
  - fighter.RenderableModel.is_action_frame must be True - new flag that can be verified and checked in Animation system
  - must have valid weapon (WeaponInUse) and valid ammo (AmmoInUse) -> Arm Weapon system and Arm Ammo system must ensure validity of those flags
  - generate some kind of flag based on animation phase `FlagCreateFromFactory` on ammoPack

*AnimationSystem*
 **TODO** animation system returns `FlagIsAnimationActionFrame` flag
 - `PerformFrameUpdateProcessor` -> set the `FlagIsAnimationActionFrame` flag
 - `PerformActionAnimationProcessor` -> set the proper action to RenderableModel
  - `FlagDoAttack` + `WeaponInUse` -> use action
  - no `FlagDoAttack` + `WeaponInUse` -> use idle_action


## arm ammo how to effectivelly add ammo to existing entity of ammo
 1. has weapon check generator based on key in AmmoPack

 1. has_weapon.get_component factory
everything that is in inventory - `NewIsInInventory(path in categories)`

NewIsInInventory + AmmoPack 
  all ammo packs AmmoPack
    that belong to the weapon AmmoPackBow
  - HasInventory[ammo1]
    - categories[ammo][bow][wooden_arrow] : [ammo1]
  - pickup ammo2
  - HasInventory[ammo1, ammo2]
    - categories[ammo][bow][wooden_arrow] : [ammo1, ammo2]
  - component ArmedAs("bow")
  - all that are AmmoPack, Armed,

### technical debt - FlagHasPicked ... in case entity picks more other entities in one cycle only the last one will be recorded - store field there
 - but if pickup is one at the time, it can work ok

### can pickup 2 entities at the same time? Ideally one entity in one cycle and the other in second cycle - to avoid problems in other processors like arm ammo system
  - scenario when entity picks 2 ammo packs in one cycle and both have picked flag on them and the processor is only covering one pick for flag Is about to arm ammo

### pickup and HasInventory - some items might be picked up not as separate entities but might be counted together
  - how to achieve that nicely?

  - pickup ammo into inventory  ... some pickup processor
  - categorize the pickedup entity ... What processor should do that? FlagWasPickedBy + AmmoPack(weapon, category) -> picker and inventory
    - seems that `PerformArmAmmoProcessor` has all information to do that
    - either there is already some entity or there is None
      - if there is none add our new entity
      - if there is existing
        - get the remaining ammo on the entity factory
          - remember the remainder in cathegories and update it?
          - get it from factory?
        - add it to the new factory
        - get rid of the old one
  - sum all the packs together and leave the current one
  - remove the obsolete pack from inventory and from categorization and destroy it 
  - arm the new pack

### Mouse controlls
  - FlagDoMove will contain the destination and all the necessary information to travel there. The flag will be not deleted at the end of the cycle but only at the time when entity
  arrives at its target or after some timeout (also counted in the FlagDoMove component)
  - Perhaps new component and processor for mouse movement `FlagDoMoveTo`

### Teleport system
  - do it by using teleport command. For a start it will be simple change of position but in future there can be animation effect in the command.
  - it would be also good to pass Position component and further components of the entitydirectly into the command so that within the command there is no need to ask for the position component again ...
  - maybe the same can be done with movement and other commands, pass the component directly there to speed things up


### Redo *COLLISION SYSTEM* to use FlagHasCollided with list of entities
  - New component `Collidable` was created. Component contains correction for the entity centre (specified by `dx` and `dy` arguments) and length and with of the collision zone (specified by `x` and `y` parameter)
  - New `NewGenerateCollisionsProcessor` that will substitute `CollisionEntityGeneratorProcessor` and generate `FlagHasCollided` component
  - New component `FlagHasCollided`
    - contains set of tuples representing the collisions `(entity, reference to Position component)`
    - might as well calculate the correction vector - math involved
    - TODO generate collision event in the new processor
    - TODO `NewRenderDebugProcessor` that would show collisions on the new components. Or use the existing one
  - *Collision with non-movable object* - object will not move after collision - implememted
  - *Collision with movable object not pickable or nothing similar* - fix of collision can be suppressed by parameter in Collidable component
  
  - TODO rename `CollisionDamageProcessor` to `GenerateDamageProcessor`
  - TODO get rid of `Collidable.has_collided` and `Collidable.col_events`. Both will be substituted by list of entities in `FlagHasCollided`
  - TODO prepere `RemoveFlagHasCollidedProcessor`
  - TODO adjust `CollisionDeletionProcessor` to use `FlagHasCollided` instead of `collision.has_collided`
    - change the way of storing the collisions
      - currently, stored directly in `Collidable` component as a list of entities
      - newly, sotre in separate flag component `FlagHasCollided` + keep also details about the collision - dx, dy, information about collision component, position component from the other entity in order to be able to resolve the collision of the object only using information contain in this event and no need to get the information dynamically from the other entities.


  - TODO get rid of old `CollisionEntityGeneratorProcessor` 
  - TODO introduce parameter that will toggle collisions only on Camera screen or in all the game regardless if on screen or not
  - *TODO* so that some particular collisions are ignored - arrow ignors the shooter
     - new parameter of `Collidable` `ignore_collision_wit`h that can be used in `GenerateEntityCollisionsProcessor` to ignore creation of collisions? But this is not ECS approach
     - ECS approach would be to assign some new flag `IgnoreCollisionWith` and as parameter list of entities. So projectile will have this assigned
     - new processor that would take all with FlagHasCollided + IgnoreCollisionWith and remove the collision before processing ...



### QUESTIONS
  1. Do I want to have weapon/wearable/ammo armed/weared and at the same time present in inventory?

### USE CASES to fill

  #### Weapon/Wearable/Ammo
  1. Pick up weapon/wearable/ammo and arm/wear it if no other weapon/wearable/ammo is already armed/weared - OK
  2. Pick up weapon/wearable/ammo and keep it in inventory only if other weapon/wearable/ammo already in use - OK

  #### Sword entity contains AmmoPack + Factory + Weapon component at the same time - is the system able to arm it properly?
  Sword entity is picked up by *PICKUP SYSTEM* and placed in the Inventory with `FlagPickedBy(picker)` component. Entity is stripped from camera/position etc components.

  1. There is place in HasWeapon for slash weapon and place for generator
    - Sword is added to a weapon by *ARM WEAPON SYSTEM*, in case there is no weapon armed
    - Sword is added to ammo by *ARM AMMO SYSTEM*, in case there is no generator armed
    - Now Sword is in HasWeapon.weapon, HasWeapon.generator and in Inventory

  2. There is no place in HasWeapon neither in slash weapon nor generator
    - Sword is not added to HasWeapon by *ARM WEAPON SYSTEM* as weapon
    - Sword is not added to HasWeapon by *ARM AMMO SYSTEM* as generator
    - Sword remains only in inventory

  3. PROBLEMATIC: There is place in HasWeapon.weapon but no place in HasWeapon.generator (fist fighting - no weapon, but fist is generating collisions)
    - Sword is added to HasWeapon by *ARM WEAPON SYSTEM* as weapon
    - Sword is not added to HasWeapon by *ARM AMMO SYSTEM* as generator - weak fist generator stays
    - Sword is in inventory and weapon and not as generator
    HOW TO SOLVE THIS:
      - **cannot be generator without weapon** - do not allow assignment of generator in case there is no weapon - adjust *ARM AMMO SYSTEM*
      - can be weapon without generator - example is bow without arrows
  
  4. PROBLEMATIC: There is place in HasWeapon.generator but no place in HasWeapon.weapon (generator depleted - some sword is destroyed and cannot cause harm anymore)
    - Sword is not added to HasWeapon by *ARM WEAPON SYSTEM* as weapon - previous destroyed weapon stays
    - Sword is added to HasWeapon by *ARM AMMO SYSTEM* as generator
    - Sword is in inventory and as generator and not as weapon
    HOW TO SOLVE THIS:
      - there can be weapon without generator (bow without arrows)
      - mark somehow special entity that must be armed weapon + generator at the same time or not at all - new component `WeaponWithGenerator()`
      - new processor `xxx`
        - get `WeaponWithGenerator` + `FlagPickedBy` + `FlagWasArmedAsAmmo` + not `FlagWasArmedAsWeapon` - remove from generator
        - **do change in *ARM AMMO SYSTEM* - test if `WeaponWithGenerator` AND not `FlagWasArmedAsWeapon` do nothing and keep it in inventory only**
  
  #### New Pack component and *UNPACK SYSTEM* - usable for trunks etc.
    - Pickable, Pack, Position, Collidable
    - Pack component can contain 
      - list of entities(weapon, generator - both without position)
      - parameter if automatically extract or not

    - *PICKUP system* adds the component to the inventory
    - new extract processor will go through all Pack, PickedBy(picker) and extract them in case the Pack.auto_extract == True
      - put all entities to the inventory
      - put flag `PickedBy(picker)` to all of the entities inside so those can be processed further by other systems (weapon, wearable)


  #### How to change weapon (for example by command)
  #### How to drop weapon (for example by command)

### Teleport system
  - GenerateTeleportationProcessor FlagHasCollided + Teleport comp -> FlagForTeleportation(position and key)
  - CalculateTeleportationProcessor - FlagForTeleportation + teleportable + position ... change the position
    - need to check the inventory which is not nice but needs to be done ... try/except
  - RemoveFlagForTeleportationProcessor

### Temporary component and processor integrate as part of destroy system
  - `GenerateDestroyedProcessor` will assin `IsDestroyed` component
  - `RemoveDestroyedProcessor` will remove entities with `IsDestroyed` component after some TTL - copy from Temporary com and processor
  - this will have effect on projectiles that are using `Temporary` - how to solve this?

### Processor has its prerequisities as part of the Processor class
  - later when processors/systems are defined as part of scene, we can check those dependencies
  - create new wrapping function that is putting processors into the world - with every put there is check if dependency is kept


### Redo *PICKUP SYSTEM* to use new FlagHasCollided component

  Pickup only works if `Pickable` on one side and `Inventory` on the side of the picker. The result of this system is entity in inventory with flag `FlagPickedBy(picker)`. From here other systems can process the picked entity and wear it / arm it / or keep it as it is. This is the aim of other systems - *WEAR SYSTEM*, *ARM WEAPON SYSTEM*, *ARM AMMO SYSTEM*.

  - new processor `GeneratePickUpProcessor` processing `Pickable` + `HasCollided` and assigning new component `FlagIsABoutToPickEntity(x)` to all entities
  - new processor `PerformPickUpProcessor` processing `Inventory` + `FlagIsAboutToPickEntity(x)` and assigning new `FlagPickedBy(picker)`  to the entity that is being picked
    - entity is cleared from some components and added to the Inventory
  - new processor `RemoveFlagIsAboutToPickEntityProcessor` and `RemoveFlagPickedByProcessor`

### Redo *WEAR SYSTEM* to use new FlagPickedBy(picker) component

  The new *PICKUP SYSTEM* manages moving of the wearable component to Inventory. There it stays, or is weared if possible - i.e. the picker has `CanWear` component and empty slot for wearing.
  NOTE: The *WEAR SYSTEM*, *ARM WEAPON SYSTEM*, ** ... can be applied all at the same time - so one entity can be armed and weared. Is that ok or not??? Seems to be good for Sword that is both Wepon and Weapon Generator...

  - new processor `GenerateWearProcessor` processing `Wearable` + `FlagPickedBy(picker)` adding tag `FlagToWear(wearable entity)` to the picker
  - new processor `PerformWearProcessor` processing `FlagToWear(wearable entity)` + `CanWear` (+ `Inventory` - due to the logic, entity having `FlagToWear` must also have `Inventory`. `Inventory` can be used later for removing the entity from inventory when successfully weared) and produce `FlagHasWeared(weared entity)` to the picker if entity was successfully weared od `FlagWasWeared(wearer entity)` to the wearable entity??? Or both?
    - the flag `FlagWeared` on the wearable entity would be useful in case we want to introduce `ScorableOnWear` component and *WEAR SCORE SYSTEM* to count score for wearing something.

    - now here I need information about wearable.bodypart in order to check if given bodypart is weared or not. Data needed:
      - Wearable.bodypart (to know which bodypart to wear)

    - 2 options:
      - get Wearable component from the wearable entity that is passed in `FlagToWear` component
      - pass the wearable.bodypart in arguments of `FlagToWear`

    - in success, the flags `FlagHasWeared(weared entity)`, `FlagWasWeared(wearer entity)` are assigned
    - in case wearable.bodypart is already filled by some other entity, keep the wearable in the inventory

### Redo *ARM WEAPON SYSTEM* to use new FlagPickedBy(picker) component

  The new *PICKUP SYSTEM* manages moving of the `Weapon` entity to Inventory. There it stays, or is armed, if possible - i.e. the picker has `HasWeapon` component and empty slot for the weapon.
  NOTE: The *WEAR SYSTEM*, *ARM WEAPON SYSTEM*, ** ... can be applied all at the same time - so one entity can be armed and weared. Is that ok or not??? Seems to be good for Sword that is both Wepon and Weapon Generator...

  - new processor `GenerateArmWeaponProcessor` processing `Weapon` + `FlagPickedBy(picker)` adding tag `FlagToArmWeapon(weapon entity)` to the picker
  - new processor `PerformArmWeaponProcessor` processing `FlagToArmWeapon(weapon entity)` + `HasWeapon` (+ `Inventory` - due to the logic, entity having `FlagToArmWeapon` must also have `Inventory`. `Inventory` can be used later for removing the entity from inventory when successfully armed) and produce `FlagHasArmedWeapon(weapon entity)` to the picker if entity was successfully weared or `FlagWasArmedAsWeapon(has weapon entity)` to the weapon entity??? Or both?

    - now here I need information about weapon type in order to check if given weapon type is already armed or not. Data needed:
      - Weapon.type (to know which weapon to arm)
    
    - 2 options:
      - get Weapon component from the weapon entity that is passed in `FlagToArmWeapon`
      - pass the weapon type in arguments of `FlagToArmWeapon` (weapon type)

    - in success, the flag `FlagWasArmedAsWeapon` on the weapon entity would be useful in case we want to introduce `ScorableOnArm` component and *ARM SCORE SYSTEM* to count score for wearing something.
    - in case type of weapon is already armed, keep the weapon in the inventory

### Redo *ARM AMMO SYSTEM* to use new FlagPickedBy(picker) component

  The new *PICKUP SYSTEM* manages moving of the `AmmoPack` entity to Inventory. There it stays, or is armed, if possible - i.e. the picker has `HasWeapon` component and empty slot for the ammo.
  NOTE: The *WEAR SYSTEM*, *ARM WEAPON SYSTEM*, *ARM AMMO SYSTEM* ... can be applied all at the same time - so one entity can be armed and weared. Is that ok or not??? Seems to be good for Sword that is both Weapon and Weapon Generator...
  NOTE: Cannot have HasWeapon.generator without HasWeapon.weapon on particular weapon type

  - new processor `GenerateArmAmmoProcessor` processing `AmmoPack` + `FlagPickedBy(picker)` adding tag `FlagToArmAmmo(ammo_pack entity)` to the picker
  - new processor `PerformArmAmmoProcessor` processing `FlagToArmAmmo(ammo_pack entity)` + `HasWeapon` (+ `Inventory` - due to the logic, entity having `FlagToArmAmmo` must also have `Inventory`. `Inventory` can be used later for removing the entity from inventory when successfully armed) and produce the following

    - **in case there is no weapon armed, do not arm Ammo** That is why `PerformArmWeaponProcessor` must happen before `PerformArmAmmoProcessor`

    - **test if `ArmAmmoOnlyWithWeapon` AND not `FlagWasArmedAsWeapon` do nothing and keep it in inventory only**


    - now here I need information if ammo_pack.type = has_weapon generator type and hence if I can Arm the AmmoPack. Data needed: 
      - **ArmAmmoOnlyWithWeapon true/false** - if True and **NOT** `FlagWasArmedAsWeapon`, do nothing and keep it in inventory only
      - AmmoPack.weapon (to know which weapon I am trying to arm ammo to)
      - AmmoPack.type (to check if the same type is already armed)
      - Factory.max_units (to increase the units if the same type is already weared)
      - Factory.current_units (to increase the units if the same type is already weared (max-current))

    - 2 options:
      - get AmmoPack and Factory data from ammo_pack.get_component ...
      - pass the necessary data in arguments of `FlagToArmAmmo` (AmmoPack.weapon, AmmoPack.type, Factory.max_units, Factory.current_units - the last to can be passed as units_to_transfer or something like that)

    - in success (no previous ammo pack armed), add component `FlagHasArmedAmmo(ammo_pack entity)` to the picker, if entity was successfully armed + `FlagWasArmedAmmo(has weapon entity)` to the ammo_pack entity
    - in case same type already armed, add component `FlagHasArmedAsAmmo(ammo_pack entity)` to the picker, if entity was successfully armed + `FlagWasArmedAsAmmo(has weapon entity)` to the ammo_pack entity + destroy the new ammoPack entity and keep the old one armed (component `FlagFactoryDepleted`)
    - in case different type is already armed, do nothing and keep the AmmoPack in inventory as picked only

## NEW SYSTEMS - END ###################################################


### Weapon skill
  - Every weapon type has skill level attached (bow, sword,...) - `HasWeapon` entity implements that
  - Skill is based on number of hits
  - Skill influences the damage caused by the weapon - damage multiplicator
  - Skill is calculated based on FlagHittedBy - calculate score if entity is Scoreable and originator has Score component
### Make Spellcast work - no weapon, only AmmoPack (virtual weapon needed)
  - rename actions - spellcast, shoot, slash, thrust, move (walkcycle), expire

### Make spike work

### Get spritesheet for quiver and for sticks
### If AmmoPack is in inventory and the same AmmoPack type is put in inventory - one entity should disappear and arrows should be on one heap
### Score counting, experience counting

### Branch 'Dying should be possible in all directions'
  - prepare model animation of dying for all directions - for darkmale it is done
  - find another word instead of die - I want this animation to be used with any object being destroyed - `expire`
  - rename all the die occurences and use `expire` instead - done

### make it possible to change the resolution within the game
  - used by Camera component - camera should have some possibility to define it as reference to screen variable
  - for example x : 'RESOLUTION_X div 2 - 10', if RESOLUTION_X is available for Camera component then we can run eval() and that is it
  - but same as with entity -alias we want to preprocess the data comming from the scene - translate to real data so the components do not need to handle this
  - so do this translation somewhere else? create_component function in init calls translate fction that already is doing the translation for aliases
  - put config dict as reference to create entity. And then use eval on every parameter for creation of the component
  - but eval('hello') will not work - so use try eval if fail then use the original value - TypeError if we are evaluating something else then string, NameError if we are evaluating something that is not known

### Why is lua not needed and how the console scripting works - Put some words above - about console scripting in python
  - lua is complication when all is in python already
  - the only advantage of using lua is that you can write for cycle directly on one row in the console
  - lua scripts are more complicated because they need to use functions that translate from Python structures to lua structures
  - python scripts are powerful and no additional functions needed
  - nevertheless, the lua support stays in the console and can be used if needed
  --- implemented
  - python scripts can be called with parameters
  --- TODO
  - default .py suffix add automatically
  - prepare interesting scripts with parameters that can handle the game behavior
  - console commands
    - 1st level - simple Python command
        `py print(game.alias_to_entity)`
        `lua print(game.alias to entity)`
    - 2nd level - Python scripts
        `!get_entities 2 3 4`
        `!set_value player01 Position x=20`
    - 3rd level - Python scripts called from Lua
        `lua local i for i=1,4,1 do cmd('set_value '..i..'Position x=20') end`
    - 4th level - Lua scripts called separately
        `lua_script test_script.lua`
    - 5th level - all above integrated into Conslole script - each row contains one of above console calls
        `script test_script.scr`
    - 6th level - call console script using lua
        `lua scr('test.scr')`
    ----- 
    - get_entities
    - set_value

### Incorporate Lua into separate Game-Console project
### Incorporate bitmap fonts into COnsole
### Incorporate default folder for the scripts (it takes time to always enter the full path)
### Incorporate list of lua commands that should happen with every script (dictionary to table)

### when killed it started to produce projectiles without controll - fix situation when player is killed

### Rewrite Factory generation
  - arrow is shoot - temporary - next IsDead (means just animation state change + change direction down + ignore it for collision)
  - 
  - when ammo pack is armed and another is picked, the newly picked should be destroyed completely - not happening now in collision ammo pack processor

  - destroy the pack of arrows if reaches 0 - otherwise there will be arrow displayed still in animation
    - mark is as temporary
  FIRST VERSION - DONE
  --------------------
  - processor `PrepareProjectileProcessor`
    - checks the animation frame and compares with the action frame
    - if the action frame is the current frame
      - generate new component `FlagCreateFromFactory` with parameters position and parent and more
  - processor `CreateEntityOnPositionProcessor`
    - process the components by similar way as currently done with current version of `GenerateProjectileProcessor`

  - Pick up AmmoPack
    - new component AmmoPack(weapon, type)   
    - new collision processor

  - TODO: Sword by default has Factory and Weapon in one entity - pickup processors must handle that = create invisible entity as sword swing
    -
  - TODO: Count on Factory level number of fired/generated entities - if Factory generated all then what ? Destroy the factory component? Destroy the whole entity?
  - TODO: Create parent component as part of Factory generation
  - TODO: PickUp ArrowPack
    - new component on weaponGenerator, containing weapon type to which  it belongs
    - move to inventory when new pack is picked
    - what if same pack is picked as already in use??? Increase and keep just one entity?
    - Sword has generator in it. How to pickup both properly?
      - pickup weapon processor - if ammo component also, keep it for later pickup by ammo pack pickup
  - TODO: How to add weapon experience into the damage effect
    - damage should be build on experience with the weapon type 
      - 1. how many generated swings/arrows
          - PrepareProjectileProcessor 
            - add on weapon component/has weapon component +1 total swings - this can influence the usability of the weapon
            - calculate experience on hasWeapon entity and add damage multiplicator to FlagGenerateEntity
      - 2. how many hits were done by weapon
          - new component Projectile having entity number as parameter + weapon type as parameter
          - ProjectileCollisionProcessor
            - counts the Score - CanScore component on player, FlagAddScore component + CalculateScoreProcessor (selects CanScore + FlagAddScore and ads score)
            - counts the hits - FlagAddWeaponExperience on player - CalculateWeaponExperienceProcessor (selects FlagAddWeaponExperience and HasWeapon and ads experience)
      - 3. damage caused as an outcome of experience and damage on the arrow
          - damage must be adjusted post generation and pre hitting
          - add new component on the new entity FlagAdjustDamagable(*1.2) and forget it
          - new porcessor that will select Damage and FlagAdjustDamagable components and adjust the Damage component accordingly


  - FURTHER STEPS: create another Generator that will generate people.
    - NEW version should be slower because it creates and destroys component.
    - but new version is not using container so some processor will not have this container condition ...
  - PROBLEMS: How to count score?

  ----------------------------------------
  LATEST THOUGHTS
   - use new event generate or parametr factory.generate = TRUE
   - Factory will have new parameters position, random, scheduled etc. that will be filled by preparateion processor
   ----
  - STEP (0) - How do I want Factory to work in general
    - processor that iterates all Factories
      - how to determine if it is the right moment for generation
        1. have a special tag for it
        2. **have attribute on Factory component - generate = True
      - how to determine on which position to generate
        1. have a new option for Position component
          - something like *relative* - that would mean to take position from the parent???
        2. **have a new component CopyParentPosition
          - every picked component has Parent(entity) component
          - entities with `CopyParentPosition` component will have this component exchanged for the real Position component by some processor

    SCENARIO FOR PROJECTILE GENERATION
    1. `GenerateProjectileProcessor` checks if frames are aligned and set the attribute on Factory *generate* = True
    2. New processor `GenerateEntityFromFactoryProcessor`
      - iterates all factories
      - calculates and updates time from the last entity generation (for scheduled Factories)
      - if `Factory.generate == True` - generate Entity with `CopyParentPosition` component and `Parent` component set to Factory entity
    3. New processor `CopyParentPositionProcessor`
      - find entities with `Parent` component and `CopyParentPosition` component
      - get Position from `Parent` entity. If `Parent` entity has no `Position` component go to his parent etc... until you find position or no parent available
      - delete `CopyParentPosition` and create new regular `Position` component
    4. How to take into the account the collision zones?
      1. parameter of `CopyParentPosition(collision_adjustment=True)` - i.e. include calc of Collision component of parent and collision component of himself
      2. OR ignore collision between parent and generated things???
      3. **new component `IgnoreCollisionWith(entity_id)`



  - STEP (1) - with existing projectiles functionality
    - processor `PrepareProjectileProcessor`
      - checks the animation frame and compares with the action frame
      - if the action frame is the current frame
        - generate new component `FlagCreateFromFactory` with parameters position and parent
    - processor `CreateEntityOnPositionProcessor`
      - process the components by similar way as currently done with current version of `GenerateProjectileProcessor`
-----
  - put projectiles somehow on the factory level where they belong - DONE
    - currently when Factory generates entity and registers it into the world, it adds Container component that references HasWeapon component
    - what if I want to use factory to generate new game characters, i.e. not to produce projectiles
      - processor that would iterate all factories that should generate some entity
        - put the entity into the world
        - link it to factory component or some entity?????
        - position will be inherited from the position component on the Factory component level? Or 
          - put component/tag GenerateEntityTag on WoodenArrowsPack entity
          - parameter of the component/tag will be Position where to generate??? and entity who has generated it.
  - get rid of container component (not needed - only to remove from hasWeapon list of entities)
    - just generate arrow on the correct position and add that component GeneratedBy(Entity ID) - for score, message whatever message ...

  - wouldnt it be better to have processor that iterates all factories ...
    - projectile generator processor only puts TAG on entity GenerateEntityTag
	- some new generic processor FactoryGenerator - that iterates GenearateEntityTag

### General - how to handle components that are having reference to other component and components that have reference to entities???
  - is there some universal approach?
  - HasWeapon is container that needs to have
    - reference to Weapon component
    - reference to Generator component

### In-game messagesm HUD, Inventory - some part of the system can listen to events and then display it. Something that we have with the message queue.

### Rename HasWeapon to CanFIght to have it aligned with CanTalk and CanWear?

### New experiments - how to integrate Lua into the python - example is Factorio
  - possible to call Lua commands from console (example below)
    /c for key,ent in pairs (game.player.surface.find_entities_filtered{name="locomotive"}) do 
        ent.train.manual_mode = false
      end

### Make better console - such as Factorio - https://wiki.factorio.com/Console
  - with python console it is not possible to write the for loop into the console as pressing Return executes the command and single line statements are hard to support in python
  /command <command>	Executes a Lua command (if allowed).
  /c <command>	Executes a Lua command (if allowed).
  /editor	Toggles the map editor.
  /measured-command <command>	Executes a Lua command (if allowed) and measures time it took.
  /silent-command <command>	Executes a Lua command (if allowed) without printing it to the console.
  /sc <command>	Executes a Lua command (if allowed) without printing it to the console.

### Rename HasInventory to CanPick to have it aligned with CanTalk and CanWear?

### New branch where map tiles are also components

### Allow comment in json using commentjson library ...

### Proceed with rewriting dialogs to class with buttons

### How to implement key actions to the dialog window - dialogs_v2
  - in the script `show_dlg_window` - there would need to be loop for every frame
   - read the keys 
   - if pressed, do something -> CONTINUE  to the next frame, to previous frame
   - if TAB is pressed next button is selected
   - if K_SUBMIT button is pressed ... run the function associated
  - DIALOG must have some elements - buttons

    "buttons" : [
      {
        "position" : [100, 100],
        "dimensions" : [50,20],
        "label" : "OK"
        "key" : [K_o, K_O]
        "on_submit" : function
      }
    ],
  - dialog is a class containing buttons as instances
    - button has btn.onSubmit function - how this function is defined?

  - **I would need to reimplement dialogs as class in order to implement buttons**
     - simple quit game dialog as a start excersise
     - dialog definition from json
     - dialog __init__ reads the json and transforms the dictionary to instance od dialog
      - dialog has array of button objects ordered list - moving using arrows and tab
      - dialog remembers button that is selected
      - button object has position, label, dimension, display function, ON_SUBMIT dunction
        - ON_SUBMIT function can do following things
          - close the dialog and nothing else (x to close the window)
          - show some other dialog (are you sure yes/no) and wait for the return of that dialog
          - create event in the event queue (can be defined in dialog definition)
          - execute command (can be defined in dialog definition) - for example if accept deny the next scene
          - execute script (can be defined in dialog definition)
        - after execution of on_submit either close the dialog or proceed to the next frame or keep the dialog
    
    "id" : "dlg_quit",
    "template" : ["dlg_yes_no"],
    "buttons" : [
      {
        "position" : [100, 100],
        "dimensions" : [50,20],
        "label" : "OK"
        "submit_key" : [K_o, K_O]
        "post_submit" : "CLOSE_DIALOG" || "NEXT_FRAME || NOTHING (keep the dialog as it is)"
        "on_submit" : [  

          ////////////////////////////////////////////
          // List of actions similar to event handling
          ////////////////////////////////////////////

          // Show yet another dialog window
          ["show_dlg_window", {"dialog_id" : "dlg_scene_start", "position" : [200,200]}]

          // Execute some other command
          ["execute_script", {"script_body" : "print(f'QUEST HAS STARTED')"}],

          // Modify brain
          ["modify_brain", {
              "entity" : "script_engine", 	 
              "commands" : [
                  [null, "disable_talk", {"entity" : "player01"}], ...
        }
      }
    ]

    **How will be the whole dialog functionality handled??**
    - show_dlg_window script? Preferable. There will be loop inside, so the whole game will be stopped during the dialogs. That is ok.

    **What about PAUSE dialog**
    - should be compatible with the old dialogs definition
      - we will pop pouse dialog from the dialogs and just display it
        - dialogs.get('pause_dlg').display()
    
    **Where to process the key pressed and actions**
    - does script has keys that are pressed in the moment? Nope, only commands have keys.
      - script_dlg_window
       - blit copy of game screen
       - dialog.update(k_up=K_NAV_UP, k_down=K_NAV_DOWN, k_submit=K_SUBMIT) ... here read the input and do action based on input if any - K_NAV_keys are defined in config. To keep dialog module reusable, pass the update keys here
       - dialog.display()
       - pygame.display.update()





### Add shadow to the window

### Create documentation to the event processing - how to define conditions on the events
  - i have troubles catching scene id for the QUEST_START event
  - rewrite conditions for event handling
    - "params" currently check only alias for entity objects - example of example below - system search for `ent` and `col_event_entity` in `alias_to_entity` dictionary
      - teleport_event = event.Event('TELEPORTATION', ent, col_event_entity, params={'teleport' : ent, 'teleportee' : col_event_entity})
    - now I have QUEST_START that does not have entity integer as a parameter - instead it hase some elementary value - string
      - self.event_queue.append(event.Event('QUEST_START', self, None, params={'scene_id' : self.id}))
    *SOLUTION*
      - event handler must first check alias_to_entity and next plain condition if key not found in alias_to_entity



### Rework event queue - ignore some events, not address event_queue directly but via function, log event creation and processing in a file
  - event queue must remain as a list in order to be processed from oldest to newest events - causality in game must be kept
  - if event queue is processed as dictionary, I would loose the information about which event was generated first and which second etc. So list is good option
  - still it is useful to have processor that processes only selected event types and ignore the other types

  - some processors are created with event_queue as a parameter - this is not probably right, better to pass some function engine.add_to_event_queue(event) that will manage everything necessary for adding (can have feature to add with priority etc.)

### Clear dialog code amd sum up the functionality in text above

### when there is dialog displayed it is not possible to show the console

### processing of event is happening before the world is drawn on the display - parametrize procesor for event processing to have specific list of events to process 
  - simply postponing the processing of PHASE START after render processors will help because there will be already some objects displayed in the screen buffer and the command for displaying dialog will force screen update - or better taking the screen copy function of engine will force the update (based on parameter)
  - by doing so - phase start and scene start events can be processed after some image is drawn on the screen and not before
  - all_events_processor = processors.GameEventsProcessor(process_game_events) ... this will take all events
  - scene_events_processor = processors.GameEventsProcessor(process_game_events, ['QUEST_START', 'PHASE_START']) ... this will take selected events only
    - game_event_handler must have event_type on input

    - must be done smartly - list of indexes cannot be parsed for deletion
      - list of indices ... can be used for processing of events on given positions
      - for deletion we need to create a copy of event queue [event for i, event in enumarate(event_queue) if i not in indices]

### Command that will Pause the whole game or that will stop all entities including the main character - brain freeze + input freeze
  - such command then added to script engine entity

### Command that displays dialog and manages key presses



### Rewrite `show_text` using dialogs as a json configuration
  - dialog is specified in a form of json
  - dialogs are part of scene json specification
  - upon start of the phase, dialogs for given phase are loaded and stored in engine dictionary - dialog_id : dialog data dict / instance of the object
  ----
  - during game dialogs are poped out as an action on some event by calling `show_dialog` script
  - parameter of `show_dialog` is `dialog_id`
  - `show_dialog` will call display_dlg(target=window, position, dlg_dictionary, keys_and_events)
  - this will display dlg and stopped the game until some key is pressed - the key for continue will be part of dialog specification.
  ----
  - upgrade - dialog to read key input and return some value that can be used to further change the flow of the game
  - example, accepting the new scene by some selection done in the dialog
  ----
  - dialog as a class? vs
  - dialog as a dictionary that has stored the surfaces
  - top-down approach
    - function display_dlg(target, position, dictionary)

    - script `show_dialog` - parameter dialog_id that is saved during loading of the scene into the new engine global table. Similarly, for `modify_brain` action `entity_id` is used.
    - 
  - dialog is configured as a part of the scene
  - create dialog function that will create dialog from the hierarchy and templates ...???
    - must know about FONT PATH and IMG PATH ...


### Loging of all events happening in the world

### All resources have description about the json structure.
  - Dialogs - DONE
  - Quests
  - Fonts
  - Frames

### Module for displaying and processing of the MENUS - main menu

### Check validity of the game states in the MAIN module

### YES / NO decision during conversation??? How this can be achieved.

### IMPROVEMENT: rework events processing - event_queue as dict not as list?
  -- does ECS support multiple instances of the same processor? YES

### Maybe engine.py divide into world.py and engine.py. In world.py there is all the load save create run. In engine.py all the queues and related functions
  - first rename the global variables properly
      global world - ok
      global _maps - TO maps - DONE
      global scenes - TO scenes - DONE
      global c_event_queue - TO event_queue - DONE
      global command_queue - ok
      global message_queue - ok
      global _entity_map - TO alias_to_entity - DONE
      global entity_to_alias - ok

  - getters setters and is functions
    - accessing engine.scenes
      - `set_phase` command is using it. How to work around that?
      - what about passing scene in commands? Yes, by passing globals to following engine variable
      - `def process_game_commands(keys=None, events=None, debug=False, gl_vars = {})` + command processor has the gl_vars as parameter
        - game.create_processor -> game.CommandProcessor(engine.process_game_commands)
        - game.run() - game.world.process(keys, events, gl_vars)
      - `game._quests` -> create processor in game CommandProcessor(... game._scene) -> game.run() - game.world.process(keys, events, gl_vars) -> CommandProcessor().process(... scenes)


    - accessing engine.maps
      - `Position` and `Teleport` components are accessing that for assertion checks
      - solution is to remove the assertion completelly
      - other solution would be to pass maps as argument to create_component function. By doing so eveny component can have access to Maps and other globals.
              `def create_component(world, entity: int, comp_class: str, comp_params: dict, global_refs: dict)` - maps, scenes
                        comp_inst = comp_name(**{**comp_params, **global_refs})
              `assert self.map in kwargs.get('gr_map', {}).keys(), f'Map {self.map} is not initialized for {self.__class__} component.`



    - function that checks scenes
    - functions that translate alias to entity and entity to alias

  - event_queue, command_queue is really private variable, it seems that it is not accessed directly from no other module. Hence it should be ok to rename it to _event_queue, _command_queue and does not need to be necessarily global ... it is used only in engine.py and shared with processor via parameter

  - message_queue is referenced directly from add_msg script and command. WOuld it be possible not to reference it directly but in the same way as command and event queue? for example brain processor will have command queue and message queue???

	- main
		- engine
		- game
		
	-	game.py
		- save
		- load
		- pause
		- init

	-	engine.py
		-	draw window
		- 	draw messages
		-	process
		-	process
		-	process
		-	window init

### Rename Event.generator_obj, to subject and object and document. Also add to events also parameters such as damage caused etc + adjust so that this parameter can be used in event to message functionality

### If MessageProcessor is not planned do not allow storing anything into the message queue OR cut the message queue regularly
  - queue enabled variable?
  - clear every couple of seconds, not always? not to wiste resources every cycle? Procesor does not run always??? No it must always run
  - function that puts into the queue engine `append_game_msg` that would control if messages are enabled
  - set enabled to False by default and the processor change it to True if run ... + adjust process_ame_messages


### How to display messages that relate to scene for example at the beginning of the scene phase??
  - Message has frame and picture - same as static window below???? wait with implementation till the below is implemented


### Scene has defined events to which it is listening to - must register this in engine module so that engine sends the events to the scene. Otherwise all scenes are processing all generated events.
  - probably some structure on engine level emembering what scene requires what event to process

### Update documentations on mapping using _entity_map and entity_to_alias

### try to implement damage as a command - processor selects the right entities and triggers events DAMAGE trigger command CMD_DAMAGE??????????

### Adjust the architecture of game messages generation - DISCUSSION
  - Rename current `GameMessageProcessor` to `RenderGameMessagesProcessor`
    - calls `core.engine.process_game_messages` to get rid of invalid messages only
	- generates the messages on the screen by looping through `engine.message_queue` and bliting on screen
  - Adjust `core.messages.messages` module
    - message is now regular class with slots. On init, remember the time of creation and assign it automatically to the event.
  - ADVANTAGES
    - It is clear that this processor renders messages - more clarity in the list of processors
    - Processor is bliting messages - same as other Render processors are bliting things on screen
  - DISADVANTAGES
    - If processor is not planned - message queue grows bigger and noting reduces it (currently done by `engine.process_game_messages`) - the current solution has the same disadvantage.
	- Other processors that are handeling the queues (Command processor and Event processor) are resolved similarly as current version of GameMessageProcessor - i.e. calling engine function and nothing more. But the other processors are not rendering anything, they are just calling other handlers - event processor for example takes all events in the queue and resends them to `scene` module for handeling. `scene` module based on handeling invokes action in the form of a `script`. Similarly, `engine.process_game_commands` execute command and notifies related `brain` about the result. So what are the options for our `process_game_messages` function? Definetelly it must clear invalid messages from the queue. Then every message in the queue send to the handler? But handler is nothing more than printing on the game window and to do it correctly it must be printed on perfectly given position - should such handler be in the `scene` module? Probably not - in such case scene configuratin file should contain part describing where on the screen to generate messages and which messages to generate and which not to generate. That is good, but where to process the printing of the screen - by calling new script `print_messages` or by calling some other script that will be able to handle the list of messages `store_messages_to_disk`  - but there can be several scenes active at the same time ... what if 2 scenes are handling the same message? Does not make sense... PROCESSING MESSAGE using QUEST HANDLER DOES NOT MAKE SENSE (due to multiple scenes can be active at the same time whereas message is one)
  - SO IT MAKE SENSE TO PROCESS MESSAGES ON THE GAME LEVEL - in MESSAGES module

### Keys
  - implement pause key window

### Transparent window on the beginning
  - define the window and text and pictures by json
  {
	  frames : [
		  {
			  background_color:
			  background_transparency:
			  ttl: 300
			  texts: [
				  {
					  text : 'sdfsdf dsffsda asdfsdf'
					  position : [100, 100]
				  },
				  {
					  text : 'sdfsdf dsffsda asdfsdf'
					  position : [200, 200]
				  }
			  ],
			  pictures : [
				  {
					  picture : imaes/sdfsdf.png
					  position: [30,30]
				  },
				  {
					  picture : imaes/sdfsdf.png
					  position: [30,30]
				  }
			  ]
		  }
  }
  - function that will prepare surface from the definition
	- script_show_text_json(example.json or dictionary)
  - call script command that will read from json and display from it


### have the possibility to change the configuration via console during game in JSON and reload it

### key mapping as config parameters
  - Controllable has parameters up/down/left/right/attack
    - controllable - control_keys dict now there are numbers in scene json
        default_keys = {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122}
    - newly I need something better
        default_keys = {'left' : 'left_arrow', 'right': 'right_arrow', 'up' : 'up_arrow', 'down' : 'down_arrow', 'attack' : 'left_ctrl'}
    - keys config K_UP, K_DOWN
    - new COmponent 'Player' - value 1,2,3,4 - id of the player
    - config will define keys for player1-4 ... in json keys[player1][up] = 'K_UP' string
    - component controllable will have key_scheme = 'player1' - it will load keys from the config

### dt as parameter for console.show?

### Update console library so that it has the paths encapsulated in str() to support libpath + if function is not defined the text on console should scroll the error

### Processors - skipping of processors based on configuration

### Prepare splash screen, main menu screen, save and load screen - game.py module implementing those menus?

### Delete on collision processor and temporary processor should delete entity using engine function to unregister it from dict before deletion

### How to display some message across the whole window - regardless cameras
  - QUest description for example, or game loading
  - some command that will display global window that can be part of global script engine
    - on start/end of scene generate event 
    - on start/end of phase generate event
  - events are generated by processors now
  - newly event queue is passed to load_quest method and further to load_phase method
  - event is added on scene and phase load, parameters of the event is scene/phase id
  - scenes have event handlers for scene start, scene end 
  - handlers call function for displaying of text for example, or music or earthquake
  - function to show something on the screen and stop the game


### Prepare test_empty_map.tmx and do scenes for testing of collisions
  - several moving entities that are hitting each other

### Prepare scenes for testing of teleportation
  - including moving teleport
  - including teleport that teleports to other map and back
  - prepare RenderableModel for teleport
  - write teleport events on console

### Skills improvement
  - smashing and shooting faster - constant that reduce the duration of animation

### Entity Resolvers might contain parameter that will decide if the collision event is deleted after processing or not

### Temporary processor and collision deletion processor share the same deletion functionality
  - maybe those processor should only mark entity as for deletion and the new processor then deletes it

### Re-think collisions

  - **Resolution** 
    - collision generator processor resets all has_collided flags to False at the beginning of the loop
    - collision generator sets Collidable.has_collided flag to True on entities where collision occured
    - collision deletion processor search and deletes entities that has_collided + DeleteOnCollision
    - maybe that temporary and delete on collision processors will just put tag ForDeletion + new processor at the end that will do the actual deletion
  
  1. `collision_map_processor`
    - FOR ALL `Position`, `Collidable`
    - IF map is hit, return to position.lastx, position.lasty

  #### Collision Generators

  2. `collision_entity_generator_processor`
    - For ALL Viewable `Position`, `Collidable`
    - If hit by one another, add to `Collidable.CollisionEvents(entity)`
    - **Possible Solution** - add `has_collided` variable to Collidable component and check it at the end of all collisions in `DeleteOnCollision` processor
  
  #### Collision Resolvers

  3. `collision_damage_processor`
    - For ALL `Damaging`, `Collidable`
    - If hit `Damageable`, decrease the health + get rid of the event with `Damageable` component
    - **Possible limitation** - if entity is damaging it cannot be teleport or pickable at the same time. I.e. I cannot damage entity and then teleport it. Is it a problem? Also I cannot damage entity and then let the entity pick it. Is it a problem?

  4. `collision_teleport_processor`
    - For ALL `Teleport`, `Collidable`
    - If hit `Teleportable`, `Position`, `Collidable`, check if key is required and do teleportation + get rid of the event with `Teleportable` entity
    - **Possible limitation** - if entity acts as Teleport it cannot be Pickable, Weapon or Wearable. Because the event is deleted.

  5. `collision_weapon_processor`	# Resolves weapon pickups collisions + generates events to the main program where those can be further processed
  6. `collision_wearable_processor`	# Resolves wearable pickups collisions + generates events to the main program where those can be further processed
  7. `collision_item_processor` # Resolves item pickups collisions + generates events to the main program where those can be further processed

  8. `collision_entity_processor` # Resolves entity collisions + generates events to the main program where those can be further processed
    - For All `Position`, `Collidable`
    - If hit other `Position`, `Collidable`, issue move command + get rid of the collision event


### Indicate error in scene definition if weapon or wearable has Position component and at the same time is in inventory of the player. If this is done it is causing error in rendering the object. The reason is that this object is in idle status when displaying at position and might be shifting the frames in this action status???


### Where to put pygame.Vector2 so that it is used in the whole game
  - config??

### Pickup collision of generator implementation - add to HasWeapon
  - picking up bunch of arrows

### Probably create also Render processor for generation on the foreground
  - in order to show some statistics , bars etc.
  - when presing some key, dislay inventory on top of the game window

### Adjust move command so we can pass parameters about speed - new command

### Rename HasWeapon to CanAttack

### Properly support default action if no other action exist in model - or have idle/down on all models????? or default/down???

### How to solve comunication between components?
  - State/Status entity for all (basically default component similar to label)???
  - Just use some component as a tag that component is in some particular status? How fast is that solution?

### Merge Renderable Action and Renderable Update processors
  - both processors are iterating over the same set

### Group processors into domains modules - Physics, Rendering, ...

### Group components into domains modules - Physics, Rendering, ...

### Implement several test scenes for testing purposes
  - test01_map_scrolling.json
  - all models, all wearables, all weapons, teleportation, collisions

### Model system for weapons in DRAW.IO sketch


### Number of max projectiles - currently on weapon - how much generated at the same time
  - we need to incorporate also units of projectiles available in ammo_pack

### Implement move_to command using A* algorithm
  - create graph from collision map on map init

### Implement some spear as a weapon spear pilot

### Implement some fireball as a weapon pilot

### 

### ParticleEffecOnCollision component
  - parameter might be effect_id
  - do some effect upon collision
  - ParticleEffectOnCOllisionProcessor

### Generate the entity not on the last frame but on different frame number???

### Tool that generates hierarchy of the models into the file automatically

### GUI and editor - inventory wearable

### Internet play - sockets - client and server part

### Think about re-implementation of collisions
  - now we iterate entity per entity through the list of entities that have collided. Is it optimal for ECS?
  - what about having new Tag? what about performance of such solution?

## Bugs

####

### Fix when rats scene dialog is finished and the NPC bounces to the player again, the initial dialog happens again and also the item is given one more time

### Fix colision correction movement - now it is moving strangelly into the side

### Fix teleportation into the collision zone - it is impossible to move in this situation

### Fix save and load, probably some processors have problem

### Fix problem - not changing position when face command is executed


## Performance fine-tuning questions

### Blitting debug information + Brain information takes away 20 FPS with bitmap font
  - after removing debug information via config the FPSs are back to +-60

####

### What is quicker for loop over components or try entity?

### What is quicker - component_for_entity vs. try_entity

### How much memory is used by the map??

###  HW sprites support, reducing the bitdepht

