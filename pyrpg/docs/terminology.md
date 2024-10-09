# Entity
 - Short form - `ent`
 - Long form - `entity`
## Entity ID
Unique integer assigned to every entity in the game
 - Short form - `ent_id`
 - Long form - `entity_id`
## Entity Alias
Unique string representing the entity. One entity alias belongs to max one entity id and one entity id can have none or one alias.
 - Short form - `ent_alias`
 - Long form - `entity_alias`

# Component
 - Short form - `comp`
 - Long form - `component`
## Component Type
### Component Type Parameters

# Processor
 - Short form - `proc`
 - Long form - `processor`

  - Processor alias, processor class def
    - `"event_system.game_events_processor:GameEventsExProcessor"`
  - Processor definition
    - `["event_system.game_events_processor:GameEventsExProcessor", {"process" : ["QUEST_START", "DESTROYED", "CUST_UI_CONFIRM"]}]`


 # Translation from File definition to Python basic obj definition to instances of classes
  - The json/yaml definition object of entity/component/processor that is translated to dictionary/list/tuple/str is called definition and is named with suffix `_def`.
  -> JSON/YAML/other -> translates to `_def` (`scene_def`, `comp_def`, `proc_def`, etc) it is string/list/dictionary -> this further translates to instances of classes representing the game objects in the game world, i.e. `scene`, `component` or `comp`, `processor` or `proc`

# ID versus ALIAS
 - id is a number or UUID assigned to some game object without any semantic meaning
 - alias is human readable word representing the game object in definitions

# delete / clear / remove ???

# load / create
 - load 
 - create when returning some real object instance as result

# Other Unsorted
 - use "" rather than ''
 - use CAPITALS for global environments
 - use space after the comment # comment """ Comment."""
 