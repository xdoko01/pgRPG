# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project summary

**pgrpg** is a Pygame-based 2D RPG game engine built around Entity–Component–System (ECS) architecture. All game logic, AI, scenes, and UI flows are defined in **JSON/YAML data files** — not in Python. The engine is an installable Python package consumed by a game project (e.g., `example_game/`).

Design priority: **clarity and readability over performance**.

---

## Repository layout

```
pgrpg/                  — the engine package (published via pyproject.toml)
  core/
    main.py             — entry point: init() + run() game loop
    engine.py           — scene loading pipeline + manager wiring
    scene.py            — lightweight Scene data object
    ecs/
      __init__.py       — custom esper fork: World, Component, Processor base classes
    managers/
      ecs_manager.py    — ECS world wrapper; loads processors/templates/entities/components
      event_manager.py  — event queue + JSON-defined handler dispatch
      script_manager.py — lazy-loads Python script modules; executes json_logic action trees
      command_manager.py— entity command queue (BTree/AI-generated commands)
      map_manager.py    — Tiled tile map loading/management
      dialog_manager.py — scriptable dialog flow definitions
      message_manager.py— in-game message log
      pathfind_manager.py— non-blocking pathfinding distributed across cycles
    config/
      gui.py            — pygame display / GUI manager (module-level singleton)
      sound.py          — sound/music manager (module-level singleton)
      states.py         — State enum + state machine
    commands/
      generators/
        btree/          — behavior tree command generator
        blist/          — ordered command list generator
    events/event.py     — Event dataclass
    states/state.py     — State enum (MAIN_MENU, GAME, CONSOLE, etc.)
    maps/map.py         — Map wrapper around pytmx
    models/model.py     — Model (sprite/animation data)
    sounds/sound.py     — Sound wrapper
  functions/            — pure utility functions
    get_dict_from_file.py — load JSON/YAML with C-style comment support
    json_logic.py       — JSON-encoded condition/action tree evaluator
    translate.py        — replace entity alias strings with integer ECS IDs
    get_dict_params.py  — fill template dicts with variable substitution
    allow_deny_filters.py, dict_utils.py, str_utils.py, ...
  utils/                — dev/authoring tools
    entity_json_generator.py, generate_model_json_from_template.py, ...

example_game/           — reference game built on pgrpg (NOT part of the package)
  game.py               — runnable entry point
  config.jsonc          — game-specific config (overrides pgrpg defaults)
  core/
    components/         — game-specific Component classes (inherit pgrpg.core.ecs.Component)
    processors/         — game-specific Processor classes (inherit pgrpg.core.ecs.Processor)
    scripts/            — event action scripts (loaded lazily by ScriptManager)
    commands/           — command implementations for CommandManager
    states/             — state module implementations (main menu, pause, etc.)
    console/            — in-game dev console commands and scripts
  resources/
    scenes/             — scene definition files (.jsonc / .yaml)
      empty.jsonc       — minimal scene template
      tests/00_render … 12_ai/  — numbered progressive test scenes
      games/            — complete game scenes (sokoban, collect_coins, kill_all)
    entities/           — reusable entity definition files
    maps/               — Tiled map files (.tmx)
    btrees/             — behavior tree definition files
    dialogs/            — dialog flow definition files
    images/, sounds/, music/, fonts/, frames/, models/

tests/                  — Python unit tests (pytest)
```

---

## Architecture

### Module-level singletons

All managers in `pgrpg/core/managers/` are **modules, not class instances**. There is no DI container — the engine wires them by passing a `game_functions` dict to `ecs_manager.initialize()` at startup. The old class-based versions are preserved as commented-out code in each manager file.

### State machine

`pgrpg/core/config/states.py` holds the `State` enum. Each state (MAIN_MENU, GAME, CONSOLE, PAUSE_GAME, …) maps to a state module with a `run(key_events, key_pressed, dt)` method. `state_manager.change_state()` switches between them each frame.

### ECS (esper fork)

`pgrpg/core/ecs/__init__.py` is a modified esper 1.3 fork with:
- **Processor groups** — processors can be added to named groups and processed independently
- **Execution throttling** — `exec_cycle_step` lets a processor run every N cycles instead of every frame
- **Extended queries** — `get_components_ex` / `get_components_exs` / `get_components_opt` for include/exclude/optional component filtering
- **`SkipProcessorExecution`** exception to skip a processor's logic without an error

