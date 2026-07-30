# Commands and AI

> Last updated: 2026-07-30 | Verified by: Source-verified
> `pgrpg/core/managers/command_manager.py`, `pgrpg/core/commands/__init__.py`,
> `pgrpg/core/commands/generators/btree/btree.py`,
> `pgrpg/core/commands/generators/blist/blist.py`,
> `example_game/core/components/brain_ai.py`,
> `example_game/core/commands/move_dir.py`,
> `example_game/core/processors/command_system/*.py` @ `c7b9a5f1`

A **command** is a named, parameterised action applied to one entity, which may take many frames to
complete. Commands are the unit of both player input and AI. A **command generator** is a data
structure that decides which command comes next.

## The pipeline

```
GenerateCommandFrom{Input,Brain,BTree,BList,File,Mouse}Processor
    └─ generator.get_command()          → (Command | None, is_first_call)
    └─ command_manager.add_command(cmd, orig_entity_id, generator)

PerformCommandProcessor
    └─ command_manager.process_commands(ecs_mng, keys, events)
         while queue:
           (cmd, entity_id, generator) = queue.pop(0)
           if generator:
               generator.notify_command_start()                  # blackboard stats
               result = execute_command_with_ctx(...)            # may run *_init first
               generator.process_command_result(result)          # advance the generator
           else:
               execute_command(...)                              # ad-hoc, no context
```

Both ends are ordinary processors placed in the scene's `processors` list, so the frame position of
generation and execution is a scene-authoring decision.

## `Command` and `CommandStatus`

`pgrpg/core/commands/__init__.py`:

```python
Command = namedtuple('Command', ['name', 'params', 'entity_id'])
```

`cmd_factory(cmd)` turns the JSON form `["name", {params}]` into a `Command`. It asserts that
`cmd[0]` is a `str` and `cmd[1]` is a `dict`, then **pops** `params["entity"]` into
`Command.entity_id` and asserts it is an `int` — i.e. the alias must already have been translated at
component-construction time. A raw alias string here is a hard failure with the message
`Entity alias "..." is not translated to int!`.

`add_command` resolves the target: `cmd.entity_id` if set, otherwise the generator owner's entity.
It asserts the result is an `int`, and **silently ignores `cmd is None`** — which is how a finished
generator reports "nothing more to do".

```python
class CommandStatus(Enum):
    NONE = 'NONE'; RUNNING = 'RUNNING'; SUCCESS = 'SUCCESS'; FAILURE = 'FAILURE'
```

`RUNNING` means "call me again next frame". `SUCCESS` / `FAILURE` complete the command and advance
the generator.

## The command module contract

Commands live under `MODULEPATHS["COMMAND_MODULE_PATH"]` (`core.commands` in the example game), one
module per command, module name = command name. `example_game/core/commands/move_dir.py` is the
canonical template. Three functions:

```python
def initialize(register, module_name):
    register(fnc=process, alias=module_name)              # mandatory
    register(fnc=init,    alias=module_name + '_init')    # mandatory

def init(ecs_mng, entity_id, ctx, <your params>, **cmd_kwargs) -> None: ...
def process(ecs_mng, entity_id, ctx, <your params>, **cmd_kwargs) -> CommandStatus: ...
```

| Parameter | Meaning |
|-----------|---------|
| `ecs_mng` | The `ecs_manager` **module** (from `REF_ECS_MNG`). Full world access. |
| `entity_id` | Target entity. |
| `ctx` | The `CommandContext` (blackboard + timing), or `None` for ad-hoc commands. |

`**cmd_kwargs` is mandatory in practice: `execute_command` passes `**cmd_ctx.locals.__dict__`, which
accumulates every parameter the command was ever given, so a strict signature will raise `TypeError`.

`get_command(cmd_name, init=False)` lazy-registers on first lookup, exactly like scripts.

Commands typically do their work by **adding a flag component**, leaving the actual effect to a
later processor. `move_dir` is the whole pattern in three lines:

```python
new_component = FlagDoMove(moves=moves, dt_on=dt_comp, absolute=absolute)
ecs_mng.add_component(entity_id, new_component)
return CommandStatus.SUCCESS
```

