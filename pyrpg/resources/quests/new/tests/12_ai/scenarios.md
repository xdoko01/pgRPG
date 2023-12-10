# Composable comands
 - mapping outputs to inputs - similar to UE videos
 
 - TaskGetRandomLocation
  - (v)Target
    (v)Radius
    (v)Blackboard Key

  - (f)GetActorLocation
    - (in)Target <--(v)Target
    - (out)Return Value --> (in)Origin

  - (f)GetRandomPointInNavigableRadius
    - (in)Origin, <-- (out)Return Value
      (in)Radius <-- (v)Radius
    - (out)Random Location

  - (f)SetBlackboardValueAsVector
    - (in)Key, <-- (v)Blackboard Key
    - (in)Value <-- (out)Random Location

"commands": [
  {
    "name": "TaskGetRandomLocation",
    "params": ["target", "radius", "blackboard key"],
    "functions": [
      {
        "name": "GetActorLocation",
        "params": {
          "target": "$target",
        },
        "returns": ["return_value"]
      },
      {
        "name": "GetRandomPointInNavigableRadius",
        "params": {
          "origin": "GetActorLocation.return_value",
          "radius": "$radius"
        },
        "returns": ["random_location", "return_value"]
      },
      {
        "name": "SetBlackboardValue",
        "params": {
          "key": "$blackboard_key",
          "value": "GetRandomPointInNavigableRadius.random_location"
        },
        "returns": []
      }
    ],
    "returns": ["GetRandomPointInNavigableRadius.return_value"]
  }
]

# Ideal bahavior tree structure
 1. Recognizes scope of values stored on the blackboard
  - every node can have its blackboard (except Behavior node)
 2. Decorator that evaluates the condition from the blackboard
 3. Simple paralell - 2 commands are executed simultaneously in one cycle - BTree returns more than one command to execute.


## walk and check for enemies at the same moment in one cycle

 - simple paralel node
 - move - secondary action
 - check - primary action -
 

## How to implement the scope chain - it is implemented as a stack LIFO of objects - dictionaries

 - blackboard will look as follows
    [
      {"start_tile_pos": [100,100],"end_tile_pos": [200,200]}, ... /Repeat Indefinetelly/Move Between Points/Move to end point
      {"start_tile_pos": [10,10], "end_tile_pos": [20,20]}, ... /Repeat Indefinetelly/Move Between Points
      {"start_tile_pos": [5,5], "end_tile_pos": [7,7]}, ... /Repeat Indefinetelly
      {} ... globals
    ]
- must implement pushing new values in the blackboard and poping adequatelly
- must implement read and write to the blackboard - some explicit keyword if we want to write to global always awailable
- the translation dictionary for the processing of command must shring into one dictionary

## Source Blackboard where there is everything recorded
blackboard: {
  "/": {},
  "/Repeat Indefinetelly": {
    "start_tile_pos": [5,5],
    "end_tile_pos": [7,7]
  },
  "/Repeat Indefinetelly/Move Between Points": {
    "start_tile_pos": [10,10],
    "end_tile_pos": [20,20]
  }
  "/Repeat Indefinetelly/Move Between Points/Move to end point": {
    "start_tile_pos": [100,100],
    "end_tile_pos": [200,200]
  }
}

## Path to the command must be known at any point
  /Repeat Indefinetelly/Move Between Points/Move to end point

## Before passing the blackboard to the command as a context, process it based on Source Blackboard and path to the command
command path: /Repeat Indefinetelly/Move Between Points/Move to end point
 - take {}
 - override with '/' keys
 - override with '/Repeat Indefinetelly/' keys
 - override with '/Repeat Indefinetelly/Move Between Points/' keys
 - override with '/Repeat Indefinetelly/Move Between Points/Move to end point/' keys

## command will get the processed blackboard - must be available before substituing the comand parameters with the blackboard values
blackboard to be used for correct searching of keys - *for move to end point command*
blackboard:{
    "start_tile_pos": [100,100],
    "end_tile_pos": [200,200]
}

