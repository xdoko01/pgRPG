# `World` — Internals, Queries and Lifecycle

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/ecs/__init__.py` @ `c7b9a5f1`;
> Test-verified `tests/core/ecs/`

## Data model

```python
class World:
    _processors      = defaultdict(list)   # {group_id: [Processor, ...]} sorted by priority desc
    _next_entity_id  = 0                   # monotonic counter, never reused
    _components      = {}                  # {ComponentType: {entity_id, ...}}
    _entities        = {}                  # {entity_id: {ComponentType: instance}}
    _dead_entities   = set()               # deferred deletions
    process_times    = defaultdict(int)    # only when timed=True
```

`World(timed=False)`. When `timed=True` the world swaps `self._process` for `self._timed_process`,
which accumulates per-processor-class milliseconds into `process_times`. Driven by config
`pgrpg.TIMED`; readable via `ecs_manager.get_proc_perf(sort=True)` and the `proc_perf` console
command.

Entity ids start at 1 (`_next_entity_id += 1` happens *before* the id is used) and are never reused
within a world. `clear_database()` resets the counter to 0.

## Queries

Five query families. All are decorated with `@functools.lru_cache()`.

| Method | Returns | Use |
|--------|---------|-----|
| `get_component(T)` | `[(entity, comp), ...]` | one component type |
| `get_components(T1, T2, ...)` | `[(entity, [c1, c2, ...]), ...]` | entities having **all** listed types |
| `get_components_ex(T1, ..., exclude=T)` | as above, minus entities having `T` | "movable but not AI-controlled" |
| `get_components_exs(include=(T1, T2), exclude=(T3, T4))` | as above, multiple excludes | both sides as tuples |
| `get_components_opt(T1, T2, optional=T3)` | `[(entity, [c1, c2, c3_or_None]), ...]` | one type is optional |

Note the differing call conventions — `get_components_exs` takes **both** sides as keyword tuples
while `get_components_ex` takes required types positionally and a single `exclude=`.

Implementation, from `_get_components`:

```python
for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
    yield entity, [entity_db[entity][ct] for ct in component_types]
```

`_get_components_ex` adds `.difference(comp_db.get(exclude_component_type, {}))` — note the `.get`
with a `{}` default: without it, excluding a type that no entity currently holds would raise
`KeyError` and be swallowed by the `except KeyError: pass`, silently returning nothing.

**Every query family swallows `KeyError` and yields nothing.** If a required component type has no
instances anywhere in the world, `comp_db[ct]` raises and the query returns an empty list — not an
error. So a processor whose components have all been removed simply does nothing, and a typo in a
component type produces silence rather than a traceback.

### Single-entity accessors

| Method | Behaviour |
|--------|-----------|
| `component_for_entity(e, T)` | The instance. **Raises `KeyError`** if absent. |
| `components_for_entity(e)` | Tuple of all instances for that entity. Raises if the entity is unknown. |
| `try_component(e, T)` | The instance or `None`. Still raises `KeyError` if the *entity* is unknown. |
| `try_components(e, *Ts)` | Generator yielding one list of all instances, or nothing if any is missing. |
| `has_component(e, T)` | `bool`. Uses `_entities.get(e, {})` — **returns `False` for an unknown entity** rather than raising. |
| `has_components(e, *Ts)` | `bool`, all-of, same tolerance for unknown entities. |

The `has_component*` tolerance is deliberate and documented in the source: `remove_component()` can
leave an entity with an empty component dict, and callers should not have to distinguish that from
"entity gone".

## Query caching

All five query methods are `@_lru_cache()`d. `clear_cache()` clears all five and is called from:

- `add_component`
- `remove_component`, `remove_component_force`
- `delete_entity(immediate=True)`
- `_clear_dead_entities()` (i.e. once per `process()`)
- `clear_database()`

Two consequences:

- **Any structural change invalidates every query cache.** Adding a component in a tight loop
  defeats the cache entirely. This engine adds and removes flag components constantly, so in
  practice the cache mostly helps *within* a frame across processors querying the same signature.
- `create_entity()` does **not** clear the cache directly — it delegates to `add_component` for each
  component passed, and its own `self.clear_cache()` line is commented out. `create_entity()` with
  no components therefore leaves the cache stale, but since a component-less entity matches no
  query, nothing observes it.

Because arguments are the cache key, they must be hashable. Types are; that is why the
`*_ex`/`*_exs`/`*_opt` APIs take types and tuples of types rather than lists.

## Entity lifecycle

### Creation

```python
entity_id = world.create_entity(*components)   # id, then add_component for each
```

`ecs_manager` wraps this — see [../core/scene-pipeline.md](../core/scene-pipeline.md).

### Deletion — deferred by default

```python
world.delete_entity(entity)                  # → _dead_entities, applied at next process()
world.delete_entity(entity, immediate=True)  # applied now; clears the cache
```

`process()` calls `_clear_dead_entities()` **before** running any processor, so a deletion requested
during frame N is visible from the start of frame N+1. Use `immediate=True` only outside entity
iteration — deleting mid-iteration over a query result mutates the sets being iterated.

`_clear_dead_entities` duplicates `delete_entity`'s body for speed; the source says so, and warns
that changes must be made in both places.

`delete_entity` on an unknown id raises `KeyError` (via `_entities[entity]`) in the immediate path;
in the deferred path it adds a phantom id to `_dead_entities`, which then raises inside
`_clear_dead_entities` at the start of the next frame. `ecs_manager.delete_entity` tolerates a
missing alias but not a missing id.

### Components on an entity

| Method | Behaviour |
|--------|-----------|
| `add_component(e, instance)` | Adds, **replacing** any existing instance of the same type. Creates the entity record if needed. Clears cache. |
| `remove_component(e, T)` | Removes. Raises `KeyError` if the entity or type is absent. Clears cache. Returns the entity id. |
| `remove_component_force(e, T)` | Same, but returns `None` instead of raising. |

`add_component` replacing silently is what makes the scene loader's template layering work: a later
template's `Position` simply overwrites an earlier one.

### `remove_component` keeps the entity — a deliberate fork change

Upstream esper deletes the entity record when its last component goes. This fork does not, and the
docstring explains why:

> Upstream esper drops the Entity record here, which makes an Entity disappear without ever being
> marked dead — that crashes `_clear_dead_entities()` and `delete_entity(immediate=True)`, and leaves
> aliases in `ecs_manager` pointing at an Entity that no longer exists.

So `delete_entity` stays the only way an entity leaves the world. The cost is that a fully-stripped
entity lingers; `get_empty_entities()` exists to detect that:

```python
def get_empty_entities(self) -> list:
    return [e for e, comps in self._entities.items() if not comps]
