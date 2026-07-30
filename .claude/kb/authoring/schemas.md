# JSON Schemas

> Last updated: 2026-07-30 | Verified by: Source-verified
> `example_game/core/schemas/{scene,entity,template,component,command,processor,definitions}.schema.json`
> and `components/position.schema.json`; Runtime-verified — the `class_def` and `template_str_def`
> regex patterns were tested against real values and match nothing @ `c7b9a5f1`

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
This is the only mechanism — there is no CLI validation step and no test that validates the shipped
scenes.

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
| **`definitions.schema.json#/basics/class_def` pattern matches nothing** | `^\([a-z]+\.\)*[a-z]+:[A-Z][a-z]+$` — `\(` and `\)` are **literal parentheses**, not a group, so the pattern demands a leading `(`. Tested: `movable:Movable`, `position:Position`, `renderable_model:RenderableModel` and `brain_ai:BrainAI` all fail. Even read as intended it would reject underscores and multi-capital class names. Currently `$ref`d by nothing, so harmless. |
| **`template_str_def` / `template_list_def` patterns match nothing** | Same `\(...\)` mistake, plus a mandatory trailing `(...)` that plain paths like `model/body/special/minotaur` do not have. These **are** `$ref`d, from `template.schema.json`'s `templates` array via `#/basics/template_def`. |
| **`prefixItems` / `items: false` in a Draft-07 document** | `template_list_def` uses Draft 2020-12 vocabulary. A Draft-07 validator ignores both keywords, so the tuple constraint has no effect. |
| **`basics` is not a schema keyword** | `definitions.schema.json` puts fragments under a top-level `basics` key as well as the standard `definitions`. `$ref "#/basics/..."` resolves by JSON Pointer, so it works — but a validator will not treat those subschemas as definitions, and some tooling will not follow them. |
| **`cleanup.processors` typed as `array of string`** | The loader requires `[group_id, "module:Class"]`. See [../core/scene-pipeline.md](../core/scene-pipeline.md#-cleanupprocessors-does-not-work). |
| **`scene.schema.json` uses `minLength` on arrays** | `prereqs` has `"minLength": 0` where `minItems` is the array keyword. No-op. |
| **`processors`, `maps`, `dialogs`, `handlers` are untyped arrays** | `scene.schema.json` declares them `"type": "array"` with no `items`, so nothing validates their contents — despite `processor.schema.json` and `command.schema.json` existing. Wiring those in is the single biggest available improvement. |

A related class of bug was fixed recently: issue #80, *"`$ref` beside `properties`/`required`
disabled params validation"* (commit `69ff7e92`). If a schema appears to validate nothing, check
whether a sibling `$ref` is shadowing the local keywords.

## Adding a schema for a new component

1. Create `components/<module>.schema.json` with `$id`, `$schema` (draft-07), `title`,
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
