# pgrpg — ECS Pygame Game Engine

![pgrpg Screenshot](docs/empty_01.png)

**pgrpg** is a Pygame-based 2D RPG game engine built around an Entity–Component–System (ECS) architecture with strong emphasis on data-driven design, behavior trees, and event-driven gameplay. Game logic, AI behavior, scenes, processors, and even UI flows are primarily defined in JSON/YAML — enabling rapid iteration without touching engine code.

The engine is designed for experimentation with RPG mechanics, AI orchestration, and systemic gameplay rather than as a monolithic framework.

![pgrpg Screenshot](docs/test_sensors_01.png)

> **Learn by doing!** Documentation is still growing. The best way to understand the engine is to browse the numbered test scenes under `example_game/resources/scenes/tests/`, run them, read the JSON, and tweak things. There are comments throughout to guide you.

All of this grew from personal experimentation with Python and the ECS paradigm. Clarity and readability were prioritized over raw performance so the code stays approachable.

![pgrpg Screenshot](docs/sokoban_02.png)

---

## Key Features

| Feature | Description |
|---|---|
| ECS | Entity–Component–System powered by a custom esper fork |
| AI | Behavior Trees (BTrees), ordered command lists (BLists), and Brain command queues |
| Events | Event-driven architecture — conditions and actions defined in JSON |
| Data-driven | Scenes, entities, processors, handlers all in JSON/YAML with C-style comments |
| Processor groups | Named processor groups activated per game state (e.g. separate inventory loop) |
| Non-blocking pathfinding | BFS pathfinding distributed across game cycles |
| Combat systems | Modular damage, health, score, destruction, arming/disarming |
| Inventory | Drag-and-drop inventory with configurable slot layout |
| FX systems | Sound and visual effects bound to component lifecycle events |
| Cameras | Multiple cameras, split-screen, scroll, delayed-scroll |
| Dialogs | Scriptable dialog flows |
| Dev console | In-game F9 console with commands and `.scr` scripts |
| JSON schemas | JSON Schema (Draft-07) definitions for all components, commands, and processors |

---

## Installation & Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd pgRPG

# Install the engine package and dependencies
pip install -e .

# Run the example game (defaults to sokoban)
python example_game/game.py

# Run a specific test scene
python example_game/game.py --file tests/01_movements/test_movement_01.jsonc

# Start directly into the main menu
python example_game/game.py --state MAIN_MENU

