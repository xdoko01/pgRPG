# Authoring — The Data Language

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/engine.py`,
> `pgrpg/functions/{translate,get_dict_params,str_utils,json_logic}.py`,
> `pgrpg/core/managers/{ecs_manager,command_manager,event_manager}.py`;
> cross-checked against all 78 files under `example_game/resources/scenes/` @ `c7b9a5f1`

Almost everything a "game" is in pgrpg is declared in data files, not Python. This domain documents
that language.

## The file types

| Files | Live in | Format | Declare |
|-------|---------|--------|---------|
| Scenes | `resources/scenes/` | `.jsonc`, `.yaml` | Which processors, maps, dialogs, templates, entities and handlers make up a level |
| Entities / templates | `resources/entities/` | `.json`, `.jsonc` | Reusable entity fragments, referenced by path |
| Behaviour trees | `resources/btrees/` | `.json` | Reusable AI subtrees |
| Dialogs | `resources/dialogs/` | `.json` | Dialog windows, with template inheritance |
| Models | `resources/models/` | `.json` + `.png` | Tiled-format animated sprite sheets |
| Maps | `resources/maps/` | `.tmx`, `.tsx` | Tiled tile maps |
| Schemas | `core/schemas/` | `.json` | Draft-07 JSON Schemas for editor validation |

Formats are interchangeable where the loader is used: `get_dict_from_file` tries `.toml`, `.yaml`,
`.json`, `.jsonc` in that order when the extension is omitted.
`tests/04_collisions/test_collisions_05` exists as both `.jsonc` and `.yaml` to prove it.

## Pages

| Page | Covers |
|------|--------|
| [scene-format.md](scene-format.md) | Every top-level scene key, with types and examples |
| [entity-and-template.md](entity-and-template.md) | Entity defs, template files, `vars`, template calls, entities-as-templates |
| [component-params.md](component-params.md) | The `{"type": ..., "params": ...}` form, tile-relative params, allow/deny lists |
| [ai-definitions.md](ai-definitions.md) | `cmd_tree` and `cmd_list` syntax, blackboards, AI templates |
| [handlers-and-actions.md](handlers-and-actions.md) | Handler registration, `json_logic` operators, script actions |
| [schemas.md](schemas.md) | JSON Schema validation, what the schemas cover and where they lie |

## The three substitution prefixes

Three different substitution mechanisms operate on data files, at three different times. Confusing
them is the most common authoring error, so learn all three.

| Prefix | Resolved by | Against | When |
|--------|-------------|---------|------|
| `$var` | `get_dict_params` → `translate` (`prefix=''` on the template's `vars` map) | Template arguments | **Template expansion**, at scene load |
| `^key` | `command_manager.execute_command_init` → `translate(prefix='^')` | The generator's **global blackboard** | **First tick** of the command |
| `%key` | the script itself, via `translate_str(prefix='%')` | `event.params` | **Handler execution**, inside a script |

```jsonc
// $ — template variable, substituted when the template is expanded
{"id": "t_tile_pos", "vars": ["$tileX=0", "$tileY=0", "$map"],
 "components": [{"type": "position:Position",
                 "params": {"tile_x": "$tileX", "tile_y": "$tileY", "map": "$map"}}]}

// ^ — blackboard reference, resolved on the command's first tick
{"command": ["move_to_checkpoints", {"checkpoints": "^checkpoints"}]}

// % — event parameter, substituted by the script into a string
["SCRIPT", "show_msg_window", {"html_text": "<b>Scene:</b> %id — %title"}]
```

Important differences in failure behaviour:

- **`$`** — an unmatched `$var` is left in place as a literal string. The component then receives
  `"$tileX"` and usually fails its `isinstance` assertion. Symptom: `ValueError` on scene load.
- **`^`** — an unmatched `^key` **raises `KeyError`** with
  `Cannot find value '^key' in the translation dictionary`. Deliberately loud. Symptom: crash on the
  frame the command first runs, not at load.
- **`%`** — an unmatched `%key` is left in place and shown to the player verbatim.

## The fourth, invisible substitution: entity aliases

Separate from the three prefixes, **every** string in a component's `params` and in a handler's
`actions` is checked against the entity alias table and replaced with an integer id if it matches.
No prefix, no opt-out. This is why `{"target": "player01"}` works.

It also means an entity alias that collides with a literal string you meant to keep will be silently
replaced. See [../_shared/aliases.md](../_shared/aliases.md).

## Authoring workflow

1. Copy `resources/scenes/empty.jsonc` as a starting point — it has every top-level key present and
   empty, plus a `$schema` reference.
2. Point `$schema` at `core/schemas/scene.schema.json` with the right number of `../` for your depth.
3. Add processors. This is the part with no safety net: a scene with the wrong processor set renders
   nothing, or moves nothing, with no error. Copy the processor block from the nearest test scene
   under `resources/scenes/tests/` — they are numbered `00_render` → `12_ai` and each adds one
   subsystem to the previous.
4. Add the map, templates and entities.
5. Run it: `python example_game/game.py -f tests/my_scene.jsonc` from the repository root.

The numbered test scenes are the real documentation for "which processors do I need for X".

## Related

- [../core/scene-pipeline.md](../core/scene-pipeline.md) — what the loader does with these files.
- [../_shared/filepaths-modulepaths.md](../_shared/filepaths-modulepaths.md) — where each path resolves.
- [../reference/index.md](../reference/index.md) — the names available to write.
