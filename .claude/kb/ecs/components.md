# Writing Components

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/ecs/__init__.py`,
> `example_game/core/components/{position,collidable,camera,brain_ai,destroy_on_no_health}.py`,
> `pgrpg/core/managers/ecs_manager.py` @ `c7b9a5f1`

A Component is **data only**. It carries no game logic; processors read and write it.

## The base class

```python
class Component(object):
    def __init__(self): pass
    def reinit(self): pass          # display config changed
    def pre_save(self): pass        # drop non-serializable refs
    def post_load(self): pass       # rebuild them
    def __str__(self): ...          # prints every __slots__ value + size in bytes
```

`Component` inherits `object` **explicitly** — required for `__slots__` to work as intended, and the
base `__str__` iterates `self.__slots__`, so a component without `__slots__` breaks its own
`__str__` (and therefore `ecs_manager.get_debug_info()` and the debug renderer).

## The minimal component

```python
from pgrpg.core.ecs import Component

class MyComponent(Component):
    __slots__ = ['value', 'active']

    def __init__(self, value=0, active=True):
        super().__init__()
        self.value = value
        self.active = active
```

Place it under `MODULEPATHS["COMPONENT_MODULE_PATH"]` — `example_game/core/components/my_component.py`
for `"COMPONENT_MODULE_PATH": "core.components"`. Reference it from JSON as:

```jsonc
{"type": "my_component:MyComponent", "params": {"value": 42}}
```

The `module:ClassName` form is resolved by `get_class_from_def` — see
[../authoring/component-params.md](../authoring/component-params.md).

## House conventions in this repo

The shipped components follow a consistent shape. Match it.

### 1. `__slots__` is mandatory

Memory (thousands of components per scene) and `__str__` both depend on it.

`Collidable`'s slot list also documents the component's full surface at a glance — that is part of
why the convention is worth keeping.

### 2. `*args, **kwargs` + `kwargs.get`, not named parameters

```python
def __init__(self, *args, **kwargs):
    super().__init__()
    self.ttl = kwargs.get('ttl', 0)
```

Why: `params` dicts from JSON often carry extra keys the component does not care about. `BrainAI`
receives `handlers` (consumed by the scene pipeline, not by the component) and simply ignores it.
A strict signature would raise `TypeError` on unexpected keys. `Position`, `Collidable`, `Camera`,
`Damageable`, `DestroyOnNoHealth` and most others use this form.

Newer/simpler components (`Movable`, some flags) do use named parameters. Both work; `**kwargs` is
safer for anything a scene author will touch.

### 3. Validate with `assert`, raise `ValueError`

```python
try:
    assert isinstance(self.map, str), f'Map "{self.map}" is not a string for {self.__class__}.'
    assert isinstance(self.x, int),   f'Position x is not an integer for {self.__class__}.'
except AssertionError:
    raise ValueError
```

`ecs_manager.create_component_from_def` catches `ValueError` specifically, logs
`Error while creating component "<type>" with parameters "<params>"` and re-raises. **A bad param
therefore fails scene loading loudly** — the right behaviour for authoring errors. Note the assert
messages are what you will see in the AssertionError, not in the ValueError, so log level matters
when debugging.

Do not use bare `raise` for a validation failure; the manager only recognises `ValueError`.

### 4. Accept tile-relative params for world geometry

Anything describing world geometry should take a `*_tiles` form and multiply by
`GAME["TILE_RES_PX"]` at construction. `Position` (`tile_x`/`tile_y`), `Collidable`
(`x_tiles`/`y_tiles`/`dx_tiles`/`dy_tiles`), `Teleport` (`tile_dest_x`), `CanSee`/`CanHear`
(`distance_tiles`) and `HasTargetPosition` all do this. See
[../_shared/resolution.md §Tile-relative params](../_shared/resolution.md#tile-relative-params).

`Collidable._extent` is the reference implementation:

```python
@staticmethod
def _extent(kwargs, px_key, tiles_key, default=None):
    if px_key in kwargs:    return kwargs[px_key]          # absolute — never scaled
    if tiles_key in kwargs: return round(kwargs[tiles_key] * GAME["TILE_RES_PX"])
    return default