# Start in the dev console (no scene file = console entry)
python example_game/game.py
```

The in-game dev console (toggle with **F9**) lets you inspect entities, components, and processor timings, and run `.scr` scripts for ad-hoc control.

---

## Repository Layout

```
pgRPG/
├── pgrpg/                      Engine package (installable via pyproject.toml)
│   └── core/
│       ├── main.py             Entry point: init() + game loop
│       ├── engine.py           Scene loading pipeline + manager wiring
│       ├── scene.py            Lightweight Scene data object
│       ├── ecs/
│       │   └── __init__.py     Custom esper fork: World, Component, Processor
│       ├── managers/
│       │   ├── ecs_manager.py      ECS world wrapper (processors/templates/entities)
│       │   ├── event_manager.py    Event queue + JSON-defined handler dispatch
│       │   ├── script_manager.py   Lazy-loads Python script modules; executes json_logic trees
│       │   ├── command_manager.py  Entity command queue (Brain/BTree/BList-generated)
│       │   ├── map_manager.py      Tiled tile map loading and management
│       │   ├── dialog_manager.py   Scriptable dialog flow definitions
│       │   ├── message_manager.py  In-game message log
│       │   └── pathfind_manager.py Non-blocking pathfinding (BFS, distributed)
│       ├── config/
│       │   ├── gui.py          Pygame display/GUI manager (module-level singleton)
│       │   ├── sound.py        Sound/music manager (module-level singleton)
│       │   └── states.py       State enum + state machine
│       ├── commands/generators/
│       │   ├── btree/          Behavior Tree command generator
│       │   └── blist/          Ordered command list generator
│       └── functions/          Pure utility functions
│           ├── get_dict_from_file.py   JSON/YAML loader with C-style comment support
│           ├── json_logic.py           JSON-encoded condition/action tree evaluator
│           ├── translate.py            Alias string → integer ECS ID substitution
│           └── get_dict_params.py      Template variable substitution ($var)
│
└── example_game/               Reference game built on pgrpg (not part of the package)
    ├── game.py                 Runnable entry point
    ├── config.jsonc            Game-specific config (overrides pgrpg defaults)
    └── core/
        ├── components/         Game-specific Component classes
        ├── processors/         Game-specific Processor classes (20 system subdirs)
        │   ├── animation_system/
        │   ├── arm_ammo_system/
        │   ├── arm_weapon_system/
        │   ├── attack_system/
        │   ├── collision_system/
        │   ├── command_system/
        │   ├── damage_system/
        │   ├── debug_system/
        │   ├── destroy_system/
        │   ├── drop_system/
        │   ├── effects_system/
        │   ├── event_system/
        │   ├── factory_system/
        │   ├── gui_system/
        │   ├── movement_system/
        │   ├── pickup_system/
        │   ├── position_system/
        │   ├── render_system/
        │   ├── score_system/
        │   ├── sensor_system/
        │   └── teleport_system/
        ├── scripts/            Event action scripts (lazy-loaded by ScriptManager)
        ├── commands/           Command implementations for CommandManager
        ├── states/             State module implementations (main menu, pause, …)
        ├── console/            Dev console commands and scripts
        └── schemas/            JSON Schema definitions
            ├── scene.schema.json
            ├── entity.schema.json
            ├── template.schema.json
            ├── component.schema.json   ← top-level component dispatcher
            ├── command.schema.json     ← top-level command dispatcher
            ├── processor.schema.json   ← top-level processor dispatcher
            ├── definitions.schema.json ← shared type definitions
            ├── components/             One schema per Component class
            ├── commands/               One schema per command
            └── processors/             One schema per Processor (grouped by system)

    └── resources/
        ├── scenes/             Scene definition files (.jsonc / .yaml)
        │   ├── empty.jsonc             Minimal scene template
        │   ├── tests/                  Numbered progressive test scenes (00–12)
        │   └── games/                  Complete game scenes (sokoban, collect_coins, kill_all)
        ├── entities/           Reusable entity definition files
        ├── maps/               Tiled map files (.tmx)
        ├── btrees/             Behavior tree definition files
        ├── dialogs/            Dialog flow definition files
        └── images/, sounds/, music/, fonts/, frames/, models/
