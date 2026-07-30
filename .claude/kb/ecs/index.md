# ECS

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/ecs/__init__.py` (593 lines)
> @ `c7b9a5f1`; Test-verified `tests/core/ecs/`

The whole ECS is one file: `pgrpg/core/ecs/__init__.py`. It is a **modified fork of esper 1.3**
(MIT) with four additions, all marked in the source with `# ... by xdoko01` comments.

## The three concepts

| Concept | Is | Holds |
|---------|-----|-------|
| **Entity** | an `int` | nothing — identity only |
| **Component** | a `Component` subclass instance | data, in `__slots__` |
| **Processor** | a `Processor` subclass instance | behaviour, run once per frame per group |

An entity is never an object. `World` keeps two indexes over plain ints:

```python
_entities   = {entity_id: {ComponentType: instance, ...}}   # by entity
_components = {ComponentType: {entity_id, ...}}             # by type
```

Every query is a set operation over `_components` followed by lookups in `_entities`.

## What this fork adds to esper 1.3

1. **Processor groups** — `_processors` is a `defaultdict(list)` keyed by group id, and
   `World.process(proc_group_id=...)` runs one group. This is how pause and inventory overlays are
   implemented without a single `if paused:`.
2. **Execution throttling** — `Processor.exec_cycle_step` (set from a `step` param) makes a
   processor run every N frames, signalled by raising `SkipProcessorExecution`.
3. **Extended queries** — `get_components_ex` (exclude one type), `get_components_exs`
   (include/exclude tuples), `get_components_opt` (optional type yielded as `None`).
4. **Lifecycle hooks** — `reinit`, `pre_save`, `post_load`, `finalize` on `Component` / `Processor`;
   `remove_component` keeps the entity record alive; `get_empty_entities()` diagnostic.

Details and the exact behavioural differences: [world.md §Fork deltas](world.md#deviations-from-upstream-esper-13).

## Pages

| Page | Covers |
|------|--------|
| [world.md](world.md) | `World` internals, all query methods, query caching, entity lifecycle, processor registry, timing, fork deltas |
| [components.md](components.md) | Writing a Component: `__slots__`, constructor conventions, `reinit` / `pre_save` / `post_load`, flag components |
| [processors.md](processors.md) | Writing a Processor: `process()`, throttling, groups, priority, `PREREQ`, dependency injection, `finalize` |

## Access from outside

Game code does not import `World`. It goes through `ecs_manager`, which owns the single instance:

```python
from pgrpg.core.managers import ecs_manager
ecs_manager.add_component(entity_id, MyComponent(...))
ecs_manager.try_component(entity_id, Position)
```

Inside a processor, `self.world` is the `World` and is the right thing to query. Inside a command,
`ecs_mng` is the `ecs_manager` module. See [../core/managers.md](../core/managers.md).

## Related

- [../core/scene-pipeline.md](../core/scene-pipeline.md) — how components and processors get created.
- [../authoring/component-params.md](../authoring/component-params.md) — the JSON side.
- [../reference/index.md](../reference/index.md) — everything the example game defines.
