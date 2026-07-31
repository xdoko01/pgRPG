# JSON Schemas

> Last updated: 2026-07-30 | Verified by: Source-verified
> `example_game/core/schemas/{scene,entity,template,component,command,processor,definitions}.schema.json`
> and `components/position.schema.json`; Runtime-verified — every template reference and every
> `module:ClassName` string in `resources/` was validated against the fixed fragments (#95)

The schemas exist for **editor support while authoring**. Nothing in the engine validates against
them at load time; the engine's validation is the `assert`/`ValueError` pattern inside each component
constructor.

## Layout

```
example_game/core/schemas/
  scene.schema.json          top level — required id/title/description/objective, cleanup, arrays
  entity.schema.json         id + templates + components
  template.schema.json       entity plus `vars`
  component.schema.json      oneOf → components/*.schema.json      (49 entries)
  command.schema.json        oneOf → commands/*.schema.json        (38 entries)
  processor.schema.json      oneOf → processors/<system>/*.json    (~130 entries)
  definitions.schema.json    shared fragments
  components/  commands/  processors/    the per-item schemas
```

`components/_old/` holds superseded schemas and is not referenced.

## Wiring it up

Put a `$schema` reference at the top of the scene file, with the right number of `../` for its depth:

```jsonc
{
    "$schema": "../../core/schemas/scene.schema.json",       // resources/scenes/x.jsonc
    "$schema": "../../../../core/schemas/scene.schema.json", // resources/scenes/games/sokoban/x.jsonc
    ...
}
```

VS Code resolves relative `$schema` paths, giving hover documentation, completion and inline errors.
That is the only mechanism *while authoring* — there is no CLI validation step. In CI,
`tests/example_game/test_resource_schemas.py` sweeps the shipped `resources/` and validates every
component definition against its per-component schema, every template reference against
`#/definitions/template_ref`, and every `module:ClassName` string against `#/definitions/class_def`.
It is a **ratchet**: `KNOWN_VIOLATIONS` records the component types still failing, as ceilings.

## What a per-component schema gives you

`components/position.schema.json` is the best-developed example. It supplies:

- **`examples`** — real JSON snippets, surfaced by the editor on hover.
- `type` constrained to an `enum` of the single valid `"module:ClassName"` string. This is what makes
  the `oneOf` in `component.schema.json` discriminate.
- Per-param `title`, `description`, `default`, and a type constraint.
- Each param accepts **either** its real type **or** a `$ref` to
  `definitions.schema.json#/definitions/template_var` (`^\$[a-zA-Z_][a-zA-Z0-9_]*$`) — so
  `"tile_x": "$tileX"` validates inside a template.
- Conditional requirements in `$defs`: "either `x` or `tile_x`", "either `y` or `tile_y`", plus
  `map` required.

That conditional pattern (`cond_either_x_or_tile_x_required`) is the model to copy for any other
component with alternative param forms.

## Generation

The schemas are generated from Python signatures by the tools in `pgrpg/utils/`
(`entity_json_generator.py`, `generate_model_json_from_template.py`,
`generate_tiled_json_from_template.py`) and then hand-extended. They are therefore **derived
artefacts that drift**. When the two disagree, the **component docstring is authoritative** — it is
what the constructor actually reads.

## Known schema defects

These matter because a schema that silently matches nothing gives no editor warnings, which reads as
"my file is valid".

| Defect | Detail |
|--------|--------|
| **`cleanup.processors` typed as `array of string`** | The loader requires `[group_id, "module:Class"]`. See [../core/scene-pipeline.md](../core/scene-pipeline.md#-cleanupprocessors-does-not-work). |
| **`scene.schema.json` uses `minLength` on arrays** | `prereqs` has `"minLength": 0` where `minItems` is the array keyword. No-op. |
| **`processors`, `maps`, `dialogs`, `handlers` are untyped arrays** | `scene.schema.json` declares them `"type": "array"` with no `items`, so nothing validates their contents — despite `processor.schema.json` and `command.schema.json` existing. Wiring those in is the single biggest available improvement. |

## One template reference definition, not two

A template is applied either as a string (`"t_tile_pos(5, 5, test_arena_sand)"`) or as a list — the
four forms `pgrpg.functions.str_utils.parse_fnc_list` accepts: `[name]`, `[name, [args]]`,
`[name, {kwargs}]`, `[name, [args], {kwargs}]`. **`definitions.schema.json#/definitions/template_ref`
is the single definition of that shape**, `$ref`d from both `entity.schema.json` and
`template.schema.json`.

Do not add a second one. The `basics/template_str_def` / `template_list_def` / `template_def` set
removed in #95 was exactly that: a parallel definition that drifted until it matched nothing, while
the copy next to it stayed correct.

Note the distinction between two identically named keys:

- a **scene's** `templates` holds whole template *definitions* (`template.schema.json` documents);
- a **template's** or **entity's** `templates` holds *references* (`template_ref`).

## Bugs of this shape, already fixed

These share one failure mode — a schema that looks authoritative but validates less than it appears
to, with no editor warning to say so.

| Issue | What it was |
|-------|-------------|
| [#80](https://github.com/xdoko01/pgRPG/issues/80) | A `$ref` beside `properties`/`required` shadowed the local keywords, disabling params validation (commit `69ff7e92`). If a schema appears to validate nothing, check for a sibling `$ref`. |
| [#83](https://github.com/xdoko01/pgRPG/issues/83) | Documents declared draft-07 while relying on `prefixItems`, which draft-07 ignores — tuple validation was silently off across 148 files. All schemas now declare `2020-12`. |
| [#95](https://github.com/xdoko01/pgRPG/issues/95) | `\(` / `\)` used as grouping in three patterns; in ECMA-262 they are literal parens, so each pattern demanded a leading `(` and matched nothing. |

## Adding a schema for a new component

1. Create `components/<module>.schema.json` with `$id`, `$schema` (2020-12), `title`,
   `description`, `examples`, `required: ["type", "params"]`, `type` as a single-value `enum`, and
   per-param `properties`.
2. Allow `template_var` alongside each param's real type, so the component can be used inside a
   template.
3. Add a `{"$ref": "components/<module>.schema.json"}` line to `component.schema.json`'s `oneOf`.
4. Copy an existing file rather than writing from scratch — `position.schema.json` for conditional
   params, `damageable.schema.json` for a simple one.

Because `component.schema.json` uses `oneOf`, a component object that matches **two** schemas is an
error. Keep the `type` enum single-valued so exactly one branch can match.

## Related

- [component-params.md](component-params.md) — what the params actually mean.
- [scene-format.md](scene-format.md) — the keys the top-level schema covers.
- [../SCOPE.md](../SCOPE.md) — status register including these defects.
