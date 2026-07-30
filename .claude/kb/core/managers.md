# Managers and the `game_functions` Wiring

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/engine.py`,
> `pgrpg/core/managers/*.py` @ `c7b9a5f1`

## Managers are modules

Every manager in `pgrpg/core/managers/` is a **module with module-level globals**, not a class.
There is nothing to instantiate:

```python
from pgrpg.core.managers import ecs_manager
ecs_manager.create_entity(entity_def)          # correct
ecs_manager = ECSManager()                     # wrong — no such class
```

Each manager keeps its state in private module globals (`_world`, `_event_queue`, `_maps`, …) and
exposes functions. Older class-based versions survive as commented-out code inside several manager
files; ignore them.

Consequences worth remembering:

- **One game per process.** Module globals are process-wide.
- **Import order matters.** `pgrpg/core/engine.py` calls `script_manager.init(...)` and
  `event_manager.init(...)` at *module import time*, before `engine.init()` runs.
- **Tests must reset state explicitly** — there is no fixture that gives you a fresh manager.

## The eight managers

| Manager | Owns | Key functions |
|---------|------|---------------|
| **ecs_manager** | `_world` (the ECS `World`), `_entity_to_alias` / `_alias_to_entity`, `_game_functions`, `_template_definitions` | `initialize`, `process`, `load_processor`, `create_processor`, `load_template`, `load_register_empty_entity`, `load_update_empty_entity`, `create_entity`, `delete_entity`, `delete_entities_pattern`, `update_component`, `delete_component`, `reinit_processors`, `reinit_components`, `get_entity_id`, `get_entity_alias`, `get_debug_info` |
| **event_manager** | `_event_queue` (a `deque`), `_event_handlers` | `init`, `add_event`, `get_events`, `clear_events`, `process_events`, `create_event`, `load_handler`, `delete_handler`, `delete_handlers_pattern` |
| **script_manager** | `_scripts` registry, alias-dict callback | `init`, `register_script`, `execute_event_actions`, `execute_script`, `clear_scripts` |
| **command_manager** | `_command_queue`, `_commands` registry | `add_command`, `get_command_queue`, `clear_command_queue`, `process_commands`, `register_command`, `get_command`, `execute_command`, `execute_command_init`, `execute_command_with_ctx` |
| **map_manager** | `_maps` | `load_map`, `get_map`, `delete_map`, `delete_maps_pattern`, `clear_maps` |
| **dialog_manager** | `_dialogs` | `load_dialog`, `delete_dialog`, `delete_dialogs_pattern`, `clear_dialogs` |
| **message_manager** | `_message_queue` | `add_message`, `get_messages`, `clear_messages` |
| **pathfind_manager** | `_req_queue`, `_req_lookup`, `_next_req_id` | `request_path`, `continue_pathfinding`, `get_path` |

### ecs_manager

The bridge between the scene pipeline and the ECS. Beyond the delegation helpers
(`component_for_entity`, `add_component`, `try_component`, `remove_component`, `process`) it owns:

- **Alias bookkeeping** — two dicts kept in sync. `check_lookup_tables()` asserts they are the same
  length. See [../_shared/aliases.md](../_shared/aliases.md).
- **Processor construction** — `create_processor` resolves the class, runs its `PREREQ` check, and
  performs the `game_functions` parameter-name matching described below.
- **Component construction** — `create_component_from_def` resolves `"module:ClassName"` against
  `MODULEPATHS["COMPONENT_MODULE_PATH"]`, alias-translates the params, and constructs.
- **Template storage** — `_template_definitions`, filled by `load_template` and, implicitly, by
  every entity that goes through `load_update_empty_entity`.
- **Diagnostics** — `get_all_entities`, `get_entities_with_alias`, `get_entities_wo_alias`,
  `get_empty_entities`, `get_proc_perf(sort=)`, `get_debug_info()`.

`ECSManagerMock` at the bottom of the module exists so that command modules' doctests can run
without a world.

### pathfind_manager

Pathfinding is **resumable across frames** so no single frame pays for a long search.

```python
req_id = request_path(graph, start, goal, search='BFS')   # enqueue, get a ticket
continue_pathfinding(max_steps=100)                        # spend a step budget this frame
path = get_path(req_id)                                    # None = still computing; [] = no path
```

`continue_pathfinding` divides its budget evenly: `max_steps // len(_req_queue)` per request;
`max_steps=None` means "finish everything now". Completed requests are dropped from the queue.

`get_path` **consumes** the result — it pops the request from `_req_lookup`, so a second call
returns `None`. Three search options exist, as `PathfindOption` members:

| Option | Search | Post-processing |
|--------|--------|-----------------|
| `BFS` | BFS | full path |
| `BFS_CHECKPOINTS` | BFS | `filter_checkpoints()` — only direction changes |
| `BFS_CHECKPOINTS_W_FIRST` | BFS | checkpoints, plus `include_start()` |

The graph comes from `Map.generate_path_graph()`, built once at map load: `{(x, y): [((nx, ny),
cost), …]}` over 4-way moves with uniform cost 1, restricted to tiles whose GID on the collision
layer is 0.

The game side reaches this through `PerformPathfindingCalculationProcessor`, configured in scenes as
`{"max_no_of_calcs": 100}`.

### message_manager

`get_messages()` is not a pure getter — it **prunes expired messages** each call, comparing
`pygame.time.get_ticks()` against each `Message.created + ttl`. It is exposed to processors as
`game_messages`, and the renderer calling it is what drives expiry.

### dialog_manager

`load_dialog(dialog_def)` resolves a `templates` chain of `.json` files under `DIALOG_PATH`
recursively (deeper templates merged first, then shallower, then the scene-level definition last),
then calls `pgrpg.utils.dialog.prepare_dlg_obj_from_data` to build pygame surfaces. So dialog
definitions support inheritance, but with a **shallow** `{**a, **b}` merge at each level — not the
recursive `merge_dicts` used for configuration.

## The `game_functions` wiring table

`engine.init()` builds one dict of engine callables and passes it to `ecs_manager.initialize()`.
Processors do not import managers; they **declare what they need as `__init__` parameters** and the
manager matches by name (`ecs_manager.create_processor`, `ecs_manager.py:173`):

```python
proc_attrs = new_class.__init__.__code__.co_varnames[1:]                       # param names, minus self
proc_attrs = {a: _game_functions.get(a) for a in proc_attrs
              if _game_functions.get(a) is not None}                            # matched by name
proc_attrs = {**proc_attrs, **cust_proc_class_attrs}                            # scene JSON wins
return new_class(**proc_attrs), proc_group
```

So a processor declared as

```python
def __init__(self, FNC_ADD_COMMAND, *args, **kwargs):
```

is handed `command_manager.add_command` automatically, and anything in the scene's params dict
overrides a same-named entry. **A typo in the parameter name silently yields no injection** — the
key is skipped, and the processor fails later with a `TypeError` on a missing argument or a `None`
callable. This is the single most common cause of "my new processor won't construct".

Note `co_varnames[1:]` includes *locals declared in `__init__`*, not only parameters — harmless in
practice, but it means an accidentally-named local could pick up an injection.

### The table

| Key | Bound to | Notes |
|-----|----------|-------|
| `window` | `gui_manager.window` | The pygame display surface. |
| `create_entity_fnc` | `ecs_manager.create_entity` | Runtime entity creation. |
| `remove_entity_fnc` | `ecs_manager.delete_entity` | |
| `maps` | `map_manager._maps` | The live dict, by reference. |
| `FNC_GET_MAP` | `map_manager.get_map` | Preferred over `maps`. |
| `FNC_ADD_EVENT` | `event_manager.add_event` | Canonical name. |
| `add_event_fnc` | `event_manager.add_event` | Older alias. |
| `teleport_event_queue` | `event_manager.add_event` | Legacy per-domain alias. |
| `weapon_event_queue` | `event_manager.add_event` | Legacy alias. |
| `ammo_pack_event_queue` | `event_manager.add_event` | Legacy alias. |
| `wearable_event_queue` | `event_manager.add_event` | Legacy alias. |
| `item_pickup_event_queue` | `event_manager.add_event` | Legacy alias. |
| `entity_coll_event_queue` | `event_manager.add_event` | Legacy alias. |
| `damage_event_queue` | `event_manager.add_event` | Legacy alias. |
| `destroy_event_queue` | `event_manager.add_event` | Legacy alias. |
| `score_event_queue` | `event_manager.add_event` | Legacy alias. |
| `clear_events_fnc` | `event_manager.clear_events` | |
| `get_events_fnc` | `event_manager.get_events` | |
| `game_event_handler` | `event_manager.process_events` | Used by `GameEventsExProcessor`. |
| `game_messages` | `message_manager.get_messages` | |
| `add_message` | `message_manager.add_message` | |
| `FNC_ADD_COMMAND` | `command_manager.add_command` | |
| `FNC_CLEAR_COMMANDS` | `command_manager.clear_command_queue` | |
| `FNC_GET_COMMANDS` | `command_manager.get_command_queue` | |
| `FNC_PROCESS_COMMANDS` | `command_manager.process_commands` | Used by `PerformCommandProcessor`. |
| `FNC_EXEC_CMD_INIT` | `command_manager.execute_command_init` | For the `do_parallel` command. |
| `FNC_EXEC_CMD` | `command_manager.execute_command` | For the `do_parallel` command. |
| `FNC_CALC_PATHS` | `pathfind_manager.continue_pathfinding` | |
| `FNC_REQUEST_PATHFIND` | `pathfind_manager.request_path` | |
| `FNC_GET_PATH` | `pathfind_manager.get_path` | |
| `FNC_GET_ENTITY_ID` | `ecs_manager.get_entity_id` | |
| `REF_ECS_MNG` | the `ecs_manager` **module itself** | Full access — commands receive it as `ecs_mng`. |
| `FNC_PLAY_SOUND` | `sound_manager.play_sound` | |

The nine `*_event_queue` keys are all the same function. They are historical: the engine once had a
queue per domain. New processors should declare `FNC_ADD_EVENT`.

`REF_ECS_MNG` is the escape hatch: any processor or command holding it can do anything to the world.
`PerformCommandProcessor` takes it and forwards it into `command_manager.process_commands`, which is
how every command function receives its `ecs_mng` argument.

## Adding a new engine function

1. Add the key and callable to the dict in `engine.init()` (`pgrpg/core/engine.py:60`).
2. Declare a parameter of exactly that name in the consuming processor's `__init__`.
3. `super().__init__(*args, **kwargs)` first, so throttling still works.

Prefer the `FNC_`/`REF_` naming for anything new — it makes the injected parameters obvious at the
call site.

## Related

- [events-and-scripts.md](events-and-scripts.md) — event_manager and script_manager in depth.
- [commands-and-ai.md](commands-and-ai.md) — command_manager in depth.
- [../ecs/processors.md](../ecs/processors.md) — the processor side of the injection.
- [scene-pipeline.md](scene-pipeline.md) — which manager function each pipeline step calls.