## command will get the processed blackboard
blackboard to be used for correct searching of keys - *for move to start point command*
blackboard:{
    "start_tile_pos": [10,10],
    "end_tile_pos": [20,20]
}


  "cmd_tree": {
    "type": "Repeater",
    "name": "Repeat Indefinetelly",

    "blackboard": {
      "start_tile_pos": [5,5],
      "end_tile_pos": [7,7]
    },

    "children": [
      {
        "type": "Sequence",
        "name": "Move Between Points",
        
        "blackboard": {
          "start_tile_pos": [10,10],
          "end_tile_pos": [20,20]
        },

        "children": [
          {"name": "Move to end point", "type": "Behavior", "blackboard": {"start_tile_pos": [100,100], "end_tile_pos": [200,200]}, "command": ["move_to_pos_tile", {"pos": "^end_tile_pos"}]},
          {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]},
          {"name": "Move to start point", "type": "Behavior", "command": ["move_to_pos_tile", {"pos": "^start_tile_pos"}]},
        ]
      }
    ]
  }


1. move between pre-defined 2 points


  "cmd_tree": {
    "type": "Repeater",
    "name": "Repeat Indefinetelly",

    "children": [
      {
        "type": "Sequence",
        "name": "Move Between Points",
        
        "blackboard": {
          "start_tile_pos": [10,10],
          "end_tile_pos": [20,20]
        },

        "children": [
          {"name": "Move to end point", "type": "Behavior",  "command": ["move_to_pos_tile", {"pos": "^end_tile_pos"}]},
          {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]},
          {"name": "Move to start point", "type": "Behavior", "command": ["move_to_pos_tile", {"pos": "^start_tile_pos"}]},
        ]
      }
    ]
  }


2. move between pre-defined N points
   
   Globals
   - path : {path: [], _idx: null}
   - next_stop: null

    Repeat
    - cmd set_next_point(^path, store_to=next_stop)
    - cmd move_to_pos_px(pos=^next_stop)

  "cmd_tree": {
    "type": "Repeater",
    "name": "Repeat Indefinetelly",

    "children": [
      {
        "type": "Sequence",
        "name": "Move Between N Points",
        
        "blackboard": {
          "start_tile_pos": [10,10],
          "end_tile_pos": [20,20]
        },

        "children": [
          {"name": "Move to end point", "type": "Behavior",  "command": ["move_to_pos_tile", {"pos": "^end_tile_pos"}]},
          {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]},
          {"name": "Move to start point", "type": "Behavior", "command": ["move_to_pos_tile", {"pos": "^start_tile_pos"}]},
        ]
      }
    ]
  }


X/ move between 2 points but every specified amount of time do some other action

  - after some time return fail
  - btree will react on this fail with some other action
  - then again will resume the movement

3/ move between n points - defined repeats

   Globals
   - path : {path: [], _idx: null, _repeat: 0}
   - next_stop: null

    Repeat
    - cmd set_next_point(^path, store_to=next_stop)
    - cmd move_to_pos_px(pos=^next_stop)

4/ find path betwween 2 points and move from start to end

    Globals
    - target

    - cmd set_path(target=^target, store_to=path) # stores

    Repeat
    - cmd set_next_point(^path, store_to=next_stop)
    - cmd move_to_pos_px(pos=^next_stop, notify_after_x_ms=100, notify into bb = control_stop)

5/ move between points but stop when damaged.

 - decorator with condition on the blackboard that damage was taken ...
 - decorate the behavior node with condition on the blackboard decorator
 - game event will be automatically propagated to the blackboard of the behavior tree - so that all events are visible
 - the decorator node and the action node should happen in one step - one cycle

# cmd scope
locals: {}

globals: {
  "\": {},
  "\sequence": {},
  "\sequence\sequence": {}
}