```

**Never hardcode a pixel size.** `tests/core/maps/test_map.py` and `tests/core/models/test_model.py`
assert correct rendering at 32, 64 and 96 px; a hardcoded size fails the suite.

### 5. Doctests in the class docstring

```python
    Tests:
        >>> c = Position(**{"x": 0, "y": 0, "map": "test_map"})
        >>> c.x
        0
```

Run with `python -m core.components.position -v` from `example_game/`. The module footer is always:

```python
if __name__ == '__main__':
    import doctest
    doctest.testmod()
```

### 6. Ship a `*Mock` dataclass when commands need one

Command modules' doctests run without a world, using `ECSManagerMock`, which returns mock components:

```python
@dataclass
class PositionMock:
    x: int = 0
    y: int = 0
    map: str = 'map_mock'
    ...
```

Add one only if a command's doctest needs your component.

### 7. Document `Used by:` and a JSON example

Every shipped component's docstring lists the processors that consume it and shows the JSON form.
This is the only place that mapping is recorded, so keep it current — the KB links to it rather than
duplicating it.

## Lifecycle hooks

### `reinit()`

Called for **every component instance** by `main.reinit()` →
`ecs_manager.reinit_components()`, which walks `get_all_dict_values(_world._entities)`. Use it to
rebuild anything derived from display configuration.

`Camera.reinit()` is the reference case — it re-reads `DISPLAY["RESOLUTION"]`, recomputes the halves
and allocates a new `Surface`, but only when `screen_fill` is set:

```python
def reinit(self):
    if not self.screen_fill: return
    self.screen_width  = DISPLAY["RESOLUTION"][0]
    self.screen_height = DISPLAY["RESOLUTION"][1]
    ...
    self.screen = Surface((self.screen_width, self.screen_height))
```

Only `Camera` and `FlagShowInventory` implement it in the example game. Notably `RenderableModel`
does **not**, which is one half of why `TILE_RES_PX` cannot change at runtime — see
[../_shared/resolution.md §Set it at start-up only](../_shared/resolution.md#set-it-at-start-up-only).

### `pre_save()` / `post_load()`

For serialization. `pre_save` must drop anything unpicklable; `post_load` must rebuild it.
`Camera` is again the reference:

```python
def pre_save(self):  self.screen = None
def post_load(self): self.screen = Surface((self.screen_width, self.screen_height))
```

> ⚠️ There is **no save/load implementation yet**. `example_game/core/states/game.py` raises
> `NotImplementedError` on the save and load keys. The hooks exist so components are ready when it
> lands. See [../SCOPE.md](../SCOPE.md).

## Flag components

A large fraction of the components in this engine are **flags**: near-empty markers added by one
processor and consumed (then removed) by another, within a single frame. Naming tells you the phase:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `FlagDo*` | An intent, produced by a command | `FlagDoMove`, `FlagDoAttack` |
| `FlagIsAboutTo*` | A pending interaction, subject or object named in the flag | `FlagIsAboutToPickEntity`, `FlagIsAboutToBeDamagedBy` |
| `FlagHas*` | A completed action, on the actor | `FlagHasCollided`, `FlagHasPicked`, `FlagHasScored` |
| `FlagWas*By` | A completed action, on the target | `FlagWasPickedBy`, `FlagWasDamagedBy` |
| `FlagAdjust*` | A post-creation fixup request | `FlagAdjustCollidable`, `FlagAdjustMovement` |

The paired `Remove*Processor`s are what make this work, and their placement in the scene's
`processors` list defines the frame's phase boundaries. See
[processors.md §The generate/perform/remove idiom](processors.md#the-generateperformremove-idiom).

The upshot for a component author: a flag is cheap, and adding one is the normal way to communicate
between processors. Do not add state to an existing component to signal a transient condition.

## Related

- [processors.md](processors.md) — the consumers.
- [../authoring/component-params.md](../authoring/component-params.md) — the JSON side.
- [../reference/index.md §Components](../reference/index.md#components) — the full inventory.
- [../_shared/resolution.md](../_shared/resolution.md) — tile-relative params.
