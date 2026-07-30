# `TILE_RES_PX` — One Resolution, Applied at Load Time

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/config/defaults.jsonc`,
> `pgrpg/core/maps/map.py`, `pgrpg/core/models/model.py`,
> `example_game/core/components/{position,collidable,camera}.py`, `pgrpg/core/main.py` (`reinit`);
> Test-verified `tests/core/maps/test_map.py`, `tests/core/models/test_model.py` @ `c7b9a5f1`

`GAME["TILE_RES_PX"]` (default `64`) is **the single resolution the engine renders at**. It is both
the sprite size and the world grid unit.

## All art is normalised once, at load

The native resolution of a source asset does not matter. Author art at whatever size suits it; the
engine scales it to `TILE_RES_PX` when it is loaded, and never again.

**Tile images** — `pgrpg/core/maps/map.py`:

```python
self.tmxdata.images = images_rescale(self.tmxdata.images,
                                     (GAME["TILE_RES_PX"], GAME["TILE_RES_PX"]))
```

`images_rescale(images, scale)` requires both arguments on purpose: a default scale would silently
produce wrong-sized tiles at any other resolution, and pytmx relies on unused GIDs staying `None`
rather than becoming blank surfaces.

**Animated models** — `pgrpg/core/models/model.py`. `load_model(filepath, dim)` canonicalises `dim`
to a plain `(int, int)` tuple so `(64, 64)`, `[64, 64]` and `Vector2(64, 64)` share one cache entry,
then constructs `Model(filepath, target_dim)`. Inside `__init__`, `_resize(target_dim)` runs **before
the instance reaches the `lru_cache`**:

```python
self._load_model(self.model_file)
if (self.dim.x, self.dim.y) != target_dim:
    self._resize(target_dim)
self._check_model()
```

`_resize` is private for a documented reason: resizing a *cached* model in place would rescale pixels
that an earlier caller already scaled, so a model loaded at one size and then another would come back
degraded. `Model` is `@functools.lru_cache(maxsize=32)`-decorated at class level, so the cache key is
`(model_file, target_dim)` — the same file at two sizes is two entries, and each is immutable.

In this repository the tilesets are 32×32 and nearly every model is 64×64. Both render correctly at
any `TILE_RES_PX`.

## The world grid

Entity positions are stored **in pixels** and converted to tile coordinates by integer division:

```python
def get_tile(self):                                    # Position
    return (self.x // GAME["TILE_RES_PX"], self.y // GAME["TILE_RES_PX"])
```

`Position` also *centres* an entity in its tile when constructed from tile coordinates:

```python
self.x = kwargs.get('x', kwargs.get('tile_x', 0) * TILE_RES_PX + TILE_RES_PX // 2)
```

So `tile_x: 5` at 64 px gives `x = 352`, not 320. Map pixel dimensions follow the same rule:
`self.width = tmxdata.width * TILE_RES_PX`.

`TILE_RES_PX` also sizes inventory slots and converts `distance_tiles` to pixels in `CanSee` and
`CanHear`.

## Tile-relative params

Because the value is a world constant, components that describe world geometry accept
**tile-relative** parameters and convert them at construction:

| Component | Tile-relative | Absolute (never scaled) |
|-----------|---------------|-------------------------|
| `Position` | `tile_x`, `tile_y` | `x`, `y` |
| `Collidable` | `x_tiles`, `y_tiles`, `dx_tiles`, `dy_tiles` | `x`, `y`, `dx`, `dy` |
| `Teleport` | `tile_dest_x`, `tile_dest_y` | `dest_x`, `dest_y` |
| `CanSee`, `CanHear` | `distance_tiles` | `distance` |
| `HasTargetPosition` | tile coordinates per target | — |

**Prefer the tile-relative form when authoring.** Absolute pixel params still exist and are never
scaled — use them only when a value must be a fixed pixel size regardless of resolution.

`Collidable._extent` is the reference conversion:

```python
@staticmethod
def _extent(kwargs, px_key, tiles_key, default=None):
    if px_key in kwargs:    return kwargs[px_key]                        # absolute wins
    if tiles_key in kwargs: return round(kwargs[tiles_key] * GAME["TILE_RES_PX"])
    return default
```

It rounds to an `int` because the map-collision maths divides these values to reach tile coordinates.

### Why the fractions look strange

Shipped scenes contain values like `0.234375`, `0.421875`, `0.46875`. These are `n/64` — 15/64,
27/64, 30/64 — the original hand-tuned 64 px pixel counts expressed as tile fractions. Being dyadic
rationals they are **exact** in binary floating point and reproduce `n` precisely at 64 px, so
converting an old scene loses nothing.

When authoring new values, `n/64` fractions keep that property. Round numbers like `0.5` are fine too.

## Never hardcode a pixel size

Not for a sprite, a tile, a cull margin or a UI slot. Read `GAME["TILE_RES_PX"]` or derive from it.

`tests/core/maps/test_map.py` and `tests/core/models/test_model.py` assert correct rendering at
**32, 64 and 96 px**, so a hardcoded size fails the suite. `tests/example_game/test_collidable.py` and
`tests/example_game/test_map_collision_scaling.py` cover the collision-zone side.

## Set it at start-up only

`TILE_RES_PX` must be set in config before the process starts. Changing it at runtime leaves the
engine in a **half-applied state**.

The reinit path — `main.reinit()`, used by the settings screen and the `change_res` /
`toggle_fullscreen` console commands — is scoped to *display* configuration. It mutates the config
dicts in place, so a changed `TILE_RES_PX` genuinely reaches every module. But nothing re-normalises
assets that are already loaded:

- **`RenderableModel` implements no `reinit()`**, so loaded models keep their old tile size. (And even
  if it did, the `Model` `lru_cache` would have to be keyed correctly — which it is, so a fresh
  `load_model` at the new size *would* work; nothing calls it.)
- **Maps are neither components nor processors**, so the reinit sweep never sees them. `Map` has no
  `reinit()` at all.

The result: grid maths, collisions and cull margins move to the new size while tile and sprite images
plus `map.width` / `map.height` stay at the old one.

Only `Camera` and `FlagShowInventory` implement `reinit()`. Nothing in the UI exposes `TILE_RES_PX`,
so this state is unreachable in normal play — **change the value in config and restart.**

## One grid cell per model

A model cannot declare a footprint larger than a single cell. Anything authored bigger is squashed
into one cell by `_resize`. Multi-cell entities are not supported.

## Related

- [../authoring/component-params.md §Tile-relative](../authoring/component-params.md#tile-relative-vs-absolute-params)
- [../ecs/components.md](../ecs/components.md) — writing a component that honours this.
- [../core/configuration.md](../core/configuration.md) — the `GAME` section.
- [../core/bootstrap-and-loop.md §reinit](../core/bootstrap-and-loop.md#reinit--display-config-changes)