```

---

## Architecture Overview

### Module-level singletons

All managers in `pgrpg/core/managers/` are **modules, not class instances**. There is no dependency-injection container — the engine wires them by passing a `game_functions` dict to `ecs_manager.initialize()` at startup. Functions from multiple managers are collected into this dict and injected into every Processor.

```python
# engine.py — wiring example (excerpt)
ecs_manager.initialize(game_functions={
    "FNC_ADD_EVENT":   event_manager.add_event,
    "FNC_GET_MAP":     map_manager.get_map,
    "FNC_ADD_COMMAND": command_manager.add_command,
    ...
})
```

### State machine

`pgrpg/core/config/states.py` holds the `State` enum. Each state (`MAIN_MENU`, `GAME`, `CONSOLE`, `PAUSE_GAME`, …) maps to a state module with a `run(key_events, key_pressed, dt)` method. `state_manager.change_state()` switches between them each frame.

### ECS (custom esper fork)

`pgrpg/core/ecs/__init__.py` is a modified esper 1.3 with added capabilities:

| Addition | Purpose |
|---|---|
| **Processor groups** | Processors belong to named groups (e.g. `"default"`, `"inventory"`) and can be ticked independently |
| **Execution throttling** | `exec_cycle_step=N` makes a Processor run every N cycles instead of every frame |
| **Extended queries** | `get_components_ex` / `get_components_exs` / `get_components_opt` for include/exclude/optional filtering |
| **`SkipProcessorExecution`** | Exception raised inside `super().process()` to skip a Processor's logic cleanly |

**Component** — inherit `pgrpg.core.ecs.Component`, use `__slots__` for memory efficiency. Optionally implement `reinit()` for display config changes and `pre_save()` / `post_load()` for serialization.

**Processor** — inherit `pgrpg.core.ecs.Processor`, implement `process(**kwargs)`. Always call `super().process()` first to handle cycle throttling.

### Scene loading pipeline

`engine.load_scene_from_def()` walks an ordered list of `[json_path, handler_fn]` pairs:

```
prereqs             → recursively load dependency scenes first
cleanup/processors  → remove processors matching UNIX wildcard pattern
cleanup/maps        → remove maps matching pattern
cleanup/templates   → remove templates matching pattern
cleanup/entities    → remove entities matching pattern
cleanup/dialogs     → remove dialogs matching pattern
cleanup/handlers    → remove handlers matching pattern
processors          → register Processors into the ECS World
maps                → load Tiled maps
dialogs             → load dialog flow definitions
templates           → load entity templates (parameterized with $vars)
entities (pass 1)   → register all entities first so aliases exist
entities (pass 2)   → fill entities with components (aliases now resolve)
entities/…/handlers → load handlers embedded inside component params
handlers            → load top-level scene event handlers
```

The two-pass entity loading ensures aliases registered later in the file are available when components of earlier entities reference them.

### Per-frame data flow

```
pygame events + keys
  └─▶ state_module.run()
        └─▶ ecs_manager.process()         — all Processors tick in priority order
              │
              ├─ Processors emit:
              │    event_manager.add_event()      (game events: collision, damage, …)
              │    command_manager.add_command()  (entity commands from AI/input)
              │
              ├─▶ command_manager.process_commands()
              │     └─▶ command.process()         — move, attack, wait, …
              │
              └─▶ event_manager.process_events()
                    └─▶ handler(s) from scene JSON
                          └─▶ script_manager.execute_event_actions()
                                ├─ translate(alias → entity_id)
                                └─ json_logic(actions)
                                      └─▶ execute_script(name)  — lazy-loaded Python module
  └─▶ gui_manager.flip()
```

### Entity aliases

Entities have string aliases in JSON (e.g. `"player"`, `"enemy_1"`). Before any script executes, `script_manager` calls `translate()` to replace those strings with integer ECS entity IDs. This means **all aliases must be registered before handlers fire** — which the two-pass entity loading guarantees.

### Event system

Game events flow through `event_manager`. Processors enqueue events via `add_event()`; the `GameEventsExProcessor` drains the queue each frame by calling `process_events()`. Each event type can have multiple handlers defined in scene JSON. The `process` and `ignore` parameters allow a handler instance to selectively act on only certain event types.

Key event types used internally: `SCENE_START`, `ITEM_PICK`, `ITEM_DROP`, `ENTITY_COLLIDE`, `ENTITY_DAMAGE`, `ENTITY_DESTROY`, `ENTITY_SCORE`, `TELEPORT`.

### Command system

Commands are the unit of entity behavior. Each command is a Python class with a `process()` method returning `SUCCESS`, `FAILURE`, or `RUNNING`. Commands are generated each frame by:

| Generator | Source |
|---|---|
| `GenerateCommandFromInputProcessor` | Keyboard/mouse input via `Controllable` component |
| `GenerateCommandFromBrainProcessor` | `Brain` component command list (sequential AI) |
| `GenerateCommandFromBTreeProcessor` | Behavior Tree (`BTreeAI` component) |
| `GenerateCommandFromBListProcessor` | Ordered command list (`BListAI` component) |
| `GenerateCommandFromFileProcessor` | Recorded command file (playback) |

---

## Configuration

Two config files are merged at startup:

1. `pgrpg/core/config/default.jsonc` — engine defaults (do not edit directly)
2. `<game>/config.jsonc` — game overrides

| Section | Purpose |
|---|---|
| `DISPLAY` | Resolution, FPS, fullscreen, window title, font settings |
| `FILEPATHS` | `GAME_PATH`, `pgrpg_PATH`, and all resource sub-paths |
| `MODULEPATHS` | Python module paths for components, processors, scripts, commands, states, console |
| `KEYS` | Key bindings |
| `GAME` | Game-specific constants (speed, tile size, timers) |

`MODULEPATHS` controls where the engine looks for game code:
```jsonc
// example_game/config.jsonc
"COMPONENT_MODULE_PATH": "core.components",   // → example_game.core.components.*
"PROCESSOR_MODULE_PATH": "core.processors",   // → example_game.core.processors.*
"SCRIPT_MODULE_PATH":    "core.scripts",
"COMMAND_MODULE_PATH":   "core.commands"
```

---

## Scene File Format

Scene files are `.jsonc` (JSON with C-style `// comments`) or `.yaml`. All paths are relative to `FILEPATHS.SCENE_PATH`.