**Component** — inherit `pgrpg.core.ecs.Component`, use `__slots__` for memory efficiency. Implement `reinit()` for display config changes and `pre_save()` / `post_load()` for serialization.

**Processor** — inherit `pgrpg.core.ecs.Processor`, implement `process(**kwargs)` (call `super().process()` first to handle cycle throttling).

### Scene loading pipeline

`engine.load_scene_from_def()` walks `load_scene_def_fncs` — an ordered list of `[json_path, handler_fn]` pairs:

```
prereqs             → recursively load dependency scenes
cleanup/processors  → remove processors matching pattern
cleanup/maps        → remove maps matching pattern
cleanup/templates   → remove templates matching pattern
cleanup/entities    → remove entities matching pattern
cleanup/dialogs     → remove dialogs matching pattern
cleanup/handlers    → remove handlers matching pattern
processors          → register Processors into the ECS World
maps                → load Tiled maps
dialogs             → load dialog flow definitions
templates           → load entity templates (parameterised)
entities (×1)       → register all entities first (so aliases exist)
entities (×2)       → fill entities with components (aliases now resolve)
entities/…/handlers → load handlers embedded inside component params
handlers            → load top-level event handlers
```

### Per-frame data flow

```
pygame events + keys
  → state_module.run()
    → ecs_manager.process()     ← all Processors tick in priority order
      Processors emit:
        → event_manager.add_event()     (game events)
        → command_manager.add_command() (entity commands / AI)
      → command_manager.process_commands()
      → event_manager.process_events()
        → match event_type → handler(s) defined in scene JSON
          → script_manager.execute_event_actions()
            → translate(alias → entity_id)
            → json_logic(actions)
              → execute_script(name)  ← lazy-loaded Python script module
→ gui_manager.flip()
```

### Entity aliases

Entities have string aliases in JSON (e.g. `"player"`, `"enemy_1"`). Before any script executes, `script_manager` calls `translate()` to replace those strings with integer ECS entity IDs. This means **aliases must be fully registered before any handler fires**.

---

## Configuration

Two config files are merged at startup:

1. `pgrpg/core/config/default.jsonc` — engine defaults (do not edit directly)
2. `<game>/config.jsonc` — game overrides, passed as `config_file` argument

Key config sections:

| Section | Purpose |
|---|---|
| `DISPLAY` | Resolution, FPS, fullscreen, window title |
| `FILEPATHS` | `GAME_PATH`, `pgrpg_PATH`, and all resource sub-paths |
| `MODULEPATHS` | Python module paths for components, processors, scripts, commands, states, console commands |
| `KEYS` | Key bindings |
| `GAME` | Game-specific constants (speed, tile size, timers) |

`FILEPATHS.GAME_PATH` and `FILEPATHS.pgrpg_PATH` are **mandatory**.

`MODULEPATHS` entries control where the engine looks for game code. Example:
```json
"COMPONENT_MODULE_PATH": "core.components"  // → example_game.core.components.*
```

---

## Scene file format

Scene files are `.jsonc` (JSON with C-style `// comments`) or `.yaml`. Top-level keys match the scene loading pipeline:

```jsonc
{
    "id": "my_scene",
    "title": "My Scene",
    "description": "...",
    "objective": "...",

    "prereqs": [],                  // other scene files to load first

    "cleanup": {                    // UNIX-wildcard patterns for removal
        "processors": [],
        "maps": [], "templates": [], "entities": [],
        "dialogs": [], "handlers": []
    },

    "processors": [
        // ["module.ClassName", {params}]         ← default group
        // ["group_id", "module.ClassName", {params}]  ← named group
        ["render_system.some_processor:SomeProcessor", {"param": "value"}]
    ],

    "maps": [...],
    "dialogs": [...],
    "templates": [...],
    "entities": [...],

    "handlers": [
        ["EVENT_TYPE", {
            "id": "handler_id",
            "actions": ["SCRIPT", "script_name", {"arg": "value"}]
        }]
    ]
}
```

Entity definition inside `entities`:
```jsonc
{
    "id": "player",
    "components": [
        {"type": "Position", "params": {"x": 5, "y": 5}},
        {"type": "Brain",    "params": {"commands": [[null, "move", {"dx": 64}]]}}
    ]
}
```

