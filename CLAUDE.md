# CLAUDE.md — pgrpg AI Agent Entry Point

> Last updated: 2026-07-30
> This file is the onboarding entry point for AI agents. It is **not** the knowledge base.

## What This Repo Is

**pgrpg** is a Pygame-based 2D RPG engine built around an Entity–Component–System core. Its defining
property is that **the game is data, not code**: scenes, entities, components, AI, dialogs, event
handling and UI flow are declared in `.jsonc` / `.yaml` files, and Python supplies only the
Components, Processors, Commands and Scripts those files name.

The engine is an installable package (`pgrpg`). `example_game/` is the reference game that consumes
it and is **not** part of the distribution.

Design priority: **clarity and readability over performance.**

Some parts of the engine are half-built, superseded or provably broken. That is recorded as a neutral
fact — see [`.claude/kb/SCOPE.md`](.claude/kb/SCOPE.md) for each capability's status before assuming a
code path works.

## Start Here

The knowledge base lives in [`.claude/kb/`](.claude/kb/). Begin with
[`.claude/kb/README.md`](.claude/kb/README.md) — the wiki home with a quick-lookup table, a domain map
and links into every knowledge area.

| If your task is… | Read |
|---|---|
| Understand how the program starts or what one frame does | [`kb/core/bootstrap-and-loop.md`](.claude/kb/core/bootstrap-and-loop.md) |
| Understand how a `.jsonc` file becomes a live world | [`kb/core/scene-pipeline.md`](.claude/kb/core/scene-pipeline.md) |
| Write or change a Component | [`kb/ecs/components.md`](.claude/kb/ecs/components.md) |
| Write or change a Processor | [`kb/ecs/processors.md`](.claude/kb/ecs/processors.md) |
| Author a scene, entity, template or component params | [`kb/authoring/`](.claude/kb/authoring/index.md) |
| Author AI (`cmd_tree` / `cmd_list`) | [`kb/authoring/ai-definitions.md`](.claude/kb/authoring/ai-definitions.md) |
| Author event handlers / `json_logic` actions | [`kb/authoring/handlers-and-actions.md`](.claude/kb/authoring/handlers-and-actions.md) |
| Find a component / processor / command / event name | [`kb/reference/index.md`](.claude/kb/reference/index.md) |
| Work out whether something is actually implemented | [`kb/SCOPE.md`](.claude/kb/SCOPE.md) |

Maintenance rules for the knowledge base (where facts go, provenance labels, deduplication) are in
[`.claude/kb/RULES.md`](.claude/kb/RULES.md). **Read Rule 12 before finishing any task that changes
engine behaviour.**

## Repository Layout

```
pgrpg/                  the engine package (published via pyproject.toml)
  core/
    main.py             init() + run() — the game loop
    engine.py           scene loading pipeline + manager wiring
    scene.py            Scene metadata object
    ecs/__init__.py     modified esper 1.3 fork: World, Component, Processor
    config/             config load()/init(), defaults.jsonc, states, gui, sound, console
    managers/           8 module-level singletons (ecs, event, script, command,
                        map, dialog, message, pathfind)
    commands/           Command types + generators/{btree,blist}
    events/  maps/  models/  messages/  pathfinding/  sounds/
  functions/            pure utilities (json_logic, translate, get_dict_params, …)
  utils/                authoring/dev tools (not used at runtime)

example_game/           the reference game — NOT part of the package
  game.py               runnable entry point
  config.jsonc          game config, overrides pgrpg defaults
  core/
    components/         88 Component classes
    processors/         22 *_system/ packages
    commands/           38 command modules
    scripts/            event action scripts
    states/             9 state modules
    console/            dev console commands + .scr scripts
    schemas/            JSON Schemas for editor validation
  resources/
    scenes/             78 scene files — tests/00_render … 12_ai, games/, UI/
    entities/           ~2 500 reusable entity/template files
    btrees/  dialogs/  maps/  models/  images/  sounds/  music/  fonts/  frames/

tests/                  pytest suite — 186 tests
docs/                   current design docs (ADR_001, CHANGELOG_ARCHITECTURE) + docs/old/
experiments/            scratch prototypes — NOT imported anywhere; do not treat as reference
```

## Running and Testing

Always from the **repository root** — `FILEPATHS.GAME_PATH` is relative and
`pgrpg/core/config/defaults.jsonc` is a hardcoded relative path.

```bash
pip install -e .

python example_game/game.py                                # → dev console
python example_game/game.py -s MAIN_MENU                   # → main menu
python example_game/game.py -f games/sokoban/sokoban.jsonc  # → a scene (path relative to SCENE_PATH)

pytest tests/                                              # 186 tests, ~2 s
python -m core.components.position -v                      # doctests, run from example_game/
```

The in-game dev console (F9) is the main introspection tool: `get_entities`, `get_components`,
`get_processors`, `get_events`, `proc_perf`, `load_scene`.

## Hard Rules

1. **Never run `git commit` or `git push`.** The repository owner commits. Report the files you
   changed.
2. **Never hardcode a pixel size** for a sprite, tile, cull margin or UI slot. Read
   `GAME["TILE_RES_PX"]` or derive from it — the test suite asserts correct rendering at 32, 64 and
   96 px. See [`kb/_shared/resolution.md`](.claude/kb/_shared/resolution.md).
3. **Every Processor must catch `SkipProcessorExecution` itself.** `World._process` does not, so an
   escaping exception aborts every later processor in the group for that frame.
4. **Components use `__slots__`** — memory and the base `__str__` both depend on it.
5. **Managers are modules, not classes.** Do not instantiate them; call their functions.
6. **Update the knowledge base in the same change** as any source change that alters behaviour it
   describes ([`kb/RULES.md`](.claude/kb/RULES.md) Rule 12).
7. **Do not use `experiments/` as a reference.** `experiments/ecs/` is an older whole copy of the
   engine and is not imported by anything.

Fuller editing conventions — docstring style, naming, comment style, data-file conventions — are in
[`.claude/kb/_shared/conventions.md`](.claude/kb/_shared/conventions.md).
