# Core Engine

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/**` @ `c7b9a5f1`

The **core** is everything in `pgrpg/core/` except the ECS itself: the bootstrap, the game loop,
the configuration system, the scene-loading pipeline, and the eight managers that own the game's
mutable state.

## Shape of the core

There is **no dependency-injection container and no god object**. Every manager is a *module*, not
a class instance, holding module-level globals. They are wired together exactly twice:

1. `pgrpg/core/engine.py` at **import time** calls `script_manager.init(...)` and
   `event_manager.init(...)`, giving each the one callback it needs from the other.
2. `engine.init()` builds a single `game_functions` dict of engine callables and hands it to
   `ecs_manager.initialize()`. Processors later receive entries from that dict by **matching their
   `__init__` parameter names against its keys**.

That second mechanism is the one non-obvious thing about the core — see
[managers.md §The game_functions wiring table](managers.md#the-game_functions-wiring-table).

## Pages

| Page | Covers |
|------|--------|
| [bootstrap-and-loop.md](bootstrap-and-loop.md) | `pgrpg.init()` → config → engine → state modules → scene; the frame; `reinit()`; the state machine |
| [configuration.md](configuration.md) | Two-file config merge, the `_prep_conf_*` / `_init_*` split, every config section |
| [scene-pipeline.md](scene-pipeline.md) | `load_scene_def_fncs`, the 15 pipeline steps, `prereqs`, `cleanup`, two-pass entity loading |
| [managers.md](managers.md) | All eight managers, their public surface, and the `game_functions` table |
| [events-and-scripts.md](events-and-scripts.md) | Event queue, handler registry, dispatch, `json_logic` execution, lazy script loading |
| [commands-and-ai.md](commands-and-ai.md) | Command queue, `CommandContext` blackboards, `BTree` and `BList` generators |

## Module map

```
pgrpg/core/
  main.py        148 lines  init() + run(): the game loop; also the console's CLI app module
  engine.py      263 lines  manager wiring, scene loading pipeline, _clear_game()
  scene.py        32 lines  Scene — inert metadata object (id/title/description/objective/stats)
  config/
    __init__.py  517 lines  config load() + init(); global config dicts
    defaults.jsonc          engine defaults — do not edit for game-specific values
    states.py    158 lines  State enum built from config; state graph; state module registry
    gui.py                  display/GUI manager (module singleton) + ProgressBar
    sound.py                sound/music manager (module singleton)
    console.py              header/footer info functions for the dev console
  managers/               8 manager modules — see managers.md
  ecs/__init__.py 593 lines esper 1.3 fork — see ../ecs/
  commands/               Command types + generators/{btree,blist}
  events/event.py          Event data object
  maps/map.py              Map wrapper around pytmx
  models/model.py          Model — cached animated sprite sheet
  messages/messages.py     Message data object
  pathfinding/__init__.py  BFS search, resumable across frames
  sounds/, states/         Sound wrapper; empty namespace package for game states
```

`pgrpg/functions/` holds pure utilities (`json_logic`, `translate`, `get_dict_params`,
`get_dict_from_file`, `dict_utils`, `str_utils`, …). `pgrpg/utils/` holds authoring/dev tools
(bitmap frames, dialog builders, JSON generators) — not used at runtime by the game loop.