---

## Writing Components

```python
from pgrpg.core.ecs import Component

class MyComponent(Component):
    __slots__ = ['value', 'active']

    def __init__(self, value=0, active=True):
        self.value = value
        self.active = active

    def reinit(self):
        pass  # called on display config change
```

Place in the path matching `MODULEPATHS.COMPONENT_MODULE_PATH` (e.g. `example_game/core/components/my_component.py`).

Reference in JSON: `{"type": "MyComponent", "params": {"value": 42}}`

---

## Writing Processors

```python
from pgrpg.core.ecs import Processor, SkipProcessorExecution
import example_game.core.components as c

class MyProcessor(Processor):

    def __init__(self, game_functions: dict, **kwargs):
        super().__init__(**kwargs)
        self._add_event = game_functions["FNC_ADD_EVENT"]

    def process(self, events, keys, dt, **kwargs):
        super().process()  # handles exec_cycle_step throttling
        for ent, [pos, mov] in self.world.get_components(c.Position, c.Movable):
            # ... do work ...
            pass
```

Place in `MODULEPATHS.PROCESSOR_MODULE_PATH`. Reference in scene JSON:
```jsonc
["my_processor_module:MyProcessor", {"step": 2}]
```

The `game_functions` dict keys available to processors are defined in `engine.py:init()`.

---

## Writing Scripts (event action handlers)

Scripts are Python modules loaded lazily by `ScriptManager`. Each must expose an `initialize(register, name)` function:

```python
def initialize(register, name):
    register(_run, name)

def _run(event, **kwargs):
    # event.params contains the event parameters
    # kwargs are the action arguments from JSON
    pass
```

Place in `MODULEPATHS.SCRIPT_MODULE_PATH`. Reference in handler JSON:
```jsonc
"actions": ["SCRIPT", "my_script_module", {"arg": "value"}]
```

---

## AI: Brain + Commands

Entities with a `Brain` component hold a command list. Each entry is a tuple:
```python
[exception_goto_index, "command_name", {"param": "value"}]
```

The `BrainProcessor` advances the brain's index each frame, adds the current command to `command_manager`, and moves to the next on success or jumps to `exception_goto_index` on failure.

Command modules live in `MODULEPATHS.COMMAND_MODULE_PATH`. For more complex AI, `BTreeAI` and `BListAI` components use behavior trees (`resources/btrees/`) or parameterised command lists.

---

## Running the example game

```bash
# Install dependencies
pip install -e .

# Run with default scene (sokoban)
python example_game/game.py

# Run a specific scene (path is relative to SCENE_PATH in config, not project root)
python example_game/game.py -f tests/01_movements/test_movement_01.jsonc
python example_game/game.py -f games/sokoban/sokoban.jsonc

# Start into main menu
python example_game/game.py -s MAIN_MENU

# Start into the dev console
python example_game/game.py   # (default, no scene_file set)
```

The in-game dev console (toggle with F9 by default) supports commands and `.scr` scripts for ad-hoc inspection and testing.

---

## Testing

```bash
# Run all tests
pytest tests/

# Run a single test by name
pytest tests/test_ecs.py::test_processor_execution_control

# Run doctests in a component module
python -m example_game.core.components.brain -v
```

---

## JSON Schemas

JSON Schema (Draft-07) definitions for all components, commands, and processors live in `example_game/core/schemas/`. They are auto-generated from Python class signatures via `pgrpg/utils/` tools and can be used in editors for validation and auto-complete when authoring `.jsonc` scene/entity files.

Top-level schemas: `scene.schema.json`, `entity.schema.json`, `template.schema.json`, `component.schema.json`, `command.schema.json`.

---

## Key conventions

- **Readability over performance** — prefer clear names and explicit code.
- **No new files unless necessary** — extend existing components/processors.
- **Aliases everywhere** — use entity string aliases in JSON; the engine resolves them to IDs automatically.
- **UNIX wildcard patterns** in `cleanup` sections (`"enemy_*"`) for bulk removal when reloading scenes.
- **C-style comments** (`// ...`) are supported in all `.jsonc` files.
- **Processor priority** — higher number = processed first. Default group is `"default"`.
- **`__slots__`** in Components — required for memory efficiency and the `__str__` implementation.
- Managers are **modules, not classes** — do not instantiate them; call their functions directly.