```jsonc
{
    "$schema": "../../core/schemas/scene.schema.json",  // enables IDE validation

    "id":          "my_scene",
    "title":       "My Scene",
    "description": "What this scene is about.",
    "objective":   "What the player should do.",

    // Scenes to fully load before this one
    "prereqs": ["common/base_scene.jsonc"],

    // Remove previously loaded objects (UNIX wildcards supported)
    "cleanup": {
        "processors": ["my_old_proc*"],
        "maps":       ["old_map*"],
        "templates":  [],
        "entities":   ["enemy_*"],
        "dialogs":    [],
        "handlers":   ["old_handler_*"]
    },

    // ["module.ClassName", {params}]                    ← default group
    // ["group_id", "module.ClassName", {params}]        ← named group
    "processors": [
        ["render_system.perform_render_map_processor:PerformRenderMapProcessor", {}],
        ["render_system.perform_render_model_processor:PerformRenderModelProcessor", {}],
        ["inventory", "render_system.perform_render_inventory_processor:PerformRenderInventoryProcessor", {}]
    ],

    "maps": [
        {"id": "test_map", "file": "test_map.tmx"}
    ],

    "templates": [
        {
            "id": "t_tile_pos",
            "vars": ["$tileX", "$tileY", "$map"],
            "components": [
                {"type": "position:Position", "params": {"tile_x": "$tileX", "tile_y": "$tileY", "map": "$map"}}
            ]
        }
    ],

    "entities": [
        {
            "id": "player",
            "components": [
                {"type": "position:Position",     "params": {"tile_x": 5, "tile_y": 5, "map": "test_map"}},
                {"type": "movable:Movable",       "params": {"speed": 128}},
                {"type": "controllable:Controllable", "params": {
                    "control_cmds": {
                        "up":    [["move_dir", {"moves": [["up",    64]]}]],
                        "down":  [["move_dir", {"moves": [["down",  64]]}]],
                        "left":  [["move_dir", {"moves": [["left",  64]]}]],
                        "right": [["move_dir", {"moves": [["right", 64]]}]]
                    },
                    "key_feedback": {"up": "move_up", "down": "move_down", "left": "move_left", "right": "move_right"}
                }},
                {"type": "renderable_model:RenderableModel", "params": {"model": "dark_male.json"}}
            ]
        }
    ],

    // [event_type, {id, actions}]
    "handlers": [
        ["SCENE_START", {
            "id": "on_start",
            "actions": ["SCRIPT", "show_msg_window", {"html_text": "Welcome to <b>My Scene</b>!"}]
        }],
        ["ENTITY_COLLIDE", {
            "id": "on_collide",
            "actions": ["SCRIPT", "some_collision_script", {}]
        }]
    ]
}
```

### Template instantiation

Templates are reusable entity blueprints with `$var` placeholders. They can be referenced from other entity definitions:

```jsonc
// Using a template — string form
"templates": ["t_tile_pos(3, 7, test_map)"]

// Using a template — list form (supports complex param objects)
"templates": [["t_tile_pos", {"$tileX": 3, "$tileY": 7, "$map": "test_map"}]]
```

---

## Writing Components

```python
# example_game/core/components/my_component.py
from pgrpg.core.ecs import Component

class MyComponent(Component):
    __slots__ = ['value', 'active']   # required — enables __str__ and memory efficiency

    def __init__(self, value: int = 0, active: bool = True):
        self.value  = value
        self.active = active

    def reinit(self):
        pass  # called on display config change (resolution, fullscreen)
```

