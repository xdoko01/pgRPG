# Scene Loading Pipeline

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/engine.py`,
> `pgrpg/core/scene.py`, `pgrpg/core/managers/ecs_manager.py`,
> `pgrpg/functions/dict_utils.py` (`get_coll_value`, `get_coll_len`) @ `c7b9a5f1`;
> cross-checked against `example_game/resources/scenes/games/sokoban/*`

Loading a scene turns a `.jsonc`/`.yaml` document into a live world. The whole mechanism is one
data-driven loop in `engine.load_scene_from_def()`.

## Entry points

| Function | Behaviour |
|----------|-----------|
| `engine.load_scene(scene_file, clear_before_load=True, show_progress=True)` | The normal entry. Optionally `_clear_game()`s everything, loads the file, registers the resulting `Scene` in `engine._scenes`, and enqueues a **`SCENE_START`** event carrying the scene metadata. |
| `engine.load_scene_from_file(scene_file, show_progress=False)` | Reads the file (relative to `FILEPATHS["SCENE_PATH"]`), runs the pipeline, stamps `scene.filepath`. **No clearing, no `SCENE_START`.** This is what the `prereqs` step calls recursively. |
| `engine.load_scene_from_def(scene_def, show_progress=False)` | Runs the pipeline over an already-parsed dict. |

The game-side script `load_quest` (`example_game/core/scripts/load_quest.py`) calls
`load_scene(scene_file, clear_before_load=False, show_progress=False)` — that is how one level
loads the next **additively**, on top of what is already loaded.

## The pipeline

`engine.load_scene_def_fncs` (`pgrpg/core/engine.py:171`) is an ordered list of
`[data_path, handler_function]` pairs. For each pair the loader extracts every value found at
`data_path` inside the scene dict and calls `handler(item)` once per value.

```python
for data_path, process_fnc in load_scene_def_fncs:
    data_to_process     = get_coll_value(coll=scene_def, path=data_path, sep="/")   # generator
    data_to_process_len = get_coll_len(coll=scene_def,   path=data_path, sep="/")
    with ProgressBar(...) if show_progress else nullcontext(lambda x: x) as progress:
        for item in progress(data_to_process):
            process_fnc(item)
```

The 15 steps, in execution order:

| # | `data_path` | Handler | Effect |
|---|-------------|---------|--------|
| 1 | `prereqs` | `engine.load_scene_from_file` | Recursively load dependency scene files first. |
| 2 | `cleanup/processors` | `ecs_manager.delete_processor` | Remove processors. ⚠️ **broken** — see below. |
| 3 | `cleanup/maps` | `map_manager.delete_maps_pattern` | Remove maps by fnmatch pattern. |
| 4 | `cleanup/templates` | `ecs_manager.delete_templates_pattern` | Remove templates by pattern. |
| 5 | `cleanup/entities` | `ecs_manager.delete_entities_pattern` | Remove entities by alias pattern. |
| 6 | `cleanup/dialogs` | `dialog_manager.delete_dialogs_pattern` | Remove dialogs by pattern. |
| 7 | `cleanup/handlers` | `event_manager.delete_handlers_pattern` | Remove event handlers by id pattern. |
| 8 | `processors` | `ecs_manager.load_processor` | Instantiate and register Processors. |
| 9 | `maps` | `map_manager.load_map` | Load `.tmx` maps. |
| 10 | `dialogs` | `dialog_manager.load_dialog` | Build dialog surfaces from definitions. |
| 11 | `templates` | `ecs_manager.load_template` | Store template definitions (no entity created). |
| 12 | `entities` | `ecs_manager.load_register_empty_entity` | **Pass 1** — create empty entities, register aliases. |
| 13 | `entities` | `ecs_manager.load_update_empty_entity` | **Pass 2** — apply templates and components. |
| 14 | `entities/components/params/handlers` | `event_manager.load_handler` | Register handlers found nested inside component params. |
| 15 | `handlers` | `event_manager.load_handler` | Register top-level scene handlers. |

Adding a new top-level scene key means adding a pair to this list. Nothing else needs to change.

### `get_coll_value` — why paths can be deep

`get_coll_value(coll, path, sep)` (`pgrpg/functions/dict_utils.py:491`) walks the path key by key
and **fans out over every list, tuple and set it meets**. So `entities/components/params/handlers`
means "for every entity, for every component, look inside `params` for a `handlers` list, and yield
each element of it". A missing key at any level yields nothing rather than raising. This is what
makes step 14 possible without any special-casing.

The same function backs `get_coll_len`, used only to size the progress bar.

## `prereqs` — scene composition

`prereqs` is a list of scene file paths (relative to `SCENE_PATH`, extension optional) loaded
**before** anything else in this scene. Because prereq loading uses `load_scene_from_file`, it does
not clear and does not fire `SCENE_START`.

The idiom in the example game is a **base scene + level scenes**:

```
games/sokoban/sokoban.jsonc          all processors, the t_tile_pos template, the SCENE_START handler
games/sokoban/sokoban_level01.jsonc  "prereqs": ["games/sokoban/sokoban"] + this level's map/entities
games/sokoban/sokoban_level02.jsonc  same prereq, plus cleanup of level 1's entities
```

`sokoban.jsonc`'s `SCENE_START` handler then does `["SCRIPT", "load_quest", {"scene_file":
"games/sokoban/sokoban_level01"}]` — so booting `sokoban.jsonc` chains into level 1. Level 1's own
`SCENE_START` handler shows the intro message. Because prereq loading and additive `load_quest`
both re-enter the pipeline, the graph must be acyclic; nothing checks for cycles.

## `cleanup` — un-loading before loading

Every cleanup list except `processors` takes **fnmatch-style UNIX wildcard patterns** matched with
`fnmatchcase` (case-sensitive). From `sokoban_level02.jsonc`:

```jsonc
"cleanup" : {
    "maps":      ["game_sokoban_lvl01"],
    "templates": ["t_crate"],
    "entities":  ["wall*", "crate*"],
    "handlers":  ["*"]
}
```

That is how level 2 discards level 1 while keeping the shared base scene's processors alive.

Pattern deletion always iterates a `.copy()` of the registry so deletion during iteration is safe.

### ⚠️ `cleanup/processors` does not work

`ecs_manager.delete_processor` (`ecs_manager.py:199`) expects a **two-element list**
`[proc_group_id, "module:ClassName"]`, not a string — contradicting `scene.schema.json`, which
declares `cleanup.processors` as an array of strings. Worse, it then calls
`proc_class.finalize()` on the **class**, not an instance:

```python
proc_class = get_proc_class_from_def(proc_class_def)
proc_class.finalize()                      # unbound → TypeError: missing 'self'
_world.remove_processor(proc_class, proc_group_id)
```

Verified: calling an unbound `finalize(self, *args, **kwargs)` with no arguments raises
`TypeError: finalize() missing 1 required positional argument: 'self'`.

No scene in `example_game` puts anything in `cleanup/processors`, which is why this has gone
unnoticed. To reload processors today, either restart the scene with `clear_before_load=True` or
place the processors in a base scene that is never cleaned. Tracked in [../SCOPE.md](../SCOPE.md).

## Two-pass entity loading

`entities` appears **twice** in the pipeline, and the order is the whole point.

**Pass 1 — `load_register_empty_entity(entity_def)`** calls `_create_empty_entity(entity_def["id"])`:
creates an entity with zero components and records `alias → id` and `id → alias` in the ECS
manager's two lookup dicts. If the alias already exists, the existing id is returned and no new
entity is made — this is what lets an additively-loaded scene *extend* an entity that is already in
the world.

**Pass 2 — `load_update_empty_entity(entity_def)`** looks the alias up again and calls
`_update_entity`, which:

1. Applies each id in `templates`, in order — **later templates overwrite earlier ones**.
2. Adds/overwrites each component in `components`.
3. Removes each component listed in `remove` (a key the loader supports but no shipped scene uses).

Then — unless called with `add_to_templates=False` — it registers the entity definition itself as a
template under its own id.

**Why two passes:** component params are alias-translated at construction time
(`create_component_from_def` → `translate(_alias_to_entity, comp_params)`). A component that
references `"player01"` can only resolve it if `player01` is already in the lookup table. Splitting
registration from filling means **every entity in the scene can reference every other, in any
order**. See [../_shared/aliases.md](../_shared/aliases.md).

## Runtime entity creation

`ecs_manager.create_entity(entity_def, entity_alias=None)` does registration and filling in one
call — used for projectiles and other entities spawned mid-frame (`Factory` component +
`PerformFactoryGenerationProcessor`). It is exposed to processors as `create_entity_fnc`. Because
it is single-pass, a runtime-created entity's params can only reference aliases that already exist.

## The `Scene` object

`Scene` (`pgrpg/core/scene.py`) is inert metadata, not a container of game objects:

| Attribute | Source |
|-----------|--------|
| `id`, `alias` | both set to `scene_def["id"]` |
| `title`, `description`, `objective` | corresponding scene keys |
| `filepath` | stamped after loading, by `load_scene_from_file` |
| `stats` | counts: `no_of_prereqs`, `no_of_procs`, `no_of_maps`, `no_of_dlgs`, `no_of_temps`, `no_of_ents`, `no_of_handlers`, and `no_of_comps` as a per-entity dict |

All of it is passed as `Event.params` on the `SCENE_START` event, which is why a handler can write
`%title` or `%stats` in a message — see
[../authoring/handlers-and-actions.md §%-substitution](../authoring/handlers-and-actions.md#event-param-substitution-with-).

Scenes are registered in `engine._scenes` keyed by alias. `delete_scene`, `clear_scenes` and
`exit_game` manage that registry. Note `_scenes` holds only metadata — deleting a scene from it does
**not** remove its entities or processors.

## Progress bar

When `show_progress=True`, each pipeline step is wrapped in
`pgrpg.core.config.gui.ProgressBar(header="Loading", text=data_path, total=...)`, a context manager
whose `__enter__` spawns a rendering `Thread` and returns a generator-wrapping `update` function.
With `show_progress=False` the loop uses `nullcontext(lambda x: x)` instead — same code path, no UI.

> ⚠️ The `progress_bar` key seen in `empty.jsonc`
> (`["gui:SimpleProgressBar", {"background": ..., "bar": true}]`) is **not read by any code**.
> Grepping the repository finds no reference to `progress_bar` or `SimpleProgressBar` outside that
> one scene file. It is aspirational. See [../SCOPE.md](../SCOPE.md).

## Related

- [../authoring/scene-format.md](../authoring/scene-format.md) — what to write in each key.
- [../authoring/entity-and-template.md](../authoring/entity-and-template.md) — entity/template syntax.
- [managers.md](managers.md) — the handler functions the pipeline calls.
- [../_shared/aliases.md](../_shared/aliases.md) — the alias lifecycle the two passes exist for.
