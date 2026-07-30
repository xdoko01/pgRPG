# pgrpg Knowledge Base

> Last updated: 2026-07-30 | Verified by: initial authoring from full source analysis at commit
> `c7b9a5f1` (engine package `pgrpg/`, reference game `example_game/`, tests `tests/`)

**pgrpg** is a Pygame-based 2D RPG engine built on an Entity–Component–System core. Its defining
property is that **the game is data, not code**: scenes, entities, components, AI, dialogs, event
handling and UI flow are declared in `.jsonc` / `.yaml` files, and the Python side supplies only
the Components, Processors, Commands and Scripts those files name.

The engine is an installable package (`pgrpg`). `example_game/` is the reference game that consumes
it and is **not** part of the distribution (`pyproject.toml` excludes it).

This knowledge base answers "how does X work", "where does Y live", and "what does this key in a
scene file actually do".

> Design priority stated by the project: **clarity and readability over performance.**

> ⚠️ Parts of this engine are half-built or provably broken. Check [SCOPE.md](SCOPE.md) for a
> capability's status before assuming a code path works.

---

## Quick Lookup

| Fact | Where it lives |
|------|----------------|
| Boot sequence: `pgrpg.init()` → config → managers → scene → main loop | [core/bootstrap-and-loop.md §Boot](core/bootstrap-and-loop.md#boot-sequence) |
| Per-frame data flow (events → state module → processors → commands → events → flip) | [core/bootstrap-and-loop.md §Frame](core/bootstrap-and-loop.md#the-frame) |
| **Scene loading order** — the 15-step `load_scene_def_fncs` pipeline | [core/scene-pipeline.md](core/scene-pipeline.md#the-pipeline) |
| Why entities are loaded **twice** (register, then fill) | [core/scene-pipeline.md §Two-pass](core/scene-pipeline.md#two-pass-entity-loading) · [_shared/aliases.md](_shared/aliases.md) |
| How a Processor receives engine functions (`FNC_ADD_EVENT`, `REF_ECS_MNG`, …) | [core/managers.md §game_functions](core/managers.md#the-game_functions-wiring-table) |
| Config merge: `defaults.jsonc` + game `config.jsonc`, and the prep/init split | [core/configuration.md](core/configuration.md) |
| Event queue, handler registry, and how one event fans out to many handlers | [core/events-and-scripts.md](core/events-and-scripts.md) |
| `json_logic` operators (`SEQ`, `IF`, `SCRIPT`, `VAR`, `LIST`, `IN`, `AND`, …) | [authoring/handlers-and-actions.md §Operators](authoring/handlers-and-actions.md#json_logic-operators) |
| Command queue, `init` + `process` phases, `CommandStatus`, blackboards | [core/commands-and-ai.md](core/commands-and-ai.md) |
| Behaviour-tree node types and their SUCCESS/FAILURE semantics | [core/commands-and-ai.md §BTree](core/commands-and-ai.md#btree--behaviour-tree-generator) |
| Behaviour-list `Goto` / `Loop` / `on_fail_jmp` semantics | [core/commands-and-ai.md §BList](core/commands-and-ai.md#blist--behaviour-list-generator) |
| `World` query methods incl. `get_components_ex` / `_exs` / `_opt` | [ecs/world.md §Queries](ecs/world.md#queries) |
| Why `World` queries are `lru_cache`d and when the cache is cleared | [ecs/world.md §Caching](ecs/world.md#query-caching) |
| Deferred vs immediate entity deletion | [ecs/world.md §Entity lifecycle](ecs/world.md#entity-lifecycle) |
| **This fork's deviations from upstream esper 1.3** | [ecs/world.md §Fork deltas](ecs/world.md#deviations-from-upstream-esper-13) |
| Writing a Component — `__slots__`, `reinit`, `pre_save` / `post_load` | [ecs/components.md](ecs/components.md) |
| Writing a Processor — `SkipProcessorExecution` must be caught by every processor | [ecs/processors.md §Throttling](ecs/processors.md#execution-throttling) |
| Processor groups and priority (higher number = earlier) | [ecs/processors.md §Groups](ecs/processors.md#groups-and-priority) |
| Processor `PREREQ` declarations | [ecs/processors.md §PREREQ](ecs/processors.md#prereq-dependency-declarations) |
| **Scene file key reference** | [authoring/scene-format.md](authoring/scene-format.md) |
| Entity / template syntax, `vars`, `t_name(5, 5, map)` calls | [authoring/entity-and-template.md](authoring/entity-and-template.md) |
| Any entity can be used as a template for another entity | [authoring/entity-and-template.md §Entities as templates](authoring/entity-and-template.md#every-entity-becomes-a-template) |
| `"type": "module:ClassName"` component reference form | [authoring/component-params.md §Type](authoring/component-params.md#the-type-field) |
| **`x_tiles` vs `x`** — tile-relative params and why to prefer them | [_shared/resolution.md §Tile-relative params](_shared/resolution.md#tile-relative-params) |
| `TILE_RES_PX` — one resolution, applied at asset load time | [_shared/resolution.md](_shared/resolution.md) |
| `TILE_RES_PX` cannot be changed at runtime (half-applied state) | [_shared/resolution.md §Start-up only](_shared/resolution.md#set-it-at-start-up-only) |
| `^key` (blackboard) vs `$var` (template) vs `%param` (event) prefixes | [authoring/index.md §Three prefixes](authoring/index.md#the-three-substitution-prefixes) |
| Where the engine looks for scenes / entities / models / maps / scripts | [_shared/filepaths-modulepaths.md](_shared/filepaths-modulepaths.md) |
| C-style `//` comments in JSON — and the regex that strips them | [_shared/filepaths-modulepaths.md §JSONC](_shared/filepaths-modulepaths.md#jsonc-comment-stripping--and-its-limits) |
| Full inventory: components, processors, commands, events, scripts, states | [reference/index.md](reference/index.md) |
| Event types the engine emits and scenes handle | [reference/index.md §Events](reference/index.md#event-types) |
| Editing conventions (docstring style, doctests, no new files) | [_shared/conventions.md](_shared/conventions.md) |
| **What is broken / unused** (`cleanup/processors`, `progress_bar`, `Brain`, …) | [SCOPE.md](SCOPE.md) |

---

## Domain Map

| Domain | Scope | Index |
|--------|-------|-------|
| **Core** | Bootstrap, game loop, configuration, scene pipeline, managers, events, commands & AI | [core/index.md](core/index.md) |
| **ECS** | The esper fork: `World`, `Component`, `Processor`, queries, lifecycle | [ecs/index.md](ecs/index.md) |
| **Authoring** | The data language: scene / entity / template / component / AI / handler syntax | [authoring/index.md](authoring/index.md) |
| **Reference** | Flat inventories of everything the example game defines | [reference/index.md](reference/index.md) |

Shared / cross-domain facts:
[_shared/resolution.md](_shared/resolution.md) ·
[_shared/aliases.md](_shared/aliases.md) ·
[_shared/filepaths-modulepaths.md](_shared/filepaths-modulepaths.md) ·
[_shared/conventions.md](_shared/conventions.md)

Capability status register: [SCOPE.md](SCOPE.md)

---

## Reading Order for a New Agent

1. [core/bootstrap-and-loop.md](core/bootstrap-and-loop.md) — how the program starts and what one
   frame does. Everything else hangs off this.
2. [core/scene-pipeline.md](core/scene-pipeline.md) — how a `.jsonc` file becomes a live world.
3. [ecs/index.md](ecs/index.md) — the data model the whole engine iterates over.
4. [authoring/index.md](authoring/index.md) — the syntax you will actually be asked to write.

If the task is "add a feature to the game", you almost certainly write a Component + a Processor +
a scene entry, not engine code. Start at [authoring/index.md](authoring/index.md) and
[ecs/components.md](ecs/components.md).

---

## Maintaining This Knowledge Base

Any new verified fact discovered while working here must be added to the right knowledge file
before the session ends. Rules for where facts go, provenance labels, deduplication and file
length are in [RULES.md](RULES.md).

The repository owner commits — **never run `git commit` or `git push`**. Report which KB files you
changed alongside the source files (RULES.md Rule 12).