Reference in scene JSON:
```jsonc
{"type": "my_component:MyComponent", "params": {"value": 42}}
```

The `type` string format is `module_stem:ClassName`, resolved relative to `MODULEPATHS.COMPONENT_MODULE_PATH`.

---

## Writing Processors

```python
# example_game/core/processors/my_system/my_processor.py
from pgrpg.core.ecs import Processor, SkipProcessorExecution
import example_game.core.components as c

class MyProcessor(Processor):

    def __init__(self, game_functions: dict, **kwargs):
        super().__init__(**kwargs)
        # Pull only what you need from game_functions
        self._add_event = game_functions["FNC_ADD_EVENT"]

    def process(self, events, keys, dt, **kwargs):
        super().process()  # handles exec_cycle_step throttling; may raise SkipProcessorExecution

        for ent, (pos, mov) in self.world.get_components(c.Position, c.Movable):
            # do work — query components, add events, add commands
            pass
```

Reference in scene JSON (note: `module.submodule:ClassName` path is relative to `MODULEPATHS.PROCESSOR_MODULE_PATH`):
```jsonc
["my_system.my_processor:MyProcessor", {"exec_cycle_step": 2}]
// or with a named group:
["inventory", "my_system.my_processor:MyProcessor", {}]
```

Common `game_functions` keys available in processors:

| Key | Purpose |
|---|---|
| `FNC_ADD_EVENT` | Enqueue a game event |
| `FNC_GET_MAP` | Get a loaded Tiled map by name |
| `FNC_ADD_COMMAND` | Add a command to the command queue |
| `FNC_GET_ENTITY_ID` | Resolve alias → entity integer ID |
| `FNC_PLAY_SOUND` | Play a sound effect |
| `FNC_REQUEST_PATHFIND` | Request a pathfinding calculation |
| `FNC_GET_PATH` | Retrieve a completed path |
| `REF_ECS_MNG` | Direct reference to the ECS manager module |

---

## Writing Scripts (event action handlers)

Scripts are Python modules lazy-loaded by `ScriptManager`. Each must expose an `initialize(register, name)` function that registers the handler:

```python
# example_game/core/scripts/my_script.py
import logging
logger = logging.getLogger(__name__)

def initialize(register: callable, name: str) -> None:
    register(_run, name)

def _run(event, **kwargs):
    # event.event_type  — string event type
    # event.params      — dict of event parameters
    # **kwargs          — action arguments from scene JSON
    logger.info("my_script called for event %s", event.event_type)
```

Reference in handler JSON:
```jsonc
"actions": ["SCRIPT", "my_script", {"arg1": "value", "arg2": 42}]
```

Scripts can use `json_logic` conditions to branch behavior and can enqueue further events or commands by importing manager modules directly.

---

## AI: Brain + Commands

### Brain (sequential command list)

Entities with a `Brain` component hold a simple command list. Each entry is a 3-element tuple:

```jsonc
{"type": "brain:Brain", "params": {
    "commands": [
        [null,  "wait",      {"ms": 500}],     // index 0 — wait, jump to null on fail (stop)
        [0,     "move_to",   {"pos": [5, 3]}], // index 1 — move; on fail jump back to index 0
        [null,  "reset_brain", {}]              // index 2 — restart the sequence
    ]
}}
```

Format: `[exception_goto_index | null, "command_name", {params}]`

The Brain processor advances the index each frame, reads `SUCCESS`/`FAILURE`/`RUNNING` from the command, and moves forward or jumps to the exception index.

### Behavior Trees (BTree)

More complex AI uses `BTreeAI` component pointing to a `.json` behavior tree file:

```jsonc
{"type": "btree_ai:BTreeAI", "params": {"btree": "enemy_patrol.json"}}
```

Behavior trees are defined under `resources/btrees/`. Supported node types include Sequence, Selector, Repeater, Inverter, and leaf nodes that execute game commands.

Sensor commands for BTree conditions:
- `test_can_see` — check if target entities are in the sight cone
- `test_can_hear` — check if target entities are within earshot
- `test_damaged` — check if this entity was recently damaged
- `test_bb_value` — evaluate a json_logic expression against the blackboard

