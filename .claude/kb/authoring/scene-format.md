# Scene File Format

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/engine.py`,
> `pgrpg/core/scene.py`, `example_game/core/schemas/scene.schema.json`; cross-checked against
> `example_game/resources/scenes/{empty.jsonc, games/sokoban/*, tests/12_ai/*}` @ `c7b9a5f1`

A scene file is a single JSON object. Its top-level keys correspond one-to-one with the steps of the
loading pipeline — see [../core/scene-pipeline.md](../core/scene-pipeline.md).

## Skeleton

```jsonc
{
    "$schema": "../../core/schemas/scene.schema.json",   // editor validation only

    "id"          : "my_scene",       // required — registry key and alias
    "title"       : "My Scene",       // required
    "description" : "...",            // required
    "objective"   : "...",            // required

    "prereqs" : [],                   // scene files loaded first

    "cleanup" : {                     // fnmatch patterns, removed before loading
        "processors": [], "maps": [], "templates": [],
        "entities": [], "dialogs": [], "handlers": []
    },

    "processors" : [],                // the frame schedule
    "maps"       : [],                // .tmx names
    "dialogs"    : [],                // dialog definitions
    "templates"  : [],                // reusable entity fragments
    "entities"   : [],                // the world
    "handlers"   : []                 // event → actions
}
```

Every key except the four metadata fields is optional; a missing key yields nothing at its pipeline
step. `empty.jsonc` is the canonical starting point.

## `id`, `title`, `description`, `objective`

Required by `scene.schema.json`; `id` must be at least 3 characters. `id` becomes both `Scene.id` and
`Scene.alias`, and is the key in `engine._scenes`. All four are delivered to handlers as
`SCENE_START` event params, so a handler can render `%id`, `%title`, `%description`, `%objective` —
plus `%filepath` and `%stats`, which the scene file does not declare.

`load_scene` overwrites an existing entry in `_scenes` with the same id without complaint.

## `prereqs`

```jsonc
"prereqs": ["games/sokoban/sokoban"]
```

A list of scene file paths relative to `FILEPATHS["SCENE_PATH"]`, extension optional. Each is loaded
via `load_scene_from_file` — **no clearing, no `SCENE_START` event**. Loaded before every other step
of this scene, and recursively (a prereq's prereqs load first). Nothing detects cycles.

The base-scene / level-scene idiom that this enables is described in
[../core/scene-pipeline.md §prereqs](../core/scene-pipeline.md#prereqs--scene-composition).

## `cleanup`

Six lists of **fnmatch UNIX wildcard patterns**, matched case-sensitively with `fnmatchcase`:

```jsonc
"cleanup": {
    "maps":      ["game_sokoban_lvl01"],
    "templates": ["t_crate"],
    "entities":  ["wall*", "crate*"],
    "handlers":  ["*"]
}
```

| List | Matches against |
|------|-----------------|
| `maps` | map name |
| `templates` | template id |
| `entities` | entity alias |
| `dialogs` | dialog id |
| `handlers` | handler id (across all event types) |
| `processors` | ⚠️ **broken** — see below |

Cleanup runs **after** `prereqs`, so a level scene can load its shared base and then remove the
previous level's entities in the same file.

> ⚠️ `cleanup.processors` does not work. `ecs_manager.delete_processor` expects
> `[group_id, "module:Class"]` (not the string the schema declares) **and** calls `finalize()` on the
> class rather than an instance, which raises `TypeError`. No shipped scene uses it. Details and
> workarounds in [../core/scene-pipeline.md](../core/scene-pipeline.md#-cleanupprocessors-does-not-work).

## `processors`

**The most consequential key in the file.** It is the frame schedule: list order is execution order
(all registrations use priority 0 and Python's sort is stable).

Two forms:

```jsonc
"processors": [
    // 2 elements → the 'default' processor group
    ["render_system.perform_render_map_processor:PerformRenderMapProcessor", {}],

    // 3 elements → named group first
    ["inventory", "render_system.perform_blit_picture_processor:PerformBlitPictureProcessor",
     {"filepath": "red_gradient_capital_font.png", "resize": true}]
]
```

- The class reference is `"<module path under PROCESSOR_MODULE_PATH>:<ClassName>"`. Dots navigate
  packages: `collision_system.remove_flag_has_collided_processor:RemoveFlagHasCollidedProcessor`.
  A processor re-exported from a package `__init__.py` can be referenced with just the package:
  `collision_system:GenerateCollisionsProcessor`.
- ⚠️ Those `__init__.py` re-exports also **rename**. `collision_system:GenerateCollisionsProcessor`
  is really `GenerateCollisionsOptimizedProcessor`; `damage_system:GenerateDamageProcessor` is really
  `GenerateDamageSingleProcessor`. The scene name is an alias chosen by the package, so grepping the
  scene name will not find the class — check the system's `__init__.py` first.
- The params dict is merged **over** the auto-injected `game_functions` entries, so it can also
  override an injected callable.
- `{"step": N}` throttles the processor to every Nth frame
  ([../ecs/processors.md §Throttling](../ecs/processors.md#execution-throttling)).
- Groups are selected by the state module, which is how pause and overlays work
  ([../ecs/processors.md §Groups](../ecs/processors.md#groups-and-priority)).

A missing or misspelled class raises during load:
`AssertionError: Unable to create class from definition class_def=...`.

There is no default processor set. A scene with an empty `processors` list loads its world and renders
nothing. Copy the block from the nearest `resources/scenes/tests/NN_*/` scene.

## `maps`

```jsonc
"maps": ["test_arena_sand", "game_sokoban_lvl01"]
```

Plain strings — the `.tmx` basename under `FILEPATHS["MAP_PATH"]`, without extension.
`map_manager.load_map` is a no-op if the map is already loaded, so repeating a map across a prereq
chain is free.

Loading a map is expensive and eager: `Map.__init__` rescales every tile image to `TILE_RES_PX`,
builds the pathfinding graph over every tile, finds the animated tiles, and pre-renders one
full-map `Surface` per visible layer. Memory is
`layers × map_width_px × map_height_px × 4 bytes`.

Entities reference a map **by this name** in their `Position` component's `map` param.

## `dialogs`

```jsonc
"dialogs": [{"id": "my_dialog", "templates": ["basic"], ...}]
```

Dicts with a mandatory `id` and an optional `templates` list of `.json` filenames (no extension)
under `FILEPATHS["DIALOG_PATH"]`. Templates are resolved recursively and merged shallowly — deeper
first, then shallower, then the scene-level dict last. `pgrpg.utils.dialog.prepare_dlg_obj_from_data`
then builds the pygame surfaces.

Shipped dialog templates: `resources/dialogs/{basic,empty}.json`, documented in
`resources/dialogs/_DialogJSONStructure.md` and `_DialogHierarchy.txt`.

## `templates`

A list of entity-fragment definitions stored for later reference by id. Defining a template does
**not** create an entity.

```jsonc
"templates": [
    {
        "id": "t_tile_pos",
        "vars": ["$tileX", "$tileY", "$map"],
        "components": [
            {"type": "position:Position",
             "params": {"tile_x": "$tileX", "tile_y": "$tileY", "map": "$map"}}
        ]
    }
]
```

Templates may also be stored as files under `FILEPATHS["ENTITY_PATH"]` and referenced by path.
Full syntax: [entity-and-template.md](entity-and-template.md).

## `entities`

```jsonc
"entities": [
    {
        "id": "player01",
        "templates": ["model/body/male/human/white",
                      "t_tile_pos(3, 3, game_sokoban_lvl01)",
                      "controls/default"],
        "components": [
            {"type": "movable:Movable", "params": {"velocity": 80}},
            {"type": "camera:Camera",   "params": {"always_center": true, "screen_fill": true}}
        ]
    }
]
```

| Key | Meaning |
|-----|---------|
| `id` | **Required.** The entity alias. Registered in pass 1 so every other entity can reference it. |
| `templates` | Template ids / paths / calls, applied in order. **Later overwrites earlier.** |
| `components` | Components added after the templates, so they override template components. |
| `remove` | A list of `{"type": ...}` dicts whose components are removed after the above. Supported by `_update_entity` but used by no shipped scene. |

Processed in **two passes** — register all ids, then fill all components. That is what makes
order-independent cross-references possible. See
[../core/scene-pipeline.md §Two-pass](../core/scene-pipeline.md#two-pass-entity-loading).

Every entity definition is additionally stored as a template under its own `id`, so `"templates":
["crate01"]` on a later entity clones crate01's definition. See
[entity-and-template.md §Every entity becomes a template](entity-and-template.md#every-entity-becomes-a-template).

## `handlers`

```jsonc
"handlers": [
    ["SCENE_START", {
        "id": "ev_start_game",
        "actions": ["SEQ",
                     ["SCRIPT", "load_image", {"image_file": "sokoban_splash.png"}],
                     ["SCRIPT", "play_music", {"music_file": "dungeon_theme.flac", "volume": 0.5}],
                     ["SCRIPT", "load_quest", {"scene_file": "games/sokoban/sokoban_level01"}]]
    }]
]
```

Each entry is a two-element list `[event_type, handler_dict]`. The dict needs `id` (unique, used for
overwrite and for `cleanup/handlers`) and `actions` (a `json_logic` tree). Any other key —
`description` is common — is stored and ignored.

Handlers may also be nested inside a component's `params`, where the pipeline picks them up via the
path `entities/components/params/handlers`. Full syntax and operator reference:
[handlers-and-actions.md](handlers-and-actions.md).

**An event with no registered handler is silently dropped**, and events not listed in a
`GameEventsExProcessor`'s `process` filter are dropped too.

## Keys that look real but are not

| Key | Status |
|-----|--------|
| `progress_bar` | Present in `empty.jsonc` as `["gui:SimpleProgressBar", {...}]`. **No code reads it.** Grep finds no `progress_bar` or `SimpleProgressBar` anywhere else in the repo. |
| `$schema` | Real, but consumed by your **editor**, not the engine. See [schemas.md](schemas.md). |
| `phases` | Referenced by the `PHASE_START` event type and message template, but no scene key or loader step exists. |

Unknown top-level keys are ignored without warning — `get_coll_value` only looks for the paths the
pipeline declares. A typo like `"entites"` therefore loads a scene with no entities and no error.

## YAML scenes

`.yaml` works wherever `.jsonc` does; `get_dict_from_file` dispatches on the suffix.
`tests/04_collisions/test_collisions_05.yaml` is the reference. You lose `$schema`-driven editor
completion, which is why `.jsonc` is the norm here.

## Related

- [../core/scene-pipeline.md](../core/scene-pipeline.md) — the loader.
- [entity-and-template.md](entity-and-template.md) · [component-params.md](component-params.md) ·
  [ai-definitions.md](ai-definitions.md) · [handlers-and-actions.md](handlers-and-actions.md)
- [../reference/index.md](../reference/index.md) — names you can write.
