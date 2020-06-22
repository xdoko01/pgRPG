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


## To Do

####

### Indicate error in quest definition if weapon or wearable has Position component and at the same time is in inventory of the player. If this is done it is causing error in rendering the object. The reason is that this object is in idle status when displaying at position and might be shifting the frames in this action status???

### Implement death after helth is up including animation - collision_damage_processor
  - collision processor - add IsDead, remove Motion comp, remove Brain comp, add temp component (to disappear after some time) - DONE
  - action processor - get RenderableModel and Position - DONE
    - set direction down when IsDead - DONE
  - animation is repeating - new dictionary to the model tex_repeat... - TODO

### New model version
  - do we need tex_dynamic? It is always dynamic
  - new tex_data dict
  - new dict storing only sprites (number : sprite)
  - can we easily get if action exists, and if direction action exists?
  {
    'walk' : {
      'up' : {
        'texture' : [102, 103, 104, 105, 106],
        'length' : 5,
        'dynamic' : True,
        'repetitive' : True
      }
    }
  }
  - no default, only idle
  - if idle without direction then automatically fill all directions


### Where to put pygame.Vector2 so that it is used in the whole game
  - config??



### Destroy Arrow on collision
  - currently arrow flies till map is hitted
  - newly we need it to stop on entity hit - to prevent multiple hits

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

### Rewrite model
  - Fix `tex_actions` - currently filled with random characters
  - one set of pictures - so that one picture can be used by many animations
  - substitute default by idle
  - how to implement that some entity has all idle up down left right the same picture?
  - can I do this directly in Tiled - many properties
  - or just use default as a value if no idle is found


### Number of max projectiles - currently on weapon - how much generated at the same time
  - we need to incorporate also units of projectiles available in ammo_pack

### Implement nice textboxes

### Implement move_to command using A* algorithm
  - create graph from collision map on map init

### Implelent some spear as a weapon spear pilot

### Implelent some fireball as a weapon pilot

### Destroy projectile on impact
  - DestroyOnCollision component as a tag??

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

### Fix colision correction movement - now it is moving strangelly into the side

### Fix teleportation into the collision zone - it is impossible to move in this situation

### Fix save and load, probably some processors have problem

### Fix problem - not changing position when face command is executed

### rename _entity_map to entity_map or mapping, it is global so it should not start by _

### *Show* text command to have time parameter but also to disapear when space is pressed (or action key)


## Performance fine-tuning questions

####

### What is quicker for loop over components or try entity?

### What is quicker - component_for_entity vs. try_entity

### How much memory is used by the map??

###  HW sprites support, reducing the bitdepht