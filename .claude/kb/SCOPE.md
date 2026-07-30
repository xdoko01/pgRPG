# pgrpg — Capability Status Register

> Last updated: 2026-07-30 | Verified by: Source-verified across `pgrpg/` and `example_game/`;
> Runtime-verified where marked (unbound `finalize()` → `TypeError`; explicit `.toml` load →
> `ValueError`; `pytest tests/` → 186 passed) @ `c7b9a5f1`

This is the **single canonical source** for whether a capability actually works. It exists because
several parts of this engine are half-built, superseded or provably broken, and an agent that assumes
otherwise will waste a session.

## Status taxonomy

- **WORKING** — used by shipped scenes or covered by tests; safe to rely on.
- **PARTIAL** — works within stated limits; read the note before using.
- **BROKEN** — provably does not work. Evidence given.
- **UNUSED** — implemented and plausibly working, but nothing exercises it; treat as untested.
- **SUPERSEDED** — replaced by something newer; kept for compatibility.

This is a neutral record, not a to-do list (RULES.md Rule 13). Do not fix code as a side effect of
documenting it.

---

## 1. Core engine

| Capability | Status | Note |
|---|---|---|
| Bootstrap, config merge, game loop | **WORKING** | [core/bootstrap-and-loop.md](core/bootstrap-and-loop.md) |
| State machine + state modules | **WORKING** | 9 state modules in `example_game` |
| Scene pipeline: `prereqs`, `processors`, `maps`, `dialogs`, `templates`, `entities`, `handlers` | **WORKING** | |
| `cleanup/{maps,templates,entities,dialogs,handlers}` | **WORKING** | fnmatch patterns; used by `sokoban_level02.jsonc` |
| **`cleanup/processors`** | **BROKEN** | `ecs_manager.delete_processor` expects `[group_id, "module:Class"]` (schema says plain string) **and** calls `finalize()` on the class, not an instance. Runtime-verified: unbound `finalize(self, ...)` with no args → `TypeError: missing 1 required positional argument: 'self'`. No shipped scene uses it. [detail](core/scene-pipeline.md#-cleanupprocessors-does-not-work) |
| `entities/components/params/handlers` (nested handlers) | **WORKING** | Only 2 shipped scenes use it: `tests/12_ai/*_using_events.jsonc` |
| Entity `remove` key | **UNUSED** | `_update_entity` supports it; no shipped scene uses it |
| `progress_bar` scene key | **BROKEN** | Present in `empty.jsonc`; grep finds no `progress_bar` / `SimpleProgressBar` in any code. Aspirational. |
| `ProgressBar` during load (`show_progress=True`) | **WORKING** | Thread-backed, used by `main._init_game` |
| `main.reinit()` for display changes | **PARTIAL** | Display/console/GUI only. Does not re-normalise loaded maps or models — see `TILE_RES_PX` below |
| Save / load game | **BROKEN** | `example_game/core/states/game.py` raises `NotImplementedError` on `K_SAVE_GAME` / `K_LOAD_GAME`. `pre_save` / `post_load` hooks exist and are correct; nothing calls them. `FILEPATHS.SAVE_PATH` is reserved. |
| Explicit `.toml` data file | **BROKEN** | `get_dict_from_file` uses `if` not `elif` for `.toml`, so it falls through to the guess branch and raises `ValueError`. Runtime-verified. **Omit the suffix.** [detail](_shared/filepaths-modulepaths.md#file-format-detection) |
| `.yml` extension | **BROKEN** | Not recognised; use `.yaml` |
| `.yaml` scenes | **WORKING** | `tests/04_collisions/test_collisions_05.yaml` |
| `LOGGING` default `in_game_console` handler | **BROKEN** in engine defaults | `defaults.jsonc` streams to `ext://pgrpg.core.managers.console_manager`, a module that no longer exists. `example_game/config.jsonc` overrides it to `pgrpg.core.config.console`, which is correct. A game that does not override it will fail `dictConfig`. |

## 2. ECS

| Capability | Status | Note |
|---|---|---|
| `World` entity/component storage and queries | **WORKING** | Test-verified `tests/core/ecs/` |
| `get_components_ex` / `_exs` / `_opt` | **WORKING** | |
| Processor groups | **WORKING** | Pause in `states/game.py`; `inventory` group in `empty.jsonc` |
| Execution throttling (`step`) | **WORKING** | Every processor must catch `SkipProcessorExecution` itself |
| Processor **priority** | **UNUSED** | `add_processor` supports it; the scene format exposes no way to set it, so every processor registers at 0 and list order decides |
| `Processor.PREREQ` | **UNUSED** | Mechanism works (`json_logic` + `check_proc_in_world`); every shipped `PREREQ` is empty or commented out |
| `Component.reinit()` | **PARTIAL** | Called for all components, but only `Camera` and `FlagShowInventory` implement it |
| `Processor.reinit()` | **WORKING** | Called for all processors on `main.reinit()` |
| `Processor.finalize()` | **PARTIAL** | Called on teardown; base raises `NotImplementedError`, downgraded to a warning by `clear_processors` |
| `pre_save` / `post_load` on components | **UNUSED** | Correct, but see Save/load above |
| `World(timed=True)` per-processor timing | **WORKING** | `pgrpg.TIMED` in config; `proc_perf` console command |
| `get_empty_entities()` | **WORKING** | Diagnostic. Should always return `[]`; non-empty means an entity leak |

## 3. Commands and AI

| Capability | Status | Note |
|---|---|---|
| Command queue, `init` + `process` phases, `CommandStatus` | **WORKING** | |
| `BrainAI` with `cmd_list` (BList) | **WORKING** | 46 files use `brain_ai:BrainAI` |
| `BrainAI` with `cmd_tree` (BTree) | **WORKING** | |
| BTree `Sequence`, `Selector`, `Inverter`, `Repeater`, `RepeatUntilFail`, `Behavior` | **WORKING** | |
| BTree **`Succeeder`** | **BROKEN** | Class body is `pass`. Neither it nor its `Decorator` base defines `process()`, so it inherits `TreeNode.process()`, which returns `None` — the parent's `action_node, cmd = child.process()` then fails to unpack. Referenced by no scene. |
| BList nested `Loop` | **BROKEN** | A single `loop_counter` on the generator, not one per line, so two `Loop` lines interfere. Use one loop per list. |
| BList `line` field | **UNUSED** | Documentation only — the engine uses list position |
| `^blackboard` substitution | **WORKING** | Resolved once, on the command's first tick |
| `resources/btrees/{guard_path,destroy_target}.json` | **BROKEN** | Use a `cmd_process` key where `Behavior` requires `command`, so tree construction fails. Referenced only by `entities/_special/{guard,hunter}.json`, which are themselves unreferenced. `example_game/game.py` marks `kill_all_level01.jsonc` "MUST BE REDONE BTREES". |
| `Brain` component (index-based, pre-`BrainAI`) | **SUPERSEDED** | Still present and referenced by `tests/02_commands/test_commands_0{1,2}.jsonc`, `kill_all_level01.jsonc` and `entities/thing/being/human.json`. New AI should use `BrainAI`. |
| `BTreeAI` / `BListAI` components | **SUPERSEDED** | Replaced by `BrainAI`, which selects the generator by key |
| `GenerateCommandFromBTreeProcessor` / `…FromBListProcessor` | **SUPERSEDED** | Replaced by `GenerateCommandFromBrainProcessor` |
| Command record / replay | **WORKING** | `record_command_to_file_processor` + `generate_command_from_file_processor`; `tests/02_commands/record_commands.jsonc` → `play_commands_*.jsonc` |
| Mouse-driven commands | **UNUSED** | `generate_command_from_mouse_processor` exists; no shipped scene uses it |
| `do_parallel` command | **PARTIAL** | Works; `game.py` marks `tests/12_ai/simple/do_parallel.jsonc` as "SOME PROBLEM" |
| Pathfinding (BFS, resumable) | **WORKING** | `PerformPathfindingCalculationProcessor` |

## 4. Gameplay subsystems (example game)

| Subsystem | Status | Demonstrated by |
|---|---|---|
| Render (map, model, camera, debug overlay) | **WORKING** | `tests/00_render/` |
| Movement | **WORKING** | `tests/01_movements/` |
| Animation | **WORKING** | `tests/03_animations/` |
| Collision (entity–entity) | **WORKING** | `tests/04_collisions/` |
| Collision (entity–map, `ResolveMapCollisionsProcessor`) | **PARTIAL** | Implemented; commented out in `sokoban.jsonc`. Only `tests/04_collisions/test_map_collision_01.jsonc` exercises it |
| Pickup / drop / inventory | **WORKING** | `tests/05_pickup&drop/` |
| Teleport | **WORKING** | `tests/06_teleportation/` |
| Arm weapon / arm ammo | **WORKING** | `tests/07_arm_weapon/`, `tests/08_arm_ammo/` |
| Projectiles via `Factory` | **WORKING** | `tests/09_projectiles/` |
| Damage / destroy / score | **WORKING** | `tests/09_projectiles/test_projectile_damage.jsonc` |
| Visual & sound effects | **WORKING** | `tests/10_effects/` |
| Sensors (`CanSee`, `CanHear`) | **WORKING** | `tests/11_sensors/` |
| AI scenarios | **PARTIAL** | `tests/12_ai/`. `game.py` marks `test_entity_seen.jsonc` "old, does not work"; `simple/test_damaged.jsonc`, `simple/test_bb_value.jsonc`, `simple/do_parallel.jsonc` "SOME PROBLEM" |
| GUI buttons (`gui_system`) | **PARTIAL** | Only `scenes/UI/test_button_pressed.jsonc` uses it — one scene, one button |
| Dialogs (`dialog_manager` + `show_dlg_window`) | **WORKING** | 11 scenes declare `dialogs`, all inheriting `resources/dialogs/basic.json` — e.g. `tests/04_collisions/test_collisions_0{3,4,5}`, `tests/05_pickup&drop/test_pickup_01`, `tests/06_teleportation/*`, `tests/11_sensors/test_sensors_01`. The newer games (`sokoban`, `collect_coins`) use the `show_msg_window` / `show_confirm_dlg` pygame_gui scripts instead |
| Complete games | **WORKING** | `games/sokoban/` (2 levels), `games/collect_coins/`, `games/kill_all/` (the last needs its btrees redone) |

## 5. Authoring and tooling

| Capability | Status | Note |
|---|---|---|
| `$schema` editor validation | **PARTIAL** | Works for `scene`, `entity`, `template`, `component`. `processors`, `maps`, `dialogs`, `handlers` are declared as untyped arrays, so `processor.schema.json` and `command.schema.json` are never reached from the scene schema |
| `definitions.schema.json#/basics/class_def` | **BROKEN** | Regex uses `\(`/`\)` as literal parens, requiring a leading `(`. Runtime-verified to match nothing. `$ref`d by nothing, so harmless |
| `definitions.schema.json#/basics/template_str_def` / `template_list_def` | **BROKEN** | Same regex mistake, and these **are** `$ref`d from `template.schema.json`. Also uses Draft 2020-12 `prefixItems` in a Draft-07 document |
| **`"template"` (singular) in an entity definition** | **BROKEN** | `_update_entity` reads `"templates"`. Seven shipped files get this wrong: `resources/entities/controls/*.json` (all 7). Harmless there only because the parent `controls.json` adds an empty `Controllable` the child overwrites anyway |
| `"template"` (singular) in a **btree node** | **WORKING** | Correct key for `create_tree` — the two are genuinely different |
| Dev console | **WORKING** | 13 commands + `.scr` scripts |
| `pgrpg/utils/` generators | **WORKING** | `entity_json_generator`, `generate_model_json_from_template`, `generate_tiled_json_from_template` — authoring-time only |
| Multi-cell model footprint | **BROKEN by design** | One grid cell per model; anything larger is squashed |
| `TILE_RES_PX` change at runtime | **BROKEN** | Grid maths follows, images do not. `RenderableModel` has no `reinit()`; maps are outside the reinit sweep. Set it in config and restart. [detail](_shared/resolution.md#set-it-at-start-up-only) |
| `docs/old/`, `experiments/` | **SUPERSEDED** | `experiments/ecs/` is an older whole copy of the engine. Not imported anywhere; excluded from the package |
| `schemas/components/_old/` | **SUPERSEDED** | Not referenced by `component.schema.json` |
| `MESSAGES.ON_EVENT` templates for `KILL`, `WEARABLE_WEARED`, `PHASE_START` | **BROKEN** | No processor emits those types. The destroy system emits `KILLED`, not `KILL` |

## 6. Tests

| Capability | Status | Note |
|---|---|---|
| `pytest tests/` | **WORKING** | Runtime-verified: 186 passed in 2.26 s |
| Resolution-independence tests | **WORKING** | `tests/core/maps/test_map.py`, `tests/core/models/test_model.py` assert 32 / 64 / 96 px |
| Doctests | **WORKING** | CI runs `python -m doctest -v` over every `.py`, so a broken doctest fails the build |
| `flake8 --select=E9,F63,F7,F82` | **WORKING** | Hard CI gate |
| Test coverage of processors | **UNUSED** | 21 test files cover `functions/`, `ecs/`, `managers/` (command, event, message, pathfind), `maps/`, `models/`, `commands/generators/` (btree, blist), `config/`, plus `example_game`'s `Collidable`, map-collision scaling and `core.processors.functions.filter_only_visible_on_camera`. **No `Processor` class itself has a unit test**, and `ecs_manager`, `script_manager`, `map_manager` and `dialog_manager` have none either. |

---

## Maintaining this register

When you confirm or refute an entry, update it per [RULES.md](RULES.md) Rules 3 and 10 — including the
provenance label and, on a correction, the
`> Corrected YYYY-MM-DD: previously stated <old value>` note. When you add a new capability to the
engine, add a row here in the same change.