### Blackboard

BTree and BList processors maintain a **blackboard** — a key/value dict per entity. Commands can write to it (`set_bb_value`) and read from it using the `^key` pointer syntax:

```jsonc
["move_to_pos_target", {"target": "^last_seen_enemy"}]
```

---

## Test Scenes Guide

The test scenes under `example_game/resources/scenes/tests/` are numbered and progressive. Each demonstrates one or two engine features in isolation:

| Folder | Topics covered |
|---|---|
| `00_render/` | Basic rendering, models, animation |
| `01_movements/` | Movement commands, direction facing |
| `02_collisions/` | Entity-entity and entity-map collision |
| `03_camera/` | Camera follow, scroll, delayed scroll |
| `04_projectiles/` | Weapon arming, projectile factories, ammo |
| `05_damage/` | Damage system, health, destruction |
| `06_sound/` | Sound FX on events, music playback |
| `07_teleport/` | Teleport component and trigger zones |
| `08_score/` | Score generation on pickup/damage/kill |
| `09_pickup/` | Pickup system, inventory basics |
| `10_sensors/` | Sight cone, earshot, sensor-driven AI |
| `11_sensors/` | Advanced sensor use with delayed camera |
| `12_ai/` | Behavior trees, Brain, parallel commands |

The complete games under `resources/scenes/games/` show full integration:

| Game | Description |
|---|---|
| `sokoban/` | Puzzle — push boxes onto target tiles; uses wall entities for physics |
| `collect_coins/` | Action — collect coins before time runs out |
| `kill_all/` | Action — defeat all enemies using AI-controlled NPCs |

---

## Running Tests

```bash
# Python unit tests
pytest tests/

# Doctest on individual component modules
python -m example_game.core.components.brain -v
```

---

## For ClaudeCode

Tasks specifically targeting Claude Code assistance:

- [x] Improve performance of MAP rendering — redo with caching
- [x] Review `GenerateCollisionsOptimizedProcessor` for performance
- [ ] Review `PerformFrameUpdateProcessor` for performance
- [ ] Review `PerformIdleAnimationProcessor` for performance
- [ ] Prepare pytest tests for pgrpg functions/classes
- [ ] Prepare complex Behavior Tree logic for NPC — described as text, output as JSON
- [ ] Prepare a series of JSON scene files using human-language descriptions
- [ ] Porting to browser/mobile
- [ ] Prepare `kill_all` scenario scene with 4 enemies using existing commands
- [ ] Fix playback speed to be computer-speed independent
- [ ] Discuss architecture change to client/server model (multiplayer)
- [ ] Suggest solution for game string translation

---

## Roadmap & Known Issues

### Open bugs

- [ ] `Position` component `x`/`y` can be float — fix to int only
- [ ] `move_to` command — NPCs walk through tiles (pathfinding ignores map collisions)
- [ ] `move_to_pos_target_vect` — entity facing direction not updated during movement
- [ ] Pushing entities into walls still possible despite map collision being enabled
- [ ] Debug processor only works with one camera
- [ ] Debug info hover raises render error
- [ ] When restarting `collect_coins`, loading screen shows in background
- [ ] Some problem in `tests/12_ai/simple/do_parallel.jsonc` when enemy approaches
- [ ] `event_manager._event_queue` can grow unbounded during heavy collision frames — needs max capacity or event TTL

### Open features

**Engine / Architecture**
- [ ] Move Flag-removal processors before Flag-generator processors in the default ordering
- [ ] Implement post-requisite checks for processors (after all loaded, verify dependencies)
- [ ] Named processor group: `ALL` cleanup option
- [ ] Consider client/server architecture for multiplayer
- [ ] Refactor scripts to import `ecs_manager` directly instead of `main`
- [ ] `gui.py` refactor — GUIContext to represent window/manager/etc.
- [ ] Console height dynamically calculated from config
- [ ] Settings screen with Apply button (UIWindow checkbox exception needs fix)
- [ ] Universal asset loader (full path / partial / no suffix for models, sounds, VFX)
- [ ] Console commands support UNIX-like patterns
- [ ] Console `//` comment support in `.scr` scripts
- [ ] `translations` — JSON key:value file switchable by config: `trans("Some_text")`
- [ ] Font config automation — currently named one by one
- [ ] State screens with layout based on resolution config
- [ ] `for state screens prepare layout based on resolution config`