```

Its docstring states the invariant: **this should normally return an empty list.** The destroy system
adds `IsDestroyed` before stripping, and flag removals always leave identity components behind. A
non-empty result means something is leaking entities. Reachable as
`ecs_manager.get_empty_entities()`.

## Processor registry

```python
add_processor(processor_instance, proc_group_id='default', priority=0)
```

Asserts the argument is a `Processor` subclass instance, sets `priority` and `world` on it, appends
to the group's list and **re-sorts the group by priority descending** — so higher priority runs
first. Sorting on every add is O(n log n) per registration, which is fine because registration
happens only at scene load.

| Method | Behaviour |
|--------|-----------|
| `get_processor(T, proc_group_id='default')` | First instance of that exact type in the group, else `None`. Matches with `type(p) == T`, so **subclasses do not match**. |
| `remove_processor(T, proc_group_id='default')` | Detaches `world` and removes. Mutates the list while iterating it — safe only because it returns after the first hit in practice, but it does not `break`; prefer one instance per type per group. |
| `clear_processors()` | Detaches and removes across all groups. |
| `finalize_group(group)` / `finalize()` | Calls `finalize()` on processors; a `NotImplementedError` is re-raised as `ValueError(processor)`. |

### `process()`

```python
def process(self, proc_group_id='default', *args, **kwargs):
    self._clear_dead_entities()
    self._process(proc_group_id, *args, **kwargs)
```

`_process` simply calls `processor.process(*args, **kwargs)` for each processor in the group, in
priority order.

> ⚠️ **`World._process` does not catch exceptions.** An unhandled exception in one processor aborts
> every later processor in that group for that frame. This is why every processor must catch
> `SkipProcessorExecution` itself — see
> [processors.md §Execution throttling](processors.md#execution-throttling).

`ecs_manager.process` fixes the keyword set the engine passes:

```python
def process(proc_group_id, events, keys, dt, debug):
    _world.process(proc_group_id=proc_group_id, events=events, keys=keys, dt=dt, debug=debug)
```

So **every** processor's `process()` receives `events`, `keys`, `dt` and `debug` as keyword
arguments, whether it wants them or not. Signatures must end in `**kwargs`.

## Deviations from upstream esper 1.3

| Area | Upstream | This fork |
|------|----------|-----------|
| Processor storage | one `list` | `defaultdict(list)` keyed by group id |
| `process()` | runs all processors | runs one group: `process(proc_group_id='default', ...)` |
| Throttling | none | `Processor.exec_cycle_step` + `SkipProcessorExecution` |
| Queries | `get_component`, `get_components` | plus `get_components_ex`, `get_components_exs`, `get_components_opt` |
| `remove_component` | drops the entity record when empty | keeps it; `delete_entity` is the only removal |
| Diagnostics | — | `get_empty_entities()` |
| Timing | `process_times[name] = t` (last frame) | `process_times[name] += t` (cumulative ms) |
| Component base | plain | `reinit()`, `pre_save()`, `post_load()`, `__str__` over `__slots__` |
| Processor base | `process()` only | plus `reinit()`, `initialize()`, `pre_save()`, `post_load()`, `finalize()`, `cycle` counter |
| Removal helper | — | `remove_component_force()` |

Upstream project: <https://github.com/benmoran56/esper>.

## Related

- [components.md](components.md) · [processors.md](processors.md)
- [../core/managers.md](../core/managers.md) — `ecs_manager`'s wrapper API.
