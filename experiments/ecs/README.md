# ECS experiments on RPG example

####

## Requirements

####

### esper - https://github.com/benmoran56/esper
  - Changes done in ESPER
    - New esper function for exclusion of some components on entity - get_entities_ex
    - Changed try_entity so that it returns (originally it yealded)

### pytmx - https://github.com/bitcraft/PyTMX

## Some solutions

####

>**Q:** How to implement translation from entity_id to game_id in quest event processing?
>**A:** Keeping dictionary of entity names and entity ids on Engine module level.

>**Q:** How to fix moving into collision zone even if both entities have collision set?
>**A:** All movement (even corrective movements after collision) must be implemented as move command and pushed into command queue. Otherwise, by correction using lastx, lasty etc. entity will get stuck eventually.

## Features

####

### Architecture Design implemented

  - *Maps and Quests* are out of esper.world.
  - *Maps and Quests* are accessed from Processors that have esper.world as an input parameter i.e. they know how to call outside of the esper.world.
  - *Event handling* is achieved by calling to engine functions from esper.world processors.
  - *Command handling* is achieved by calling to engine functions from esper.world processors.

### Multiple game screens implemented

  - Entity can have *Camera* component assigned.
  - *Camera* component is represented by separate game screen on the main game window where entity is in the centre of this screen.
  - *Render* processors and *Camera* processors facilitates correct updating of all camera screens.
  - New screen can be dynamically added/removed by adding/removing *Camera* component to any entity that I want. Command that adds/removes *Camera* component to any entity must be called for that.

### Scrolling implemented

  - *CameraProcessor* updates camera offset based on position (*Position* component) of the entity that has *Camera* component.
  - *RenderProcessor* iterates all entities with *Camera* component and draws the screen into *Camera* componet variable sceen that is blitted on the window.

### Teleports implemented

  - Record collision entities on *Collision* components (list of entities with whom the entity has collided).
  - *CollisionEntityGenerator* processor records collision entities on *Collision* component.
  - *CollisionTeleport* processor iterates all teleports and resolves collisions that are recorder on the *Collision* component.
  - *CollisionCorrector* processor resolves all the outstanding collisions that were not handled by *Teleport* and/or *Item* processor.

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

### Picking items implemented

  - very similar to *Teleport* implementation

### Global brain implemented (Global Script processor)

  - It is implemented as a simple entity with just *Brain* component.
  - Every command must have parameter *entity* specified because if it is not specified then the command is trying to be executed on the source entity (which does not make sence for the global script processor).

### Simple quest implemented

  - **Scenario overview**
    - Player hits NPC.
    - Player and NPC have linear conversation.
    - At the end of the conversation NPC gives item to the player (key).
    - NPC waits until task is done.
    - Using the key, player can enter to the other map - teleport with the key.

### Save and Load game implemented

  - Implementation using pickle library.

  1. All engine global objects are put into the dictionary called game_state (command queue, event queue, maps, quests and esper.world)
  2. pygame.Surface objects are not serializable, so before saving it was necessary to set every such reference to None (on both components and processors).
  3. After saving those references must be refreshed in order to keep the game going - it is done using pre_save and post_load methods and the logic happens in save_game and load_game functions.
  
  - During the game, pressing *F1* saves the game and pressing *F2* loads the game.

### Animated Characters implemented

  - New component *RenderableModel* - substitution of static component - *Renderable*
  - New *Model* class that reads json tileset from *Tiled* 3rd party SW
  - New processor *RenderableModelWorldProcessor* - substitution of *RenderableWorldProcessor*
  - new *StatusProcessor* processor
    - used to correctly set the status for rendered animation character
    - uses motion.has_moved flag and hasWeapon.has_attached flag for setting up idle/walk/attack status

### Processing only entities that are visible on the screen implemented

  - New filter function filter_only_visible implemented.
  - Function is filtering based on *Position* component x, y vars and camera screen rectancle. Entities that have position out of this camera rectancle are not being drawn.

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

### Death implemented

  - Adjustment of *CollisionDamageProcessor* - after health is below 0, following happens:
    - New component *IsDead* is assigned to the entity 
    - Components *Brain*, *Motion*, *Camera*, *Collidable* are removed 
    - Component *Temporary* is added in order to remove the dead body after some time.