**Gameplay systems**
- [ ] Throw items out of inventory (with `HasInventory.remove()` in dict_utils)
- [ ] Show item information in inventory footer
- [ ] How to prevent a just-dropped item from being immediately re-picked
- [ ] `implement wear processors`
- [ ] Messages should display on camera, not window
- [ ] Enter/Esc to confirm/dismiss exit dialog
- [ ] Weapon/ammo drop when armed — fix `RenderDataFromParent` cleanup on `WeaponInUse` removal
- [ ] Shaders (reference: DaFluffyPotato)
- [ ] Inventory weaponry slots (separate from general inventory)
- [ ] `redo rendering of the tileset` — incremental rendering using previous frame data
- [ ] Extend sound FX — `SoundFXOnGeneration` for projectiles; multi-FX per entity
- [ ] Visual FX — `VisualFXOnGeneration`, `VisualFXOnCreation`
- [ ] AStar pathfinding option alongside BFS; DFS option
- [ ] BFS pathfinding preference for axis-aligned movement (reduce diagonal bias)
- [ ] `do_parallel` — support skipping cycles (timed sub-commands)
- [ ] New commands: `test_bb_value_in`, `test_bb_value_not_in` (faster json_logic alternatives)
- [ ] Blackboard implicit `self` key (entity ID/name available to all handlers)
- [ ] New command: `do_if_bb_test_true`
- [ ] BTree/BList restart function (tree restarts on event)
- [ ] Test recording — verify that inventory commands are captured

**Developer experience**
- [ ] `tile_to_px` / `px_to_tile` utility stored universally
- [ ] `dict_utils` as standalone package
- [ ] `main.reinit()` — more universal, selective reinit
- [ ] Make state-change checks optional (warnings only, not hard errors)
- [ ] `every game/test should live outside pgrpg/` — clean separation
- [ ] Abstract manager interface (`clear()`, `register()`) for uniform iteration and progress bar
- [ ] Logging: add `%`-style formatting throughout (avoid f-string construction when log level is off)

### Completed (recent highlights)

- [x] `GameEventsExProcessor` optimized — `collections.deque` replaces list (O(1) popleft vs O(n) pop(0)); `ignore`/`process` filters converted to sets for O(1) membership tests
- [x] `--file` and `--state` CLI parameters for targeted scene/state startup
- [x] `PerformScrollDelayedCameraProcessor` — smooth delayed camera follow with `delay` param
- [x] Music playback via `play_music` script triggered by scene events
- [x] Wall entities replace map-collision tiles — fixes box-chain physics (used in sokoban)
- [x] UNIX wildcard cleanup patterns for processors, maps, templates, entities, dialogs, handlers
- [x] `arm_ammo` command + disarm ammo processors + full arming flow
- [x] `load_from_template` command — loads any template onto an existing entity
- [x] `toggle_controls` command — switches full key mapping (for inventory mode)
- [x] Inventory system — slots, drag, move with arrow keys, visual feedback
- [x] Processor groups — separate processor loops per game state (e.g. inventory)
- [x] JSON Schema (Draft-07) for all components, commands, and processors
- [x] Template variables (`$var`) in component params — validated by schema
- [x] Behavior tree command generators (BTree + BList)
- [x] Non-blocking BFS pathfinding with checkpoint support
- [x] Score system (pickup, damage, no-health events)
- [x] Teleport system with key-entity trigger
- [x] Drop system with free-area search algorithm
- [x] In-game F9 dev console with `proc_perf`, `get_components`, `get_processors`, `.scr` scripts
- [x] Progress bar on scene load (configurable per scene)
- [x] Custom esper fork with processor groups, throttling, extended queries
- [x] Two-pass entity loading (register aliases first, fill components second)
- [x] GitHub Actions: pytest, doctest, lint
