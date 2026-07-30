# Component Definitions and Params

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/managers/ecs_manager.py`,
> `pgrpg/functions/get_class_object.py`, `pgrpg/functions/translate.py`,
> `example_game/core/components/{position,collidable,camera,controllable,has_weapon,factory}.py`,
> `example_game/core/schemas/component.schema.json` @ `c7b9a5f1`

## The form

```jsonc
{"type": "position:Position", "params": {"tile_x": 5, "tile_y": 5, "map": "arena"}}
```

Two keys. `params` is optional and defaults to `{}`.

## The `type` field

`"<module path>:<ClassName>"`, resolved by `get_class_from_def` against
`MODULEPATHS["COMPONENT_MODULE_PATH"]`:

```python
module, name = class_def.split(':')
return get_class_object(None, class_package + '.' + module, name)
```

With `"COMPONENT_MODULE_PATH": "core.components"`, `"position:Position"` imports
`core.components.position` and takes `Position` from it. Dots navigate sub-packages.

Failure modes:

- A missing `:` makes `class_def.split(':')` return one element → `ValueError` from the unpacking,
  caught and re-raised as `ValueError(f'Error during loading of class "{name}"')`. Note `name` is
  unbound at that point, so this itself raises `UnboundLocalError` — the error you actually see is
  confusing. **Always include the colon.**
- A wrong module or class name raises `ValueError` from `str_to_package_module` /
  `str_to_class` with a clear message.

Older scene files and some docstrings show the bare form `{"type": "Position"}`. That does **not**
work with the current resolver — it needs `module:ClassName`.

## How params reach the constructor

```python
comp_params_substituted = translate(_alias_to_entity, comp_params)
return new_class(**comp_params_substituted)
```

So:

1. **Every string value is alias-translated.** Recursively through dicts, lists and tuples. A string
   matching a registered entity alias becomes that entity's integer id; anything else passes through
   unchanged (`trans_dict.get(value, value)`). No prefix is involved.
2. The result is splatted as keyword arguments. Param names are therefore constructor kwarg names.

Because most components read params with `kwargs.get(...)`, **an unknown param is silently ignored**.
A typo produces a default value, not an error. This is also what lets `BrainAI` carry a `handlers`
key that only the scene pipeline reads.

Conversely, a component that declares named parameters will raise `TypeError` on an unexpected key.
See [../ecs/components.md §Conventions](../ecs/components.md#house-conventions-in-this-repo).

### Alias translation examples

```jsonc
{"type": "has_weapon:HasWeapon", "params": {
    "weapons": {"bow": {"weapon": "wooden_bow", "generator": "wooden_arrows_pack"}}}}