`PerformMovementProcessor` then consumes `FlagDoMove`, and `RemoveFlagDoMoveProcessor` strips it at
the end of the frame. That flag-component idiom is used throughout — see
[../reference/index.md §Components](../reference/index.md#components).

Command modules carry doctests exercised through `ECSManagerMock` / `CommandContextMock`; run them
with `python -m core.commands.move_dir -v` from `example_game/`.

## `CommandContext` — the blackboard

`CommandContext` is a `Protocol` with six fields:

| Field | Meaning |
|-------|---------|
| `globals` | `Container` — the generator's shared blackboard, seeded from the AI definition's `blackboard` key. Persists for the generator's life. |
| `locals` | `Container` — **reset for every new command**. Holds that command's resolved parameters plus anything `init` stashes. |
| `init_time` | `pygame.time.get_ticks()` when the current command started. |
| `duration` | ms since `init_time`. |
| `tick_count` | How many times the current command has been ticked; `1` on the first tick. |
| `current_time` | `pygame.time.get_ticks()` as of this tick. |

`Container` (`pgrpg/core/commands/__init__.py:46`) is an attribute bag: `add(name, val)` →
`setattr`, `get(name)` → `getattr`. So the blackboard is read in Python as `ctx.globals.target_ent`
and in JSON as `"^target_ent"`.

Both generators implement the same two blackboard methods:

- `bb.reset()` — new `locals`, `init_time = now`, `duration = 0`, `tick_count = 1`.
- `bb.update()` — refresh `current_time`, recompute `duration`, `tick_count += 1`.

`notify_command_start()` calls `reset()` on the first tick of a newly selected command and
`update()` on every subsequent tick.

### The `^` prefix: pulling values from the global blackboard

`execute_command_init` (`command_manager.py:154`) is where `^` is resolved:

```python
cmd_params_with_bb_values = translate(trans_dict=cmd_ctx.globals.__dict__,
                                      value=cmd_params, prefix='^')
for k, v in cmd_params_with_bb_values.items():
    cmd_ctx.locals.add(k, v)
cmd_init_fnc(ecs_mng, entity_id, cmd_ctx, **cmd_ctx.locals.__dict__)
```

So `{"target": "^target_ent"}` becomes `{"target": <value of globals.target_ent>}`. With
`prefix='^'` set, `translate` **raises `KeyError`** if the name is not on the blackboard — a
deliberate loud failure, unlike unprefixed translation which passes unknown values through
unchanged.

Substitution happens **once, on the first tick**, and the result is stored in `locals`. A blackboard
value changed later does not reach a command that is already running. Commands that must track a
changing target re-read it from the world themselves.

`execute_command_with_ctx` runs the init phase when `cmd_ctx.tick_count == 1`, then always runs
`process` with `**cmd_ctx.locals.__dict__`.

## `CommandGenerator` protocol

```python
class CommandGenerator(Protocol):
    bb: CommandContext
    def reset(self, new_ai_struct: dict) -> Command: ...
    def get_command(self) -> Command: ...
    def process_command_result(self, result: CommandStatus) -> None: ...
    def notify_command_start(self) -> None: ...
```

`get_command()` in both shipped implementations actually returns `(command, is_first_call)`.

Two implementations ship: `BTree` and `BList`. The `BrainAI` component picks between them **by which
key is present** (`example_game/core/components/brain_ai.py:109`):

| Key in `params` | Generator |
|-----------------|-----------|
| `cmd_tree` | `BTree` (with `val_check=True`, `template_path=FILEPATHS["BTREE_PATH"]`) |
| `cmd_list` | `BList` |
| neither | falls back to `FAILSAFE_TREE` |

`BrainAI.FAILSAFE_TREE` is a `Repeater`→`Sequence` of four absolute `move_dir` commands — an entity
that walks in a square. **If an NPC starts pacing a square for no reason, its AI definition failed
validation**; check the log for `The Behavior Tree is invalid. Substituing with default behavior.`

## BTree — behaviour tree generator

`pgrpg/core/commands/generators/btree/btree.py`. Node classes, all resolved from the JSON `type`
field via `str_to_class` against this module:

| Class | Kind | Semantics |
|-------|------|-----------|
| `Behavior` | leaf | Holds a `command`. Returns `(self, command)` from `process()`. The only node that does work. |
| `Sequence` | composite | Runs children in order. Advances on child SUCCESS; completes with FAILURE on the first child failure, SUCCESS after the last child succeeds. **AND gate.** |
| `Selector` | composite | Runs children in order. Advances on child FAILURE; completes with SUCCESS on the first child success, FAILURE after the last child fails. **OR gate.** |
| `Inverter` | decorator | Child FAILURE → SUCCESS; child SUCCESS → FAILURE. |
| `Repeater` | decorator | On child completion: if `repeat` is unset or not yet reached, reset the subtree and start again; else return SUCCESS. `repeat` is a node param. |
| `RepeatUntilFail` | decorator | Child SUCCESS → reset and rerun; child FAILURE → SUCCESS to the parent. |
| `Succeeder` | decorator | Declared but **`pass`** — it inherits `Decorator` and implements no `process()`, so it does not work. See [../SCOPE.md](../SCOPE.md). |

`TreeNode` statuses are `NONE / RUNNING / SUCCESS / FAILURE` (`BTreeCommandStatus`, a mirror of
`CommandStatus`). Node lifecycle:

- `process()` calls `on_init()` the first time the node is ticked (status `NONE`), which sets
  `RUNNING`.
- A composite tracks `child_running_idx`; ticking it descends to that child, recursively, until a
  `Behavior` leaf is reached and its command returned.
- On completion a node calls `on_completion(result)` → `on_success()` / `on_failure()`, then
  `self._parent.notify_from_child(result)`. Parents decide whether to advance or complete.
- `reset()` sets a node and its whole subtree back to `NONE`.

### The tick loop, end to end

```
BTree.get_command()
  root completed?                 → (None, False)          # tree finished; nothing more
  have a cached _action_node?     → action_node.process()   → (cmd, False)
  otherwise                       → root.process()          → (cmd, True), cache the action node

BTree.process_command_result(result)
  _action_node.set_result(result)   # Behavior.set_result: if not RUNNING → on_completion(...)
  if result completed: _action_node = None                  # re-descend next tick
```

Caching `_action_node` is what makes a multi-frame command cheap: while it returns `RUNNING`, the
tree is not re-walked from the root.

`restart_brain(bb=None)` rebuilds the tree from the stored `tree_def` and optionally replaces the
blackboard — reachable from the game via the `restart_brain` script and the `reset_brain` command.

### Tree construction from JSON

`create_tree(tree_def, parent, depth, cmd_factory, template_path)`:

- If the node dict has a `template` key, the node is loaded from a file:
  `get_dict_params(definition=<template>, dir=template_path)` — so a subtree can be a
  parameterised template call. `template_path` is `FILEPATHS["BTREE_PATH"]`
  (`example_game/resources/btrees/`).
- Otherwise `type` is mandatory; `children` is optional; **everything else in the dict is passed to
  the node constructor as a keyword argument**. That is how `repeat` reaches `Repeater` and `name`
  reaches every node — and why an unrecognised key is silently accepted by nodes with `**kwargs`.
- A `command` value is passed through `cmd_factory` (i.e. `cmd_factory` → a `Command` namedtuple).
- The definition dict is read **without being consumed** — deliberately, because `restart_brain()`
  rebuilds from the stored `tree_def` and one template file may be shared by several entities.

`val_check=True` runs `root.check()`, which asserts every composite has children and every leaf has
a command, raising `InvalidBehaviorTreeNodeError` / `InvalidBehaviorTreeError` — caught by `BrainAI`
and converted into the failsafe tree.

`BTree.print_tree()` renders the tree with ANSI colour per status (white NONE, yellow RUNNING, green
SUCCESS, red FAILURE) — useful from the dev console.

## BList — behaviour list generator

`pgrpg/core/commands/generators/blist/blist.py`. A flat list of numbered lines, each a dict:

| Line `type` | Fields | Semantics |
|-------------|--------|-----------|
| `Behavior` (default) | `command`, optional `on_fail_jmp` | Execute the command. |
| `Goto` | `jmp_to` | Unconditional jump to that index. |
| `Loop` | `repeat`, `jmp_to` | Jump back `repeat` times, then fall through to the next line. |

`_find_next_action_node()` keeps resolving `Goto` / `Loop` lines until it lands on a `Behavior`,
recursively — so chained jumps work. Indices are 0-based; running off either end sets `_is_finished`
and `get_command()` returns `(None, False)` forever after.

`process_command_result(result)`:

| Result | Effect |
|--------|--------|
| `SUCCESS` | move to `current_cmd_idx + 1` |
| `FAILURE` | jump to `on_fail_jmp` if the line defines one, otherwise `current_cmd_idx + 1` |
| `RUNNING` | stay; clear `_new_action_node_found` |

`reset(new_ai_struct)` **copies each command line** (`[command.copy() for command in
new_ai_struct['cmd_list']]`) before running the `cmd_factory` over the `command` entries — otherwise
the caller's definition would be consumed and could not be reused on restart or shared between
entities.

`loop_counter` is a **single** counter on the generator, not per line, so nested `Loop` lines in one
list interfere. Use one loop per list, or a `BTree`, if you need nesting.

`BList.print()` highlights the running line in yellow.

## Generating commands from input

`GenerateCommandFromInputProcessor` reads the `Controllable` component: a `key_profile` naming a
`KEYS.K_PROFILE` entry, an optional per-action `key_feedback` (`HOLD` / `UP` / `DOWN`), and
`control_cmds` mapping each action to a list of `[name, params]` commands. From
`example_game/resources/entities/controls/default.json`:

```json
"control_cmds": {
    "LEFT":      [["move_dir_add", {"moves": ["left"]}]],
    "ATTACK":    [["attack", {}]],
    "INVENTORY": [["toggle_inventory", {}]]
}
```

Input-generated commands are enqueued **without a generator**, so they take the
`execute_command(...)` branch: no `CommandContext`, no `init` phase, one shot per frame.

Other generators in `command_system/`: `generate_command_from_mouse_processor`,
`generate_command_from_file_processor` and `record_command_to_file_processor` (a record/replay pair
— see the `tests/02_commands/record_commands.jsonc` and `play_commands_*.jsonc` scenes), plus
`generate_command_from_btree_processor` and `generate_command_from_blist_processor` (the older
per-type variants superseded by `generate_command_from_brain_processor`).

## Related

- [../authoring/ai-definitions.md](../authoring/ai-definitions.md) — the JSON syntax for
  `cmd_tree` / `cmd_list` and the `^` prefix.
- [../reference/index.md §Commands](../reference/index.md#commands) — the 38 shipped commands.
- [managers.md](managers.md) — `command_manager`'s place in the wiring.
- [../ecs/processors.md](../ecs/processors.md) — the flag-component idiom.
