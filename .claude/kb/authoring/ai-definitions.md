# AI Definitions — `cmd_tree` and `cmd_list`

> Last updated: 2026-07-30 | Verified by: Source-verified
> `pgrpg/core/commands/generators/btree/btree.py`,
> `pgrpg/core/commands/generators/blist/blist.py`,
> `example_game/core/components/brain_ai.py`; cross-checked against
> `example_game/resources/entities/behavior/*`, `example_game/resources/btrees/*`,
> `example_game/resources/scenes/tests/12_ai/**` @ `c7b9a5f1`

AI is declared inside a `BrainAI` component's `params`. The component chooses its generator by which
key is present:

| Key present | Generator | Good for |
|-------------|-----------|----------|
| `cmd_tree` | `BTree` — behaviour tree | Reactive, prioritised behaviour |
| `cmd_list` | `BList` — behaviour list | Linear scripts with jumps |
| neither | `BrainAI.FAILSAFE_TREE` | *nothing — this is the error path* |

Semantics of the node types are in
[../core/commands-and-ai.md](../core/commands-and-ai.md#btree--behaviour-tree-generator). This page
is the syntax.

## Shared keys

```jsonc
{"type": "brain_ai:BrainAI", "params": {
    "blackboard": { ... },      // initial global blackboard
    "handlers":   [ ... ],      // event handlers, read by the scene pipeline (not by BrainAI)
    "cmd_tree":   { ... }       // or "cmd_list": [ ... ]
}}
```

`blackboard` seeds `ctx.globals`. Keys become attributes, so a key must be a valid Python identifier.
Reference them from commands with the `^` prefix.

`handlers` is unusual: `BrainAI` ignores it, but pipeline step 14
(`entities/components/params/handlers`) registers each entry as a scene event handler. Putting the
handlers next to the brain they affect is purely for readability — they are global once registered.
See [handlers-and-actions.md](handlers-and-actions.md).

## `cmd_list` — behaviour list

A flat list of line dicts.

```jsonc
"cmd_list": [
    {"line": 0, "type": "Behavior", "command": ["move_to_pos_tile", {"pos": ["^start_tile_x", "^start_tile_y"]}]},
    {"line": 1, "type": "Behavior", "command": ["move_to_pos_tile", {"pos": ["^end_tile_x", "^end_tile_y"]}]},
    {"line": 2, "type": "Goto",     "jmp_to": 0}
]
```

| Key | Applies to | Meaning |
|-----|-----------|---------|
| `type` | all | `"Behavior"` (default if absent), `"Goto"`, `"Loop"`. Matched case-insensitively for `Goto`/`Loop`, exactly for `Behavior`. |
| `command` | `Behavior` | `[name, {params}]`, converted by `cmd_factory`. |
| `on_fail_jmp` | `Behavior` | Index to jump to on `FAILURE`. Absent → fall through to the next line. |
| `jmp_to` | `Goto`, `Loop` | Target index. |
| `repeat` | `Loop` | How many times to jump back before falling through. |
| `line` | — | **Documentation only.** The engine uses list position, not this value. A wrong `line` number misleads the reader but changes nothing. |

Indices are 0-based positions in the list. Running past either end finishes the list permanently —
`get_command()` then returns `(None, False)` for the rest of the entity's life, and the entity stops
acting. A `Goto` back to 0 is how you make it loop forever.

`Loop` uses a **single** `loop_counter` on the generator, not one per line. Sequential loops are fine.
**Do not nest loops** — a nested `Loop` never terminates, because the inner loop resets the counter the
outer one is reading. Use a `BTree` `Repeater` for nested repetition. See
[../SCOPE.md](../SCOPE.md).

Minimal infinite command — the projectile idiom:

```jsonc
"cmd_list": [{"command": ["move_auto", {}]}]      // no type, no duration → moves forever
```

## `cmd_tree` — behaviour tree

A nested node dict. `type` is mandatory; `children` is a list of child nodes; **every other key is
passed to the node constructor as a keyword argument**.

```jsonc
"cmd_tree": {
    "type": "Repeater",
    "name": "Repeat movement among the checkpoints",
    "children": [
        {
            "type": "Sequence",
            "name": "Move between checkpoints",
            "children": [
                {"type": "Behavior", "name": "Move to checkpoints",
                 "command": ["move_to_checkpoints", {"checkpoints": "^checkpoints"}]}
            ]
        }
    ]
}
```

| Key | Meaning |
|-----|---------|
| `type` | **Required.** A class name in `pgrpg/core/commands/generators/btree/btree.py`: `Behavior`, `Sequence`, `Selector`, `Inverter`, `Repeater`, `RepeatUntilFail`, `Succeeder`. |
| `name` | Required in practice — every node constructor takes `name` positionally-or-by-keyword and it appears in logs and `print_tree()`. |
| `children` | Child nodes. Composites need ≥ 1; a `Decorator` accepts **exactly one** (a second raises `InvalidNumberOfChildrenError`). |
| `command` | `Behavior` only. `[name, {params}]`. |
| `repeat` | `Repeater` only. Absent → repeat forever. |
| `template` | Load this node's subtree from a file — see below. |
| `results` | Free-form documentation of what SUCCESS/FAILURE mean. **Ignored by the engine** (absorbed by `**kwargs`), but widely used in the 12_ai scenes and worth writing. |

With `val_check=True` (which `BrainAI` always sets), `root.check()` asserts every composite has
children and every `Behavior` has a command. A failure is logged and the tree is silently replaced by
`FAILSAFE_TREE` — **an entity pacing a 4-step square means its tree failed validation.**

### Subtree templates: the `template` key (singular)

```jsonc
{"template": "guard_path($bb_entity_pos_comp_in, $path_in, ...)"}
```

`create_tree` checks `tree_def.get("template")` first; if present it loads the node from
`get_dict_params(definition=<value>, dir=FILEPATHS["BTREE_PATH"])` — i.e. a file under
`example_game/resources/btrees/`, with the same parameterised-call syntax as entity templates. The
template file's own `vars` list declares its parameters.

> ⚠️ **`template` (singular) in a btree node, `templates` (plural) in an entity definition.** They
> are different keys read by different code. Writing `templates` in a btree node silently does
> nothing; writing `template` in an entity definition also silently does nothing — and seven shipped
> files under `resources/entities/controls/` make exactly that mistake. See
> [../SCOPE.md](../SCOPE.md).

## The `^` prefix — reading the blackboard

Inside a command's params, `^name` is replaced by `ctx.globals.name` on the command's **first tick**:

```jsonc
"blackboard": {"checkpoints": [[5,5], [30,10], [50,50], [50,5]], "target_ent": 0},
...
{"command": ["move_to_checkpoints", {"checkpoints": "^checkpoints", "repeat": true}]}
{"command": ["move_to_target",      {"target": "^target_ent", "proximity_tl": 2, "upd_path_ms": 3000}]}
```

Rules:

- Substituted **once**, at `execute_command_init`, then stored in `ctx.locals`. A blackboard value
  changed afterwards does not reach a command that is already running.
- An unknown `^name` **raises `KeyError`** — deliberately loud, at the frame the command starts.
- Substitution is recursive through lists and dicts, so `{"pos": ["^start_tile_x", "^start_tile_y"]}`
  works.
- Whole values only. `"^tile_x_plus_one"` is a lookup, not an expression.

Writing the blackboard from within the AI:

| Mechanism | Use |
|-----------|-----|
| `set_bb_value` **command** | `{"command": ["set_bb_value", {"key": "target_ent", "value": 0}]}` |
| `test_bb_value` **command** | `{"command": ["test_bb_value", {"json_expr": ["!=", ["VAR", "target_ent"], 0]}]}` — returns SUCCESS/FAILURE, so it works as a tree condition |
| `set_bb_value` **script** | From an event handler: `["SCRIPT", "set_bb_value", {"entity": "%damageable", "bb_key": "target_ent", "bb_value": "%damaging", "only_if_not_set": false}]` |

Note the two `set_bb_value`s take **different parameter names** (`key`/`value` for the command,
`bb_key`/`bb_value`/`entity` for the script) — they are separate implementations in
`core/commands/` and `core/scripts/`.

## Event-driven AI

The idiom in `tests/12_ai/*_using_events.jsonc`: the tree polls a blackboard slot, and an event
handler fills it.

```jsonc
{"type": "brain_ai:BrainAI", "params": {
    "blackboard": {"target_ent": 0, "checkpoints": [[5,5], [30,10], [50,50], [50,5]]},

    "handlers": [
        ["DAMAGE", {
            "id": "ev_npc_hit",
            "description": "If NPC is hit, remember the attacker on its blackboard",
            "actions": ["IF",
                          ["==", ["var", "damageable"], "NPC"],
                          ["SCRIPT", "set_bb_value",
                           {"entity": "%damageable", "bb_key": "target_ent",
                            "bb_value": "%damaging", "only_if_not_set": false}]]
        }]
    ],

    "cmd_tree": {
        "type": "Repeater", "name": "Guard and fight",
        "children": [{
            "type": "Selector", "name": "Guard and attack",
            "children": [
                {"type": "Sequence", "name": "Chase the target, if any", "children": [
                    {"type": "Behavior", "name": "Any target?",
                     "command": ["test_bb_value", {"json_expr": ["!=", ["VAR", "target_ent"], 0]}]},
                    {"type": "RepeatUntilFail", "name": "Chase until lost", "children": [ ... ]},
                    {"type": "Behavior", "name": "Clear the target",
                     "command": ["set_bb_value", {"key": "target_ent", "value": 0}]}
                ]},
                {"type": "Behavior", "name": "Patrol until damaged", "command": ["do_parallel", { ... }]}
            ]
        }]
    }
}}
```

This requires a `GameEventsExProcessor` whose `process` list includes `DAMAGE` — otherwise the event
is dropped and the handler never runs. The `_using_events` scenes are the working references.

`do_parallel` runs several commands at once and maps their combined statuses through a `returns`
table:

```jsonc
["do_parallel", {
    "commands": [["test_bb_value", {"json_expr": ["!=", ["VAR", "target_ent"], 0]}],
                 ["move_to_checkpoints", {"checkpoints": "^checkpoints", "repeat": true}]],
    "returns": {"SS": "SUCCESS", "SR": "SUCCESS", "SF": "SUCCESS",
                "FS": "FAILURE", "FR": "RUNNING", "FF": "FAILURE"}
}]
```

Each key is one letter per sub-command (`S`/`F`/`R`), in list order.

## AI as an entity template

Package a brain in `resources/entities/behavior/` and reuse it.
`resources/entities/behavior/move_between_2_points.jsonc`:

```jsonc
{
    "id": "t_move_between_2_points",
    "vars": ["$x1", "$y1", "$x2", "$y2"],
    "components": [{
        "type": "brain_ai:BrainAI",
        "params": {
            "blackboard": {"start_tile_x": "$x1", "start_tile_y": "$y1",
                           "end_tile_x": "$x2",   "end_tile_y": "$y2"},
            "cmd_list": [
                {"line": 0, "type": "Behavior", "command": ["move_to_pos_tile", {"pos": ["^start_tile_x", "^start_tile_y"]}]},
                {"line": 1, "type": "Behavior", "command": ["move_to_pos_tile", {"pos": ["^end_tile_x", "^end_tile_y"]}]},
                {"line": 2, "type": "Goto", "jmp_to": 0}
            ]
        }
    }]
}
```

Used as:

```jsonc
"templates": ["model/body/male/wolfman/gold",
              "behavior/move_between_2_points($x1=10,$y1=10,$x2=30,$y2=10)"]
```

Note how `$` and `^` cooperate: `$x1` is substituted at **template expansion**, producing a literal
`10` in the blackboard; `^start_tile_x` then reads that blackboard slot at **command start**.

For non-scalar arguments use the list call form:

```jsonc
["behavior/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear", [],
 {"$checkpoints": [[5,5], [30,10], [50,50], [50,5]], "$enemies": ["player01"]}]
```

Shipped behaviour templates: `move_between_2_points`, `move_among_checkpoints`,
`guard_fight_back_if_ambushed_and_attack_on_sight_or_hear`.

## Restarting a brain

| From | Mechanism |
|------|-----------|
| An event handler | `["SCRIPT", "restart_brain", {...}]` → `BTree.restart_brain(bb=None)` |
| Inside the AI | the `reset_brain` command |
| An event handler | `["SCRIPT", "modify_brain", {...}]` to swap the structure |

`restart_brain` rebuilds the tree from the stored `tree_def` — which is why `create_tree` and
`BList.reset` both take care not to consume the caller's definition.

## Required processors

An AI-driven scene needs, at minimum:

```jsonc
["command_system.generate_command_from_brain_processor:GenerateCommandFromBrainProcessor", {}],
["command_system.perform_command_processor:PerformCommandProcessor", {}],
["command_system.perform_pathfinding_calculation_processor:PerformPathfindingCalculationProcessor",
 {"max_no_of_calcs": 100}]                                    // for any move_to_* command
```

plus the `Remove*` processors for every flag the commands produce (`RemoveFlagDoMoveProcessor`,
`RemoveFlagDoAttackProcessor`, …) and the sensor processors if the AI uses `test_can_see` /
`test_can_hear`. Copy the block from `tests/12_ai/`.

## Related

- [../core/commands-and-ai.md](../core/commands-and-ai.md) — node and list semantics, blackboards.
- [../reference/index.md §Commands](../reference/index.md#commands) — the 38 commands available.
- [handlers-and-actions.md](handlers-and-actions.md) — the `handlers` key and `%` substitution.
