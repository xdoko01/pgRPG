# Writing Processors

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/ecs/__init__.py`,
> `pgrpg/core/managers/ecs_manager.py`,
> `example_game/core/processors/command_system/*.py`,
> `example_game/core/processors/event_system/game_events_processor.py` @ `c7b9a5f1`

A Processor is **behaviour only**. It queries the world for component signatures and acts.

## The base class

```python
class Processor:
    world = None
    cycle = None             # frames this processor has been ticked
    exec_cycle_step = None   # run every N cycles

    def __init__(self, *args, **kwargs):
        self.cycle = 0
        self.exec_cycle_step = kwargs.get('step', 1)

    def reinit(self): pass
    def initialize(self, register, proc_group_id='default'): register(self, proc_group_id)

    def process(self, *args, **kwargs):
        self.cycle += 1
        if self.cycle % self.exec_cycle_step != 0: raise SkipProcessorExecution

    def pre_save(self):  raise NotImplementedError
    def post_load(self): raise NotImplementedError
    def finalize(self):  raise NotImplementedError
```

Note `pre_save`, `post_load` and `finalize` **raise `NotImplementedError` by default** — unlike
`Component`, where they are no-ops. `clear_processors()` catches this and downgrades it to a warning,
so an unimplemented `finalize` is survivable but noisy.

## The template

```python
__all__ = ['MyProcessor']

import logging
logger = logging.getLogger(__name__)

from pgrpg.core.ecs import Processor, SkipProcessorExecution
from core.components.position import Position       # one import per component — the house style
from core.components.movable import Movable

class MyProcessor(Processor):
    """One-line summary.

    Involved components:
        - Position
        - Movable

    Related processors:
        - ...

    What if this processor is disabled?
        - ...

    Where should the processor be planned?
        - after X, before Y
    """

    PREREQ = []

    def __init__(self, FNC_ADD_EVENT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_event_fnc = FNC_ADD_EVENT

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (pos, mov) in self.world.get_components(Position, Movable):
            ...

    def pre_save(self):  pass
    def post_load(self): pass
    def finalize(self, *args, **kwargs): pass
```

Place it under `MODULEPATHS["PROCESSOR_MODULE_PATH"]` and reference it in a scene as
`["my_processor_module:MyProcessor", {"step": 2}]`.

The four docstring sections (`Involved components`, `Related processors`, `What if this processor is
disabled?`, `Where should the processor be planned?`) are the repo convention and genuinely load-
bearing: a scene author reads *where should it be planned* to know where in the `processors` list it
goes. Keep them filled in.

## Execution throttling

`super().process()` increments `cycle` and raises `SkipProcessorExecution` when
`cycle % exec_cycle_step != 0`. `exec_cycle_step` comes from the scene param `step` (default 1).

**Every processor must catch `SkipProcessorExecution` itself:**

```python
try:
    super().process(*args, **kwargs)
except SkipProcessorExecution:
    return
```

`World._process` does **not** catch it. An escaping exception aborts every remaining processor in
the group for that frame — a throttled processor that forgets the `try` silently disables everything
scheduled after it on 4 out of 5 frames. This is the single most common processor bug in this engine.

Typical uses of `step` in shipped scenes:

```jsonc
["sensor_system.generate_entities_in_sight_processor:GenerateEntitiesInSightProcessor", {"step": 100}]
["position_system.perform_check_on_target_position_processor:PerformCheckOnTargetPositionProcessor", {"step": 1000}]
```

Line-of-sight and win-condition checks do not need to run at 250 fps.

Because `cycle` counts only frames on which `process()` was *called*, a processor that lives in a
non-active group does not advance its counter — throttling is per-group-activity, not wall clock.
`self.cycle` is also the conventional prefix in log lines (`logger.debug(f'({self.cycle}) - ...')`).

## Groups and priority

Processors live in named groups (`defaultdict(list)`), and one call to `World.process()` runs exactly
one group. In a scene file:

```jsonc
"processors": [
    ["render_system.perform_render_map_processor:PerformRenderMapProcessor", {}],            // default group
    ["inventory", "render_system.perform_render_inventory_processor:...", {}]                // 'inventory' group
]
```

A 2-element entry means the `default` group; a 3-element entry names the group first
(`ecs_manager.create_processor`: `proc_group = 'default' if len(processor_def) == 2 else
processor_def[0]`).

Which group runs is the **state module's** decision.
`example_game/core/states/game.py` toggles a module global on the pause key:

```python
proc_group_id = 'pause' if proc_group_id == 'default' else 'default'
...
engine.ecs_manager.process(proc_group_id=proc_group_id, events=..., keys=..., dt=..., debug=...)
```

So "pause" is a group containing only the render processors. Same mechanism for an inventory overlay.

**Priority**: `add_processor(instance, group, priority=0)` sorts each group descending, so **higher
number runs first**. Nothing in the scene format currently sets priority — every registration uses
the default 0, and ordering is therefore **the order of the `processors` list** (Python's sort is
stable). Treat the list order as the schedule.

## `PREREQ` dependency declarations

A processor class may declare a `json_logic` expression naming processors it needs:

```python
PREREQ = ['allOf',
          'command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor']
```

`ecs_manager.check_processor` evaluates it with `check_proc_in_world` as the value function, which
resolves each string to a class and asks `_world.get_processor(cls)`. The literal string `'TRUE'`
(case-insensitive) always passes — used to state an optional prerequisite explicitly for
readability.

Behaviour on failure: `create_processor` logs an error and raises `ValueError`, aborting scene
loading. An absent or empty `PREREQ` passes trivially (`AttributeError` → `return True`).

In practice every shipped processor's `PREREQ` is empty or commented out, so this is a working but
unused facility. It is the right place to encode "this needs the command system" once someone starts
using it.

Because `get_processor` matches with `type(p) == T`, a `PREREQ` naming a base class is not satisfied
by a subclass.

## Dependency injection

Declare engine callables as `__init__` parameters and `ecs_manager` matches them **by name** against
the `game_functions` dict, then overlays the scene's params dict:

```python
def __init__(self, FNC_PROCESS_COMMANDS, REF_ECS_MNG, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.game_commands_handler = FNC_PROCESS_COMMANDS
    self.ecs_mng = REF_ECS_MNG
```

A misspelled name is **silently not injected**. Full key table:
[../core/managers.md §game_functions](../core/managers.md#the-game_functions-wiring-table).

Always call `super().__init__(*args, **kwargs)` first so `step` is picked up.

## What `process()` receives

`ecs_manager.process` always passes four keywords: `events`, `keys`, `dt`, `debug`. Read them from
`kwargs` (or declare them, but then also keep `**kwargs`):

```python
keys   = kwargs.get('keys', [])
events = kwargs.get('events', [])
dt     = kwargs.get('dt')          # milliseconds
```

`dt` is **milliseconds**. Movement code divides by 1000 where it wants seconds.

## The generate/perform/remove idiom

Processor names in this engine encode their phase, and the naming is a scheduling contract:

| Prefix | Role |
|--------|------|
| `Generate…` | Detect a condition, add a flag component or enqueue an event/command |
| `Perform…` | Consume the flag and apply the effect |
| `Remove…` | Strip the flag so the next frame starts clean |

A frame is therefore assembled in the scene file roughly as:

```
Remove* (previous frame's flags)  →  Generate*  →  Perform*  →  render  →  events
```

Shipped scenes vary: `sokoban.jsonc` puts the `Remove*` processors at the **end** of the list, while
the 12_ai scenes put them at the **start**. Both work — what matters is that a flag lives exactly one
frame-span between its producer and its `Remove*`. Getting this wrong produces the classic symptom
of an action firing twice or never.

The 22 processor systems and their contents are inventoried in
[../reference/index.md §Processors](../reference/index.md#processors).

## Related

- [components.md](components.md) — flag components and the naming scheme.
- [../core/managers.md](../core/managers.md) — dependency injection.
- [../authoring/scene-format.md §processors](../authoring/scene-format.md#processors) — the JSON form.
- [world.md](world.md) — the query API to use inside `process()`.
