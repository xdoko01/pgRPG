events
  - if any event occurs that concerns the entity as an main actor -> reset the tree
  - example: if attacked, stop chasing the enemy and start chasing someone else.
    - btree should be subscribed to events and once events received, some record should be recorder in the blackboard
    - someone hit me, my btree knows about it and has defined action on that event, to write the attacker entity to the specific blackboard key.

    "handlers": [
      "GOT_HIT": {
        bb_key: "under_attack_from",
        bb_value: some_field_from_the_event,
        action: "TREE_RESET"
      },
      "TARGET_SEEN": {
        bb_key: "target"
        bb_value:
      }
    ]

ScriptManager.execute_event_actions(EVENT, ACTIONS)

        json_logic(
            expr=translated_actions, 
            value_fnc=lambda x: x, 
            script_fnc=lambda *args: self.execute_script(args[0], event, **args[1]), 
            data=event.params
        )

							[	// CHange the behavior in case of attack
								"GOT_HIT",
								{
									"actions": [
										"IF", ["==", ["VAR", "entity"], "player01"]
										],
										["SEQ",
											["SCRIPT", "set_bb_data", {"target_ent": ???}], /// how to get info from event here
											["SCRIPT", "reset_behavior", {}]
										]
									]
								}
							]

guard - guards until it spots the enemy
 - guard a spot
  - finds a random point around
  - moves to that point
  - checks for enemy close - when spotted switch to track and attack

 - guard a path
  - 

enemy 
 - wanders around, 
 -> EVENT damage - when hit, runs away

# BT supporting events (requests)

  - special type of node - Request Handler
  - on creation of BT, create a dictionary mapping event type to RH node (one node)
  - when BT processor is executed, pass to the BT all the events
  - if BT has some of those events registered then:
    - check if the currently running behavior has higher priority than the RH node
      - if yes, continue execution of the current node as normal
    - stop processing the current behavior ans skip to the RH node and start processing it
      - the RH node will first record all event details to the blackboard
      - next it will start processing the underlying tree
    - when the RH node is finished, it returns its status to the upper node as normal
  - if RH nodes are part of the Sequence, they are ignored. THey are only invoked when event arrives

 OR:
 - on event, it is written on the blackboard
 - decorator which is resolving conditions using globals and decorating sequence is used
 - RH subtree runs meanwhile no events are processed

EVENTS - easy:
 - current node is aborted
 - tree starts from the root
 - the branches processing events are processed first

TODO:
  - events are passed to BTree - or BTRee knows abouat event manager and communicates with it
  - `CommandManager` to be able to process multiple behaviors passed by the generator
  - implement condition on globals as decorator (of any node - even sequence, ...)
  - how to decide if the currently processed node has higher priority than RH node?
    - if BT reacts on ON_DAMAGE and receives another ON_DAMAGE event - it should ignore it

  "cmd_tree": {

    "type": "Repeater",
    "name": "Trace and Attack",
    "children": [
      {
        "type": "RequestHandler",
        "name": "ON_DAMAGE run away - if health < 50",
        "event": "ON_DAMAGE",

        --> ctx.globals.event_type = "ON_DAMAGE"
        --> ctx.globals.event_source_ent = "player01"
        --> ctx.globals.event_dest_ent = "NPC"

        "children": [
          "type": "Sequence",
          "name": "If health < 50, run away",
          "children": [
            {"name": "Check globals", "type": "Behavior", "command": ["check_globals", {"conds": ["==", "NPC", ["VAR", "event_dest_ent"]]}, 
            {"name": "Check health", "type": "Behavior", "command": ["check_health", {"cond": "<50"}]},
            {"name": "Find safe spot", "type": "Behavior", "command": ["find_safe_spot", {"safe_spot_tl": "bb_safe spot"}]},
            {"name": "Move to Safe spot", "type": "Behavior", "command": ["move_to", {"pos": "^bb_safe_spot"}]},
        ]
      },

      {
        "type": "Sequence",
        "name": "Move Between the point and the target entity",
        "children": [
          {"name": "Move to target", "type": "Behavior", "command": ["move_to_target", {"target": "^target_ent", "proximity_tl": 3, "upd_path_ms": 1000}]},
          {"name": "Face the target", "type": "Behavior", "command": ["face_target", {"target": "^target_ent"}]},
          {"name": "Attack the target", "type": "Behavior", "command": ["attack", {"attack_time_ms": 2000}]},
          {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 500}]}
        ]
      }
    ]
  }


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
 - move - secondary action - running
 - check - primary action - false


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