```

`"wooden_bow"` and `"wooden_arrows_pack"` are entity aliases and arrive at the constructor as ints.
This works even though those entities appear *later* in the `entities` list, because pass 1 registered
every alias first.

> ⚠️ Translation is unconditional and matches on exact string equality. If you name an entity
> `"bow"`, then `{"type": "weapon_in_use:WeaponInUse", "params": {"type": "bow"}}` silently becomes
> `{"type": 7}`. Avoid aliases that collide with literal param values.

## Tile-relative vs absolute params

Anything describing world geometry should be authored in **tile units**. The component multiplies by
`GAME["TILE_RES_PX"]` at construction; absolute pixel params are taken literally and never scaled.

| Component | Tile-relative (preferred) | Absolute |
|-----------|---------------------------|----------|
| `Position` | `tile_x`, `tile_y` | `x`, `y` |
| `Collidable` | `x_tiles`, `y_tiles`, `dx_tiles`, `dy_tiles` | `x`, `y`, `dx`, `dy` |
| `Teleport` | `tile_dest_x`, `tile_dest_y` | `dest_x`, `dest_y` |
| `CanSee`, `CanHear` | `distance_tiles` | `distance` |
| `HasTargetPosition` | tile coordinates in each target tuple | — |

`Position` centres the entity in its tile:

```python
self.x = kwargs.get('x', kwargs.get('tile_x', 0) * TILE_RES_PX + TILE_RES_PX // 2)
```

so `tile_x: 5` at 64 px means `x = 352`, not 320.

`Collidable` describes a half-extent from the entity centre plus an offset, and absolute wins if both
forms are given (`Collidable._extent`). The fractional values in shipped scenes are
`n/64` — `0.234375` = 15/64, `0.421875` = 27/64 — which are exact in binary floating point and
reproduce the original pixel values exactly at 64 px.

Full discussion: [../_shared/resolution.md](../_shared/resolution.md).

## Allow / deny lists

Several components filter interactions with a pair of sets. `Collidable` has four pairs:

```jsonc
{"type": "collidable:Collidable", "params": {
    "x_tiles": 0.5, "y_tiles": 0.5,
    "position_fix_walkaround_mode": true,
    "accept_pos_fix_from_denylist": ["ALL"]        // nothing can push me
}}
```

| Param | Meaning |
|-------|---------|
| `allowlist` | Only collide with these entities |
| `denylist` | Never collide with these |
| `apply_pos_fix_to_allowlist` | Only push these entities on contact |
| `apply_pos_fix_to_denylist` | Never push these |
| `accept_pos_fix_from_allowlist` | Only be pushed by these |
| `accept_pos_fix_from_denylist` | Never be pushed by these |
| `position_fix_walkaround_mode` | On collision, try to slide around the obstacle (default `true`) |

Each list becomes a `set` in the constructor. The special token `"ALL"` matches everything — it is
handled by `pgrpg/functions/allow_deny_filters.py` (`allow_deny_list_filter`,
`allow_deny_item_filter`), which is also where the precedence between allow and deny is decided.

Idiomatic uses from `sokoban_level01.jsonc`:

```jsonc
// a wall: solid, immovable
"accept_pos_fix_from_denylist": ["ALL"]

// a crate: pushable, but only straight (no sliding around)
"position_fix_walkaround_mode": false

// a projectile: collides and damages, but is never displaced
"accept_pos_fix_from_denylist": ["ALL"]
```

Because these lists hold entity aliases, they are alias-translated to ints like any other param —
`"ALL"` survives because it is not an alias.

## Nested definitions inside params

Some params carry whole sub-documents:

| Component | Param | Contains |
|-----------|-------|----------|
| `Factory` | `prescription` | A full entity definition (`id`, `templates`, `components`) |
| `BrainAI` | `cmd_tree` / `cmd_list` | An AI structure — [ai-definitions.md](ai-definitions.md) |
| `BrainAI` | `blackboard` | Initial global blackboard values |
| `BrainAI` | `handlers` | Event handlers, picked up by the scene pipeline |
| `Controllable` | `control_cmds` | Action → list of `[command, params]` |
| `HasTargetPosition` | `targets` | `[map, tile_x, tile_y, tolerance_px]` tuples |
| `Debug` | `info` | Free-form dict rendered by the debug processor |

Alias translation recurses into all of these, which is exactly what makes
`"target": "player01"` work five levels deep in a behaviour tree.

## Frequently used components

The full inventory is in [../reference/index.md §Components](../reference/index.md#components).
The ones you will write most often:

```jsonc
{"type": "position:Position",   "params": {"tile_x": 5, "tile_y": 5, "map": "arena"}}
{"type": "movable:Movable",     "params": {"velocity": 100, "accelerate": -2}}
{"type": "renderable_model:RenderableModel", "params": {"model": "generic/body/male/body_male_human_white.json"}}
{"type": "camera:Camera",       "params": {"always_center": false, "screen_fill": true}}
{"type": "collidable:Collidable", "params": {"x_tiles": 0.234375, "y_tiles": 0.421875, "dy_tiles": 0.125}}
{"type": "damageable:Damageable", "params": {"health": 100}}
{"type": "damaging:Damaging",     "params": {"damage": 25}}
{"type": "can_see:CanSee",        "params": {"angle": 120, "distance_tiles": 5}}
{"type": "can_hear:CanHear",      "params": {"distance_tiles": 5}}
{"type": "debug:Debug",           "params": {"info": {"name": "NPC"}}}
```

`Camera` deserves a note: `screen_fill: true` makes the camera track the display resolution and is
the only reason `Camera.reinit()` does anything. Without it, resolution changes leave the camera at
its authored size.

## Reading a component's real parameter list

The generated JSON Schemas under `example_game/core/schemas/components/` are derived from the Python
signatures and are the fastest way to see valid params —
but they are generated, so **the docstring in the component module is authoritative**. Every shipped
component's class docstring lists its params with types and shows a JSON example.

## Related

- [../ecs/components.md](../ecs/components.md) — writing the Python side.
- [../_shared/resolution.md](../_shared/resolution.md) — tile units.
- [../_shared/aliases.md](../_shared/aliases.md) — alias translation.
- [schemas.md](schemas.md) — schema validation.