### Deletion of entities upon collision implemented

  - New component *DeleteOnCollision* that is only a tag that indicates that entity should be deleted after processing of collisions
  - Adjustment of *Collidable* component that newly contains new flag has_collided (indicates if entity has collided with something in current processor loop)
  - Adjustment of *CollisionEntityGeneratorProcessor* processor
    - processor newly resets has_collided flag on all entities with Collidable component (at the beginning of collision processing)
    - processor newly sets has_collided flag to `True` on all entities for which some collision event was created 
  - New processor *CollisionDeletionProcessor* deletes entities that have component `DeleteOnCollision` and `has_collided` set to `True`

### Support for bitmap fonts and frames implemented

  - New package `utils` containing 2 modules - `bitmap_font` and `bitmap_frame`
  - New module  `core.config.fonts`/ `core.config.frames` initiating fonts/frames to be used within the whole game (e.g. debug font, player talk font)
  - New processor `RenderTalkProcessor` only blits preprepared surfaces from `CanTalk` component on the screen
  - Component `CanTalk` newly does not contain any font reference, just surface on which text can be blitted by command
  - Command `show_dialog` is only importing preprepared fonts from `core.config.fonts`/frames from `core.config.frames` and blits the text to `CanTalk` surface

### Support for transparent dialog bubble frames

  - `CanTalk` component adjusted by new parameters - `frame_surf`, `frame_dim` and `frame_text_offset` in order for `RenderTalkProcessor` to blit frame and text individually on the game screen (to achieve transparent frame but not transparent text).
  - `show_dialog` command adjusted to prepare both surfaces - for frame and for the text and save them both into `CanTalk` component

### Support for dynamic text dialogs

  - `CanTalk` component has new attribute `text_speed` that is managing the speed of displaying text for the particular entity (NPC/player).
  - `show_dialog` module has now 2 functions `show_dialog_static` and `show_dialog_dynamic`. Static fcion is the original function whereas the dynamic is the new one.
  - Based on elapsed time from the first command call, the command is showing portion of the text. `frame_surf` is static and generated only on the first call of the command wherease the `test_surf` is generated every time the command is called internally. Hence, it is slower than `show_dialog_static` function.
  - The command remains the same, i.e. `show_command`. The decision if dynamic or static function is to be used must be done in commands package mapping.

## To Do

####

### Update console library so that it has the paths encapsulated in str() to support libpath

### Processors - skipping of processors based on configuration

### Prepare splash screen, main menu screen, save and load screen - game.py module implementing those menus?

### Delete on collision processor and temporary processor should delete entity using engine function to unregister it from dict before deletion

### How to display some message across the whole window - regardless cameras
  - QUest description for example, or game loading
  - some command that will display global window that can be part of global script engine
    - on start/end of quest generate event 
    - on start/end of phase generate event
  - events are generated by processors now
  - newly event queue is passed to load_quest method and further to load_phase method
  - event is added on quest and phase load, parameters of the event is quest/phase id
  - quests have event handlers for quest start, quest end 
  - handlers call function for displaying of text for example, or music or earthquake
  - function to show something on the screen and stop the game


### Prepare test_empty_map.tmx and do quests for testing of collisions
  - several moving entities that are hitting each other

### Prepare quests for testing of teleportation
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


### Indicate error in quest definition if weapon or wearable has Position component and at the same time is in inventory of the player. If this is done it is causing error in rendering the object. The reason is that this object is in idle status when displaying at position and might be shifting the frames in this action status???


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

### Implement several test quests for testing purposes
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

### Fix when rats quest dialog is finished and the NPC bounces to the player again, the initial dialog happens again and also the item is given one more time

### Fix colision correction movement - now it is moving strangelly into the side

### Fix teleportation into the collision zone - it is impossible to move in this situation

### Fix save and load, probably some processors have problem

### Fix problem - not changing position when face command is executed

### rename _entity_map to entity_map or mapping, it is global so it should not start by _

### *Show* text command to have time parameter but also to disapear when space is pressed (or action key)


## Performance fine-tuning questions

### Blitting debug information + Brain information takes away 20 FPS with bitmap font
  - after removing debug information via config the FPSs are back to +-60

####

### What is quicker for loop over components or try entity?

### What is quicker - component_for_entity vs. try_entity

### How much memory is used by the map??

###  HW sprites support, reducing the bitdepht