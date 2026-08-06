# Simulation / Render Frequency Separation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make pgrpg's game speed independent of both machine performance and `TILE_RES_PX`, and make command recordings replay exactly on any machine.

**Architecture:** Split the single frame clock into two. The simulation advances in fixed chunks of `1000 / GAME["SIM_HZ"]` ms (a pure `plan_steps` accumulator decides how many chunks per real frame); rendering happens once per real frame and interpolates between the two most recent simulation states. Processors declare which stage they belong to via a `Processor.STAGE` class attribute, so no scene file changes. Separately, `Movable.velocity` is redefined from pixels/second to tiles/second and converted through `TILE_RES_PX`.

**Tech Stack:** Python 3.9+, pygame, pytest, a modified esper 1.3 fork (`pgrpg/core/ecs`), JSON-with-comments (`.jsonc`) data files.

**Spec:** `docs/superpowers/specs/2026-08-03-sim-render-frequency-separation-design.md`
**Issue:** [#74](https://github.com/xdoko01/pgRPG/issues/74)

## Global Constraints

- **Never run `git commit` or `git push`.** `CLAUDE.md` Hard Rule 1 — the repository owner commits. Every task ends with a **Checkpoint** step that lists changed files for the owner to review. This deliberately replaces the "Commit" step the writing-plans skill normally prescribes.
- **Never hardcode a pixel size** for a sprite, tile, cull margin or UI slot. Read `GAME["TILE_RES_PX"]` or derive from it (`CLAUDE.md` Hard Rule 2).
- **Every Processor must catch `SkipProcessorExecution` itself.** `World._process` does not catch it, so an escaping exception aborts every later processor in the group for that frame (Hard Rule 3).
- **Components use `__slots__`** (Hard Rule 4). Declare every new attribute.
- **Managers are modules, not classes.** Call their functions; never instantiate (Hard Rule 5).
- **Update the knowledge base in the same change** as any source change that alters behaviour it describes (Hard Rule 6, `kb/RULES.md` Rule 12). Task 12 collects this.
- **Run everything from the repository root.** `FILEPATHS.GAME_PATH` is relative and `pgrpg/core/config/defaults.jsonc` is a hardcoded relative path.
- Test command: `pytest tests/` — **194 tests currently pass on `master`; that number must never regress.** (`CLAUDE.md` still says 186; it is stale, verified 2026-08-06. Correcting it is part of Task 12.)
- Design priority: **clarity and readability over performance.**
- Do not use `experiments/` as a reference (Hard Rule 7).

## File Structure

**New files**

| File | Responsibility |
|---|---|
| `pgrpg/core/timestep.py` | Pure fixed-timestep accumulator arithmetic. No pygame import. |
| `tests/core/test_timestep.py` | Unit tests for `plan_steps`. |
| `tests/core/ecs/test_processor_stages.py` | `STAGE` classification and stage-scoped dispatch. |
| `tests/example_game/test_movable.py` | Tiles→pixels conversion, `reinit()`, legacy guard. |
| `tests/example_game/test_movement_scaling.py` | Same tiles/second at 32/64/96 px. |
| `tests/example_game/test_movement_determinism.py` | Jittery vs steady real frame times produce identical traces. |
| `tests/example_game/test_movement_acceleration.py` | Acceleration integrates over time, not frames. |
| `tests/example_game/test_position_interpolation.py` | `alpha` endpoints; `prevx` survives collision scratch writes. |
| `example_game/core/processors/gui_system/perform_gui_draw.py` | Render half of the split GUI processor. |
| `pgrpg/utils/migrate_velocity_to_tiles.py` | One-shot data migration script. |
| `docs/superpowers/plans/2026-08-06-baseline-measurements.md` | Phase 0 measurements (Task 1 output). |

**Modified files**

| File | Change |
|---|---|
| `pgrpg/core/config/defaults.jsonc` | Add `GAME["SIM_HZ"]`, `GAME["MAX_CATCHUP_STEPS"]`. |
| `example_game/config.jsonc` | `MAX_FPS: 1000` → `60`. |
| `pgrpg/core/ecs/__init__.py` | `Processor.STAGE`; `World._processors` keyed by `(group, stage)`. |
| `pgrpg/core/managers/ecs_manager.py` | Pass `stage` through; fix group logging. |
| `pgrpg/core/main.py` | The two-clock loop. |
| `example_game/core/states/game.py` | `run()` becomes sim-only; add `run_render()`; snapshot positions. |
| `example_game/core/components/movable.py` | Tiles/second; `reinit()`; legacy guard. |
| `example_game/core/components/position.py` | `prevx`/`prevy`/`prevmap` + `snapshot()`. |
| `example_game/core/processors/movement_system/perform_movement_processor.py` | `accelerate * dt`; tile-relative clamp; `dt` rebind bug. |
| `example_game/core/processors/gui_system/perform_gui_press.py` | Drop the rendering half. |
| `example_game/core/processors/teleport_system/perform_teleportation_processor.py` | Snapshot after teleport. |
| `example_game/core/processors/render_system/*.py` (14 files) | `STAGE = 'render'`; interpolated positions where relevant. |
| `example_game/core/processors/functions.py` | `interp_xy()` helper. |
| `example_game/core/schemas/components/movable.schema.json` | `integer` → `number`. |
| `example_game/resources/**/*.jsonc` | Migrated `velocity` / `accelerate` values. |
| `.claude/kb/**` | Rule 12 updates. |

---

### Task 1: Baseline measurement and golden movement trace

Establishes the before/after evidence. The spec's claim "speed at 64 px is unchanged" must be *verified*, not argued from arithmetic, and the §5.5 pathfinding multiplier comes from the measured frame rate.

**Files:**
- Create: `docs/superpowers/plans/2026-08-06-baseline-measurements.md`
- Create: `tests/example_game/test_movement_golden_trace.py`

**Interfaces:**
- Produces: `tests/example_game/test_movement_golden_trace.py::test_golden_trace_at_64px` — the reference assertion later tasks must keep passing unchanged. Task 8 edits exactly one line of it (the authored unit) and no assertion. Later tasks define their own local entity-building helpers rather than importing from here, so each test file stays readable on its own.

- [ ] **Step 1: Measure the current frame rate and processor cost**

Set `"TIMED": true` in the `pgrpg` section of `example_game/config.jsonc`, then run each scene, let it settle ~10 seconds, open the dev console with F9 and run `proc_perf`:

```bash
python example_game/game.py -f tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear.jsonc
python example_game/game.py -f games/kill_all/kill_all_level01.jsonc
```

Record for each scene: the on-screen FPS figure, and the `proc_perf` table.

- [ ] **Step 2: Write up the baseline**

Create `docs/superpowers/plans/2026-08-06-baseline-measurements.md` containing, per scene: measured FPS; total cumulative ms in `render_system.*` processors; total in all other processors; and the computed ratio `measured_fps / 60`. That ratio is the expected sim-work reduction and the multiplier for the pathfinding budget in Task 11.

Revert `"TIMED"` to `false` afterwards — it adds a `pygame.time.get_ticks()` pair per processor per cycle.

- [ ] **Step 3: Write the golden-trace test**

This test must pass **before and after** the whole change, which is the point. It drives the movement processor directly with a fixed `dt`, so it does not depend on the loop.

```python
"""A reference movement trace captured before the fixed-timestep change.

At TILE_RES_PX 64 the migration in Task 8 converts every velocity by an exact
power-of-two division, so movement must remain numerically identical. This
test is the evidence for that claim: it is written against the pre-change code
and must still pass after Task 8.
"""

import pytest

import pgrpg.core.config as config
from pgrpg.core.ecs import World
from core.components.position import Position
from core.components.movable import Movable
from core.components.flag_do_move import FlagDoMove
from core.processors.movement_system.perform_movement_processor import PerformMovementProcessor

STEP_MS = 1000 / 60
STEPS = 10


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def build_moving_entity(world, velocity, accelerate=0):
    """Create an entity at tile (0,0) moving right at `velocity`.

    `velocity` is in whatever unit Movable currently accepts: pixels/second
    before Task 6, tiles/second after. Callers convert.
    """
    return world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=velocity, accelerate=accelerate),
        FlagDoMove(moves=["right"]),
    )


def run_trace(world, entity, steps=STEPS, step_ms=STEP_MS):
    """Process `steps` fixed steps, returning the position after each."""
    proc = PerformMovementProcessor()
    proc.world = world
    trace = []
    for _ in range(steps):
        world.add_component(entity, FlagDoMove(moves=["right"]))
        proc.process(dt=step_ms)
        pos = world.component_for_entity(entity, Position)
        trace.append((pos.x, pos.y))
    return trace


def test_golden_trace_at_64px(tile_res):
    """velocity 100 px/s at 64 px, 60 Hz, 10 steps: 1.5625 tiles/s."""
    tile_res(64)
    world = World()
    # Task 8 replaces `100` with `100 / 64` here — the trace must not change.
    entity = build_moving_entity(world, velocity=100)

    trace = run_trace(world, entity)

    assert trace[0] == pytest.approx((100 * STEP_MS / 1000, 0.0))
    assert trace[-1] == pytest.approx((100 * STEPS * STEP_MS / 1000, 0.0))
    assert len(trace) == STEPS
```

- [ ] **Step 4: Run the golden-trace test against unmodified code**

Run: `pytest tests/example_game/test_movement_golden_trace.py -v`
Expected: **PASS**. If it fails, the harness is wrong, not the engine — fix the harness before continuing. In particular `FlagDoMove` is consumed each cycle by `RemoveFlagDoMoveProcessor` at runtime, which is why the helper re-adds it per step.

- [ ] **Step 5: Confirm the full suite is green**

Run: `pytest tests/`
Expected: all 194 existing tests pass, plus the 1 new test — 195 total. **Record the exact number printed.** Later tasks are specified as "the previous total plus N new tests" rather than absolute counts, so this figure is the baseline for every later check.

- [ ] **Step 6: Checkpoint**

Report to the owner: `docs/superpowers/plans/2026-08-06-baseline-measurements.md`, `tests/example_game/test_movement_golden_trace.py`. Include the measured `measured_fps / 60` ratio in the report — Task 11 needs it.

---

### Task 2: `plan_steps` — the fixed-timestep accumulator

**Files:**
- Create: `pgrpg/core/timestep.py`
- Create: `tests/core/test_timestep.py`

**Interfaces:**
- Produces: `plan_steps(accumulator_ms: float, real_dt_ms: float, step_ms: float, max_steps: int) -> tuple[int, float]`, returning `(n_steps, new_accumulator_ms)`. Consumed by Task 5.

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for the fixed-timestep accumulator.

plan_steps is deliberately pure — no pygame, no clock, no globals — so the
loop's timing arithmetic is testable without a display.
"""

import pytest

from pgrpg.core.timestep import plan_steps

STEP_MS = 1000 / 60      # 16.666...
MAX_STEPS = 5


def test_steady_rate_runs_exactly_one_step():
    """A machine hitting the target rate steps once per frame."""
    n, acc = plan_steps(0.0, STEP_MS, STEP_MS, MAX_STEPS)

    assert n == 1
    assert acc == pytest.approx(0.0)


def test_short_frame_banks_time_without_stepping():
    """Half a step of real time runs no step and keeps the remainder."""
    n, acc = plan_steps(0.0, STEP_MS / 2, STEP_MS, MAX_STEPS)

    assert n == 0
    assert acc == pytest.approx(STEP_MS / 2)


def test_banked_time_is_spent_on_a_later_frame():
    """Two half-frames make one whole step."""
    n1, acc1 = plan_steps(0.0, STEP_MS / 2, STEP_MS, MAX_STEPS)
    n2, acc2 = plan_steps(acc1, STEP_MS / 2, STEP_MS, MAX_STEPS)

    assert (n1, n2) == (0, 1)
    assert acc2 == pytest.approx(0.0)


def test_slow_machine_alternates_one_and_two_steps():
    """40 fps against a 60 Hz sim averages 1.5 steps per frame."""
    real_dt = 25.0
    acc = 0.0
    counts = []
    for _ in range(4):
        n, acc = plan_steps(acc, real_dt, STEP_MS, MAX_STEPS)
        counts.append(n)

    assert counts == [1, 2, 1, 2]


def test_long_stall_is_clamped_not_replayed():
    """A 3-second stall must not schedule 180 steps (spiral of death)."""
    n, acc = plan_steps(0.0, 3000.0, STEP_MS, MAX_STEPS)

    assert n == MAX_STEPS
    assert acc == pytest.approx(0.0)


def test_simulated_time_tracks_real_time_without_drift():
    """Over many uneven frames, stepped time stays within one step of real time."""
    frames = [16.4, 17.1, 15.9, 16.8, 16.2] * 200
    acc = 0.0
    total_steps = 0
    for real_dt in frames:
        n, acc = plan_steps(acc, real_dt, STEP_MS, MAX_STEPS)
        total_steps += n

    stepped_ms = total_steps * STEP_MS
    assert abs(stepped_ms - sum(frames)) < STEP_MS


def test_accumulator_never_reaches_a_whole_step():
    """The returned remainder is always strictly less than one step."""
    acc = 0.0
    for real_dt in [0.1, 50.0, 16.0, 999.0, 3.3]:
        _, acc = plan_steps(acc, real_dt, STEP_MS, MAX_STEPS)
        assert 0.0 <= acc < STEP_MS


def test_non_positive_step_is_rejected():
    """A zero or negative step would divide by zero or loop forever."""
    with pytest.raises(ValueError):
        plan_steps(0.0, 16.0, 0.0, MAX_STEPS)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/core/test_timestep.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pgrpg.core.timestep'`.

- [ ] **Step 3: Write the implementation**

```python
"""Fixed-timestep accumulator arithmetic for the main loop.

The game keeps two clocks. Real time is a property of the hardware — how often
this machine can draw a frame. Simulated time is a property of the game — it
advances only in constant chunks of ``1000 / GAME["SIM_HZ"]`` milliseconds.
This module owns the arithmetic that converts the first into the second.

Deliberately free of pygame and of any global state, so the loop's timing can
be unit-tested without a display. See
``.claude/kb/core/bootstrap-and-loop.md``.
"""

__all__ = ['plan_steps']


def plan_steps(accumulator_ms: float,
               real_dt_ms: float,
               step_ms: float,
               max_steps: int) -> tuple[int, float]:
    """Decide how many fixed simulation steps this real frame should run.

    The accumulator is a bank of unspent real time. Real time arrives in
    uneven amounts; it is withdrawn only in whole ``step_ms`` units, and the
    remainder carries to the next frame. Over any interval, simulated time
    therefore tracks real time without drift.

    ``real_dt_ms`` is clamped to ``max_steps * step_ms`` *before* being
    banked. This is what prevents the spiral of death: after a long stall
    (scene load, breakpoint, window drag) an unclamped loop would schedule
    hundreds of steps, each costing time, enlarging the next ``real_dt_ms``
    and scheduling still more. Clamping discards simulated time instead —
    correct, because the player was not playing, and the alternatives are a
    frozen game or an entity teleporting across the map.

    Args:
        accumulator_ms: Unspent real time carried from the previous frame.
            Always less than ``step_ms``.
        real_dt_ms: Real milliseconds elapsed since the previous frame.
        step_ms: Length of one simulation step in milliseconds.
        max_steps: Most steps a single frame may run.

    Returns:
        Tuple of (steps to run this frame, accumulator for the next frame).
        The returned accumulator is always in ``[0, step_ms)``.

    Raises:
        ValueError: If ``step_ms`` is not positive.

    Tests:
        >>> n, acc = plan_steps(0.0, 1000 / 60, 1000 / 60, 5)
        >>> n
        1
        >>> round(acc, 9)
        0.0
        >>> plan_steps(0.0, 3000.0, 1000 / 60, 5)[0]   # a 3-second stall
        5
    """
    if step_ms <= 0:
        raise ValueError(f'step_ms must be positive, got {step_ms}.')

    # Clamp before banking — see the spiral-of-death note above.
    budget_ms = accumulator_ms + min(real_dt_ms, max_steps * step_ms)

    steps = int(budget_ms // step_ms)

    # Defensive: a caller passing an over-large accumulator cannot exceed the cap.
    steps = min(steps, max_steps)

    return steps, budget_ms - steps * step_ms


if __name__ == '__main__':
    import doctest
    doctest.testmod()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/core/test_timestep.py -v`
Expected: 8 passed.

- [ ] **Step 5: Run the doctests and the full suite**

Run: `python -m pgrpg.core.timestep -v` then `pytest tests/`
Expected: doctests pass; the Task 1 total plus 8.

- [ ] **Step 6: Add the configuration keys**

In `pgrpg/core/config/defaults.jsonc`, inside the `GAME` section, after `"TILE_RES_PX": 64`:

```jsonc
		"TILE_RES_PX": 64,

		// Simulation steps per second — the fixed timestep. The simulation
		// advances only in chunks of 1000/SIM_HZ ms, so game speed is a
		// property of the game rather than of the machine's frame rate.
		// Rendering rate is separate: see DISPLAY.MAX_FPS.
		"SIM_HZ": 60,

		// Most simulation steps one real frame may run while catching up.
		// Caps the work a long stall can schedule; simulated time beyond the
		// cap is discarded rather than replayed. See pgrpg/core/timestep.py.
		"MAX_CATCHUP_STEPS": 5
```

Mind the trailing comma on `"TILE_RES_PX": 64` — it is currently the last key in `GAME`.

- [ ] **Step 7: Verify the config parses**

Run: `pytest tests/core/config/ -v`
Expected: PASS. The config merge is exercised there; a `.jsonc` syntax error surfaces immediately.

- [ ] **Step 8: Checkpoint**

Report: `pgrpg/core/timestep.py`, `tests/core/test_timestep.py`, `pgrpg/core/config/defaults.jsonc`.

---

### Task 3: `Processor.STAGE` and stage-scoped processor groups

**Files:**
- Modify: `pgrpg/core/ecs/__init__.py` (`Processor` class ~line 66; `World.add_processor:159`, `remove_processor:177`, `clear_processors:190`, `get_processor:197`, `_process:545`, `_timed_process:550`, `process:567`, `_finalize:578`, `finalize_group:586`, `finalize:591`)
- Modify: `pgrpg/core/managers/ecs_manager.py` (`process:60`, `load_processor:88`)
- Create: `tests/core/ecs/test_processor_stages.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `Processor.STAGE: str = 'sim'` — class attribute, overridden to `'render'` by render processors.
  - `World._processors` keyed by `tuple[str, str]` = `(proc_group_id, stage)`.
  - `World.process(proc_group_id='default', stage='sim', *args, **kwargs)`.
  - `World.get_processor(processor_type, proc_group_id=None, stage=None)` — `None` means "any".
  - `ecs_manager.process(proc_group_id, stage, events, keys, dt, debug, **kwargs)`.

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for sim/render stage classification of processors.

The engine already supported named processor groups (the 'pause' group used by
seven scenes). Stages are an orthogonal axis: a processor declares STAGE on its
class, so the sim/render split needs no scene-file changes.
"""

from pgrpg.core.ecs import World, Component, Processor, SkipProcessorExecution


class Counter(Component):
    __slots__ = ['sim', 'render']

    def __init__(self):
        self.sim = 0
        self.render = 0


class SimProcessor(Processor):
    """Default STAGE — no declaration needed."""

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        for _, counter in self.world.get_component(Counter):
            counter.sim += 1


class RenderProcessor(Processor):
    STAGE = 'render'

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        for _, counter in self.world.get_component(Counter):
            counter.render += 1


def test_stage_defaults_to_sim():
    """Every existing processor must keep working without declaring a stage."""
    assert Processor.STAGE == 'sim'
    assert SimProcessor().STAGE == 'sim'


def test_processors_are_grouped_by_group_and_stage():
    world = World()
    world.add_processor(SimProcessor())
    world.add_processor(RenderProcessor())

    assert ('default', 'sim') in world._processors
    assert ('default', 'render') in world._processors
    assert len(world._processors[('default', 'sim')]) == 1
    assert len(world._processors[('default', 'render')]) == 1


def test_running_one_stage_does_not_run_the_other():
    world = World()
    world.add_processor(SimProcessor())
    world.add_processor(RenderProcessor())
    entity = world.create_entity(Counter())

    world.process(stage='sim')
    world.process(stage='sim')
    world.process(stage='render')

    counter = world.component_for_entity(entity, Counter)
    assert (counter.sim, counter.render) == (2, 1)


def test_stage_is_orthogonal_to_the_scene_authored_group():
    """A scene may put a render processor in the 'pause' group."""
    world = World()
    world.add_processor(RenderProcessor(), proc_group_id='pause')
    entity = world.create_entity(Counter())

    world.process(proc_group_id='default', stage='render')
    assert world.component_for_entity(entity, Counter).render == 0

    world.process(proc_group_id='pause', stage='render')
    assert world.component_for_entity(entity, Counter).render == 1


def test_get_processor_searches_every_group_and_stage_by_default():
    """PREREQ checks call get_processor with no group; they must still resolve.

    Before stages existed this only searched 'default', so a prerequisite
    registered into 'pause' was invisible. Searching everything by default
    fixes that latent bug too.
    """
    world = World()
    world.add_processor(RenderProcessor(), proc_group_id='pause')

    assert world.get_processor(RenderProcessor) is not None
    assert world.get_processor(RenderProcessor, proc_group_id='pause') is not None
    assert world.get_processor(RenderProcessor, proc_group_id='default') is None


def test_clear_processors_empties_every_stage():
    world = World()
    world.add_processor(SimProcessor())
    world.add_processor(RenderProcessor())

    world.clear_processors()

    assert all(not procs for procs in world._processors.values())


def test_finalize_reaches_every_stage():
    calls = []

    class FinalizingRender(Processor):
        STAGE = 'render'

        def process(self, *args, **kwargs):
            pass

        def finalize(self, *args, **kwargs):
            calls.append('render')

    class FinalizingSim(Processor):
        def process(self, *args, **kwargs):
            pass

        def finalize(self, *args, **kwargs):
            calls.append('sim')

    world = World()
    world.add_processor(FinalizingSim())
    world.add_processor(FinalizingRender())

    world.finalize()

    assert sorted(calls) == ['render', 'sim']
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/core/ecs/test_processor_stages.py -v`
Expected: FAIL — `AttributeError: type object 'Processor' has no attribute 'STAGE'`.

- [ ] **Step 3: Add `STAGE` to `Processor`**

In `pgrpg/core/ecs/__init__.py`, in the `Processor` class body alongside `world`, `cycle`, `exec_cycle_step`:

```python
    world = None
    cycle = None # Added by xdoko01 to note the cycle of processor for debug reasons
    exec_cycle_step = None # Added by xdoko01 to note that the process fnc should be called every exec_cycle, ie. not every cycle

    # Which of the two clocks drives this processor. 'sim' processors run on
    # the fixed timestep; 'render' processors run once per real frame and may
    # read the interpolation factor from kwargs['alpha']. Classification is a
    # property of the processor, not of the scene that lists it, so scene
    # files never mention it. See .claude/kb/ecs/processors.md.
    STAGE = 'sim'
```

- [ ] **Step 4: Key the processor registry by (group, stage)**

Replace `World.add_processor`, `remove_processor`, `get_processor` and add a key helper:

```python
    def _group_keys(self, proc_group_id: str=None, stage: str=None) -> list:
        """Return registry keys matching a group and/or stage.

        ``None`` means "any", so ``_group_keys()`` returns every key.
        """
        return [key for key in self._processors
                if (proc_group_id is None or key[0] == proc_group_id)
                and (stage is None or key[1] == stage)]

    def add_processor(self, processor_instance: Processor, proc_group_id: str='default', priority=0) -> None:
        """Add a Processor instance to the World.

        The processor lands in the group keyed by ``(proc_group_id, STAGE)``,
        where ``STAGE`` comes from the processor's class.

        Args:
            processor_instance: A Processor subclass instance.
            proc_group_id: Group to assign the processor to.
            priority: Higher number means processed first.
        """
        assert issubclass(processor_instance.__class__, Processor)
        processor_instance.priority = priority
        processor_instance.world = self

        key = (proc_group_id, processor_instance.STAGE)
        self._processors[key].append(processor_instance)
        self._processors[key].sort(key=lambda proc: proc.priority, reverse=True)

        logger.debug(f'Processor instance "{processor_instance}" added to the processor group "{key}".')
        logger.debug(f'Processor Group "{key}" now contains the following processors: "{self._processors[key]}".')

    def remove_processor(self, processor_type: Processor, proc_group_id: str='default', stage: str=None) -> None:
        """Remove a Processor from the World by type.

        Args:
            processor_type: The class type of the Processor to remove.
            proc_group_id: Group to remove the processor from.
            stage: Stage to remove from; None means every stage of the group.
        """
        for key in self._group_keys(proc_group_id, stage):
            for processor in self._processors[key].copy():
                if type(processor) == processor_type:
                    processor.world = None
                    self._processors[key].remove(processor)

    def get_processor(self, processor_type: type[Processor], proc_group_id: str=None, stage: str=None) -> Processor:
        """Get a Processor instance by type.

        Args:
            processor_type: The Processor class type to retrieve.
            proc_group_id: Group to search in; None searches every group.
            stage: Stage to search in; None searches every stage.

        Returns:
            The matching Processor instance, or None if not found.
        """
        for key in self._group_keys(proc_group_id, stage):
            for processor in self._processors[key]:
                if type(processor) == processor_type:
                    return processor
```

Note `remove_processor` now iterates a `.copy()`. The original mutated the list it was iterating, which could skip an element when a group held two instances of one type.

- [ ] **Step 5: Route dispatch and finalize through the stage**

Replace `_process`, `_timed_process`, `process`, `_finalize`, `finalize_group`, `finalize`:

```python
    def _process(self, proc_group_id: str='default', stage: str='sim', *args, **kwargs):

        for processor in self._processors[(proc_group_id, stage)]:
            processor.process(*args, **kwargs)

    def _timed_process(self, proc_group_id: str='default', stage: str='sim', *args, **kwargs):
        """Track Processor execution time for benchmarking."""

        for processor in self._processors[(proc_group_id, stage)]:
            start_time = pygame.time.get_ticks()
            processor.process(*args, **kwargs)
            process_time = pygame.time.get_ticks() - start_time
            self.process_times[processor.__class__.__name__] += process_time # cumulate the process times in ms

    def process(self, proc_group_id: str='default', stage: str='sim', *args, **kwargs) -> None:
        """Process one stage of one processor group, in priority order.

        Args:
            proc_group_id: Which processor group to run.
            stage: Which stage of that group to run — 'sim' or 'render'.
            *args: Forwarded to each Processor's ``process()`` method.
            **kwargs: Forwarded to each Processor's ``process()`` method.
        """
        self._clear_dead_entities()
        self._process(proc_group_id, stage, *args, **kwargs)

    def _finalize(self, key: tuple, *args, **kwargs) -> None:
        """Call finalize on all Processors in one registry group."""
        for processor in self._processors[key]:
            try:
                processor.finalize(*args, **kwargs)
            except NotImplementedError:
                raise ValueError(processor)

    def finalize_group(self, proc_group_id: str='default', stage: str=None, *args, **kwargs) -> None:
        """Call finalize on all Processors in a group, across stages by default."""
        for key in self._group_keys(proc_group_id, stage):
            self._finalize(key, *args, **kwargs)

    def finalize(self, *args, **kwargs) -> None:
        """Call finalize on all Processors across all groups and stages."""
        for key in self._group_keys():
            self._finalize(key, *args, **kwargs)
```

`_clear_dead_entities()` still runs on every `process()` call, i.e. once for the sim stage and once for the render stage. That is harmless — it is idempotent when the dead set is empty.

- [ ] **Step 6: Run the stage tests**

Run: `pytest tests/core/ecs/ -v`
Expected: the 7 new tests pass; the existing `test_ecs.py` tests still pass because `stage` defaults to `'sim'` and `MoveProcessor` inherits `STAGE = 'sim'`.

- [ ] **Step 7: Thread `stage` through `ecs_manager`**

In `pgrpg/core/managers/ecs_manager.py`, replace the one-line `process` delegation at line 60:

```python
def process(proc_group_id, stage, events, keys, dt: float, debug: bool, **kwargs):
    """Run one stage of one processor group.

    Args:
        proc_group_id: Scene-authored processor group ('default', 'pause', …).
        stage: 'sim' for fixed-timestep processors, 'render' for per-frame ones.
        **kwargs: Extra values forwarded to processors, e.g. ``alpha``.
    """
    _world.process(proc_group_id=proc_group_id, stage=stage,
                   events=events, keys=keys, dt=dt, debug=debug, **kwargs)
```

And in `load_processor`, fix the log line that indexes the registry with a bare group id:

```python
    # Log all the processors in the processor group
    key = (new_proc_group, new_proc_instance.STAGE)
    logger.info(f'Process group "{key}" now contains following processors "{_world._processors[key]}".')
```

- [ ] **Step 8: Run the full suite**

Run: `pytest tests/`
Expected: the Task 2 total plus 7. Any failure here is almost certainly a caller of `World.process` or `get_processor` that this task missed — search for them:

```bash
grep -rn "\.process(\|get_processor(\|finalize_group(" --include=*.py pgrpg example_game tests
```

- [ ] **Step 9: Checkpoint**

Report: `pgrpg/core/ecs/__init__.py`, `pgrpg/core/managers/ecs_manager.py`, `tests/core/ecs/test_processor_stages.py`.

---

### Task 4: Classify render processors and split the GUI processor

**Files:**
- Modify: all 14 `example_game/core/processors/render_system/*.py` processor classes
- Modify: `example_game/core/processors/gui_system/perform_gui_press.py:106-107`
- Create: `example_game/core/processors/gui_system/perform_gui_draw.py`
- Modify: `example_game/core/processors/gui_system/__init__.py`

**Interfaces:**
- Consumes: `Processor.STAGE` from Task 3.
- Produces: `PerformGUIDrawProcessor` with `STAGE = 'render'`, exported from `gui_system`.

- [ ] **Step 1: Declare `STAGE = 'render'` on every render processor**

For each of these classes in `example_game/core/processors/render_system/`, add `STAGE = 'render'` immediately above the existing `PREREQ` or `__slots__` declaration:

`generate_render_data_from_parent_processor.py`, `perform_blit_camera_processor.py`, `perform_blit_picture_processor.py`, `perform_clear_camera_processor.py`, `perform_clear_window_processor.py`, `perform_render_armed_ammo_processor.py`, `perform_render_armed_weapon_processor.py`, `perform_render_debug_info_processor.py`, `perform_render_inventory_processor.py`, `perform_render_map_processor.py`, `perform_render_messages_processor.py`, `perform_render_model_processor.py`, `perform_scroll_camera_processor.py`, `perform_scroll_delayed_camera_processor.py`.

Pattern, e.g. in `perform_render_model_processor.py`:

```python
class PerformRenderModelProcessor(Processor):
    ''' Draws the entities in the world.
    ...
    '''

    # Runs once per real frame, not on the fixed timestep.
    STAGE = 'render'

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []
```

Verify none were missed:

```bash
grep -rLn "STAGE = 'render'" --include=*_processor.py example_game/core/processors/render_system/
```

- [ ] **Step 2: Create the render half of the GUI processor**

`perform_gui_press.py` currently does two jobs in one `process()`: it consumes discrete `UI_BUTTON_PRESSED` events and emits commands, an event and a flag (simulation), then calls `gui_manager.update(dt)` and `gui_manager.draw_gui()` (rendering, lines 106-107). Create `example_game/core/processors/gui_system/perform_gui_draw.py`:

```python
__all__ = ['PerformGUIDrawProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

import pgrpg.core.config.gui as gui_manager # for the pygame_gui manager

# Logger init
logger = logging.getLogger(__name__)

class PerformGUIDrawProcessor(Processor):
    ''' Advances the pygame_gui manager and draws the GUI.

    Split out of PerformGUIPressProcessor, which handled button presses and
    drawing in the same process() call. Presses are simulation work (they emit
    commands, events and flags); advancing and drawing the GUI is rendering.
    The two now run on their own clocks.

    Involved components:
        -   None

    Related processors:
        -   PerformGUIPressProcessor - handles the presses this draws the result of

    What if this processor is disabled?
        -   GUI widgets will not be drawn or animated

    Where the processor should be planned?
        -   after PerformGUIPressProcessor - so a press is reflected the same frame
    '''

    # Runs once per real frame, not on the fixed timestep.
    STAGE = 'render'

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformGUIDrawProcessor processor.
        '''
        super().__init__(*args, **kwargs)

    def process(self, *args, **kwargs):
        ''' Advance the GUI manager by the real frame time and draw it.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Real frame time in ms - the GUI animates on the render clock, not the
        # fixed simulation timestep.
        dt = kwargs['dt']

        gui_manager.update(dt)
        gui_manager.draw_gui()

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components (none)
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game.
        '''
        pass
```

- [ ] **Step 3: Remove the rendering half from the press processor**

In `example_game/core/processors/gui_system/perform_gui_press.py`, delete the `dt` read (line 74) and the two trailing calls (lines 106-107):

```python
        # Extract events and keys from parameter kwargs
        # currently only keys are used but events might be usefull as well for mouse later
        events = kwargs.get('events', [])
```

and end the loop with only:

```python
                gui_manager.process_events(event)
```

The `gui_manager.update(dt)` / `gui_manager.draw_gui()` pair now lives in `PerformGUIDrawProcessor`.

- [ ] **Step 4: Export the new processor**

Match the existing style of `example_game/core/processors/gui_system/__init__.py` — inspect it first, then add the equivalent of:

```python
from .perform_gui_draw import PerformGUIDrawProcessor
```

- [ ] **Step 5: Register the new processor in the scenes that use the GUI**

Find the scenes listing the press processor:

```bash
grep -rn "PerformGUIPressProcessor\|perform_gui_press" --include=*.jsonc example_game/resources
```

In each, add the draw processor immediately after the press processor, e.g.:

```jsonc
		["gui_system.perform_gui_press:PerformGUIPressProcessor", {}],
		["gui_system.perform_gui_draw:PerformGUIDrawProcessor", {}],
```

This is the one place scene data must change, because a processor that does not exist in a scene's list is never instantiated. It is additive — no existing entry is modified.

- [ ] **Step 6: Verify the classification and run the suite**

Run: `pytest tests/`
Expected: the Task 3 total, unchanged — no behaviour change yet, since Task 5 has not split the loop, so only the `'sim'` stage runs and render processors are simply not called. **This means the game will render nothing if launched between Task 4 and Task 5.** That is expected; do not launch it here.

Run: `pytest tests/example_game/test_resource_schemas.py -v`
Expected: PASS — confirms the scene edits in Step 5 are still schema-valid.

- [ ] **Step 7: Checkpoint**

Report: the 14 render-processor files, `perform_gui_press.py`, `perform_gui_draw.py`, `gui_system/__init__.py`, and the scene files touched in Step 5.

---

### Task 5: The two-clock main loop

**Files:**
- Modify: `pgrpg/core/main.py:107-148`
- Modify: `example_game/core/states/game.py:75-117`
- Modify: `example_game/config.jsonc:10`

**Interfaces:**
- Consumes: `plan_steps` (Task 2), `ecs_manager.process(..., stage=...)` (Task 3), `STAGE` classification (Task 4).
- Produces: an optional `run_render(dt, alpha)` on state modules. `main.run()` calls it via `getattr(module, 'run_render', None)`; modules without it are unaffected.

**Design note — only `game.py` needs splitting.** A grep confirms `ecs_manager.process` is called from exactly one state module, `game.py:114`. The other eight states are menus that draw directly inside `run()`. So `run()` keeps its name and becomes the *simulation* entry point for every state, and `run_render` is **opt-in**. This refines spec §3.5, which assumed all nine modules would split; the behaviour is identical and the churn is eight files smaller. Consequence: for a state with no `run_render`, nothing draws on a frame where `n == 0`, so the loop must not flip a stale buffer — hence the `drew` flag below.

- [ ] **Step 1: Rewrite `main.run()`**

Replace the body of `run()` in `pgrpg/core/main.py` (currently lines 107-148):

```python
def run():
    """Run the main game loop until the process exits.

    The loop keeps two clocks. The simulation advances in fixed steps of
    ``1000 / GAME["SIM_HZ"]`` ms — ``plan_steps`` decides how many steps one
    real frame is worth — so game speed does not depend on the machine.
    Rendering happens once per real frame, capped by ``DISPLAY["MAX_FPS"]``,
    and receives ``alpha``, the fraction of the way from the previous
    simulation state to the current one, for interpolation.

    See .claude/kb/core/bootstrap-and-loop.md.
    """

    sim_step_ms = 1000 / GAME["SIM_HZ"]
    max_catchup = GAME["MAX_CATCHUP_STEPS"]

    # Unspent real time carried between frames, always < sim_step_ms.
    accumulator = 0.0

    # Seed the first frame with exactly one step's worth of time. Measuring it
    # instead would include engine start-up and produce one huge first step.
    gui_manager.clock.tick(DISPLAY["MAX_FPS"])
    real_dt = sim_step_ms

    while True:

        # Read the keys pressed, mouse, win resize etc.
        key_events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()

        state_module = state_manager.state_modules[state_manager.state]

        # --- simulation: zero or more fixed steps ---------------------------
        steps, accumulator = plan_steps(accumulator, real_dt, sim_step_ms, max_catchup)

        # Discrete events belong to the first sub-step only. key_pressed is a
        # *state* ("right arrow is down now") and applies to every sub-step,
        # but a KEYDOWN is a one-off fact: delivering it twice would toggle
        # pause twice, cancelling itself, or fire two attacks from one press —
        # a bug that would only ever appear on a slow machine.
        step_events = key_events

        for _ in range(steps):
            next_state = state_module.run(
                key_events=step_events,
                key_pressed=key_pressed,
                dt=sim_step_ms
            )
            step_events = ()

            if next_state is not state_manager.state:
                state_manager.change_state(next_state)
                state_module = state_manager.state_modules[state_manager.state]
                break

        # --- rendering: once per real frame --------------------------------
        # States that separate the two stages expose run_render; menu states
        # draw inside run() instead and simply do not define it.
        render_fnc = getattr(state_module, 'run_render', None)

        if render_fnc is not None:
            render_fnc(dt=real_dt, alpha=accumulator / sim_step_ms)
            drew = True
        else:
            # Without run_render, drawing happened inside run() — so this frame
            # only has fresh pixels if at least one step ran. Flipping an
            # untouched back buffer would flicker.
            drew = steps > 0

        # Notify console - regardless of the State - to support animation of the console during the toggle
        cons.update(key_events)
        cons.show(gui_manager.window)

        # Display FPS if SHOW_FPS is enabled in config
        not DISPLAY["SHOW_FPS"] or gui_manager.blit_text("FPS: " + str(int(gui_manager.clock.get_fps())))

        # Flip the frame buffers
        if drew: gui_manager.flip()

        # Get the real time of the frame - this caps rendering only
        real_dt = gui_manager.clock.tick(DISPLAY["MAX_FPS"])
```

Add the imports near the existing `from pgrpg.core.config import DISPLAY`:

```python
from pgrpg.core.config import DISPLAY # for MAX_FPS
from pgrpg.core.config import GAME # for SIM_HZ, MAX_CATCHUP_STEPS
from pgrpg.core.timestep import plan_steps
```

Note the loop no longer wraps `state_module.run(...)` in `state_manager.change_state(...)`. The original called `change_state` unconditionally with `run()`'s return value every frame; the new form calls it only on an actual transition, which is required because `run()` may now be called zero or several times per frame.

- [ ] **Step 2: Split `game.py` into sim and render**

In `example_game/core/states/game.py`, replace the single `ecs_manager.process` call at line 114 and add `run_render`:

```python
### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt, debug: bool=False) -> State:
    '''The simulation step for the given state.

    Called zero or more times per real frame on the fixed timestep - see
    pgrpg.core.main.run and pgrpg/core/timestep.py.
    '''

    # ... existing event handling loop unchanged ...

    # Snapshot every Position before anything moves it, so the render stage can
    # interpolate between the previous step and this one. Done here rather than
    # in a processor because a processor would have to be listed first in all 78
    # scene files to be guaranteed to run before movement.
    for _, position in engine.ecs_manager.get_component(Position):
        position.snapshot()

    # Run the simulation processors
    engine.ecs_manager.process(proc_group_id=proc_group_id, stage='sim',
                               events=key_events, keys=key_pressed, dt=dt, debug=debug)

    # Repeat the cycle next time, if State was not changed by above events
    return State.GAME


### Called once per real frame, after the simulation steps
def run_render(dt, alpha, debug: bool=False) -> None:
    '''Draw the world once per real frame.

    Parameters:
        :param dt: Real milliseconds since the previous frame.
        :param alpha: Fraction of the way from the previous simulation step to
            the current one, in [0, 1). Render processors use it to interpolate
            positions so motion looks smooth between simulation steps.
    '''
    engine.ecs_manager.process(proc_group_id=proc_group_id, stage='render',
                               events=(), keys=None, dt=dt, debug=debug, alpha=alpha)
```

Add the `Position` import to the optional-imports block:

```python
### PUT ALL YOUR OPTIONAL IMPORTS HERE
import pygame
from pgrpg.core import engine
from pgrpg.core.config import KEYS # for K_CONSOLE_TOGGLE, K_SAVE_GAME, K_LOAD_GAME
from core.components.position import Position # for the pre-step position snapshot
```

`Position.snapshot()` does not exist yet — Task 9 adds it. Until then this loop raises `AttributeError`, so **Steps 2–4 of this task must be completed together with Task 9 before launching the game.** Verify by test only until then.

- [ ] **Step 3: Add a temporary no-op `snapshot()` so the loop is testable now**

To keep this task independently verifiable, add the method to `Position` now and give it real behaviour in Task 9:

```python
    def snapshot(self):
        '''Record the position at the start of a simulation step.

        Filled in by the interpolation task; a no-op placeholder keeps the
        main loop runnable in the meantime.
        '''
        pass
```

- [ ] **Step 4: Cap rendering at a sane frame rate**

In `example_game/config.jsonc`, change line 10. `MAX_FPS` now caps *rendering only*, so 1000 would burn CPU and GPU drawing frames no monitor shows:

```jsonc
		"MAX_FPS" : 60,
```

Add a comment above it:

```jsonc
		// Caps rendering only. Simulation rate is GAME.SIM_HZ and is
		// independent of this value. Set at or near the display refresh rate.
		"MAX_FPS" : 60,
```

- [ ] **Step 5: Verify the loop by running the game**

Run: `python example_game/game.py -f tests/01_movements/test_movement_10.jsonc`
Expected: the scene renders, the character moves, the FPS counter reads ~60. Press ESC to reach the main menu, F9 for the console — both must work, proving the `drew` path for menu states and the state-transition break.

Run: `python example_game/game.py -s MAIN_MENU`
Expected: the menu renders and animates without flicker. Flicker here means the `drew` flag is wrong.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests/`
Expected: the Task 3 total, unchanged.

- [ ] **Step 7: Checkpoint**

Report: `pgrpg/core/main.py`, `example_game/core/states/game.py`, `example_game/core/components/position.py`, `example_game/config.jsonc`. Note in the report the FPS figure observed, for comparison against Task 1's baseline.

---

### Task 6: `Movable` in tiles per second

**Files:**
- Modify: `example_game/core/components/movable.py`
- Modify: `example_game/core/schemas/components/movable.schema.json`
- Create: `tests/example_game/test_movable.py`

**Interfaces:**
- Produces:
  - `Movable(velocity=<tiles/s>, accelerate=<tiles/s²>)`.
  - `movable.velocity` / `movable.accelerate` — read/write **pixel** properties (px/s and px/s²), so processors and `FlagAdjustMovement` callables are unchanged.
  - `movable.velocity_tiles` / `movable.accelerate_tiles` — read-only authored values.
  - `movable.reinit()` — recomputes pixels from tiles.
  - `MAX_VELOCITY_TILES = 15.625` — module constant, consumed by Task 7.

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for the Movable component's tile-relative speed.

Speed is a world quantity: an entity's velocity has to mean the same thing
relative to the map at any TILE_RES_PX. Authoring it in tiles per second is
what keeps it in proportion, exactly as Collidable does for extents.
"""

import pytest

import pgrpg.core.config as config
from core.components.movable import Movable, MAX_VELOCITY_TILES


# The stock character speed, as authored against a 64 px tile: 100 px/s.
CHARACTER_TILES_PER_S = 100 / 64


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def test_migrated_value_is_exact_at_64(tile_res):
    """100/64 is a dyadic rational, so it multiplies back to exactly 100."""
    tile_res(64)

    movable = Movable(velocity=CHARACTER_TILES_PER_S)

    assert movable.velocity == 100


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_velocity_scales_with_tile_resolution(tile_res_px, tile_res):
    """The same authored speed is the same fraction of a tile everywhere."""
    tile_res(tile_res_px)

    movable = Movable(velocity=1.5625)

    assert movable.velocity == pytest.approx(1.5625 * tile_res_px)
    assert movable.velocity_tiles == pytest.approx(1.5625)


def test_acceleration_scales_with_tile_resolution(tile_res):
    tile_res(32)

    movable = Movable(velocity=1.5625, accelerate=-2.8125)

    assert movable.accelerate == pytest.approx(-2.8125 * 32)
    assert movable.accelerate_tiles == pytest.approx(-2.8125)


def test_accelerate_defaults_to_zero(tile_res):
    tile_res(64)

    assert Movable(velocity=1.5625).accelerate == 0


def test_writing_pixel_velocity_keeps_tiles_in_sync(tile_res):
    """perform_adjust_movement_processor writes movable.velocity in pixels.

    The tile value must follow, or reinit() would resurrect a stale speed.
    """
    tile_res(64)
    movable = Movable(velocity=1.5625)

    movable.velocity = 320

    assert movable.velocity_tiles == pytest.approx(5.0)


def test_reinit_recomputes_pixels_from_tiles(tile_res):
    """A display reinit must not leave speed at the old resolution."""
    tile_res(64)
    movable = Movable(velocity=1.5625)
    assert movable.velocity == 100

    tile_res(32)
    movable.reinit()

    assert movable.velocity == pytest.approx(50)
    assert movable.velocity_tiles == pytest.approx(1.5625)


def test_stop_and_restore_movement_round_trip(tile_res):
    """stop_movement must not survive a reinit as a resurrected speed."""
    tile_res(64)
    movable = Movable(velocity=1.5625, accelerate=-2.0)

    movable.stop_movement()
    assert (movable.velocity, movable.accelerate) == (0, 0)
    assert movable.velocity_tiles == 0

    movable.restore_movement()
    assert movable.velocity == 100
    assert movable.accelerate_tiles == pytest.approx(-2.0)


def test_legacy_pixel_value_warns(tile_res, caplog):
    """A pre-migration px value is implausible as tiles/second — warn loudly."""
    tile_res(64)

    with caplog.at_level("WARNING"):
        Movable(velocity=100)

    assert "looks like a pre-migration pixel value" in caplog.text
    assert "1.5625" in caplog.text


def test_plausible_value_does_not_warn(tile_res, caplog):
    tile_res(64)

    with caplog.at_level("WARNING"):
        Movable(velocity=7.8125)

    assert caplog.text == ""


def test_non_numeric_velocity_is_rejected(tile_res):
    tile_res(64)

    with pytest.raises(ValueError):
        Movable(velocity="fast")


def test_missing_velocity_is_rejected(tile_res):
    tile_res(64)

    with pytest.raises(ValueError):
        Movable()


def test_max_velocity_constant_matches_the_old_pixel_cap():
    """The old clamp was a hardcoded 1000 px/s at 64 px."""
    assert MAX_VELOCITY_TILES * 64 == 1000
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/example_game/test_movable.py -v`
Expected: FAIL — `ImportError: cannot import name 'MAX_VELOCITY_TILES'`.

- [ ] **Step 3: Rewrite `movable.py`**

```python
''' Module "example_game.core.components.movable" contains
Movable component implemented as a Movable class.

Use 'python -m example_game.core.components.movable -v' to run
module tests.
'''

import logging

import pygame
from pgrpg.core.ecs import Component
from pgrpg.core.config import GAME # for TILE_RES_PX

logger = logging.getLogger(__name__)

# Speed ceiling, in tiles per second. 15.625 tiles/s is 1000 px/s at 64 px,
# which is the hardcoded pixel cap this replaced.
MAX_VELOCITY_TILES = 15.625

# Above this many tiles per second an authored value is far more likely to be a
# pre-migration pixel figure (the smallest shipped value was 50) than a real
# speed (the largest was 7.8125 tiles/s).
LEGACY_VELOCITY_WARN_TILES = 20

class Movable(Component):
    ''' Entity can move.

    Speed is authored in **tiles per second** and acceleration in **tiles per
    second squared**, so an entity covers the same ground relative to the map
    at any GAME["TILE_RES_PX"]. The pixel values processors actually use are
    derived, and kept in sync by the velocity/accelerate properties.

    Used by:
        -   PerformMovementProcessor

    Examples of JSON definition:
        {"type" : "Movable", "params" : {"velocity" : 1.5625}},
        {"type" : "Movable", "params" : {"velocity" : 1.5625, "accelerate" : -2.8125}},

    Tests:
        >>> c = Movable(**{"velocity" : 1.5625, "accelerate" : -2.8125})
        >>> c.velocity_tiles
        1.5625
        >>> c.velocity                      # px/s at the default 64 px tile
        100.0
        >>> c.accelerate
        -180.0
    '''

    __slots__ = ['_velocity_px', '_velocity_tiles', '_accelerate_px', '_accelerate_tiles',
                 '_last_move_time', '_last_velocity', '_last_accelerate']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Movable component.

        Parameters:
            :param velocity: Speed of the movement, in tiles per second (mandatory).
            :type velocity: float

            :param accelerate: Pace of acceleration, in tiles per second squared (optional).
            :type accelerate: float

            :raise: ValueError - in case movement params are not numbers.
        '''
        super().__init__()

        velocity = kwargs.get('velocity')
        accelerate = kwargs.get('accelerate', 0)

        # Assert that the speeds are numbers. Fractions are normal now, so this
        # can no longer require int - the migrated values are all n/64.
        try:
            assert isinstance(velocity, (int, float)) and not isinstance(velocity, bool), \
                f'Movement velocity is not a number for {self.__class__} component.'
            assert isinstance(accelerate, (int, float)) and not isinstance(accelerate, bool), \
                f'Movement acceleration is not a number for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Catch scenes that were never migrated from pixels to tiles. Silently
        # accepting 100 would make the entity 64x too fast.
        if velocity > LEGACY_VELOCITY_WARN_TILES:
            logger.warning(
                f'{self.__class__.__name__} velocity {velocity} tiles/s looks like a '
                f'pre-migration pixel value. Did you mean {velocity / 64} tiles/s?'
            )

        # Setting through the properties derives the pixel values.
        self.velocity = None       # placeholder so the slot exists before use
        self._velocity_tiles = velocity
        self._accelerate_tiles = accelerate
        self.reinit()

        # Intit the last movement time and last velocity
        self._last_move_time = None
        self._last_velocity = None
        self._last_accelerate = None

    @property
    def velocity(self):
        '''Speed in pixels per second - what the movement processor uses.'''
        return self._velocity_px

    @velocity.setter
    def velocity(self, px):
        '''Set the speed in pixels per second, keeping the tile value in sync.

        FlagAdjustMovement callables and stop/restore_movement all write pixels;
        letting the tile value drift would make reinit() resurrect a stale speed.
        '''
        self._velocity_px = px
        self._velocity_tiles = None if px is None else px / GAME["TILE_RES_PX"]

    @property
    def accelerate(self):
        '''Acceleration in pixels per second squared.'''
        return self._accelerate_px

    @accelerate.setter
    def accelerate(self, px):
        self._accelerate_px = px
        self._accelerate_tiles = None if px is None else px / GAME["TILE_RES_PX"]

    @property
    def velocity_tiles(self):
        '''Authored speed, in tiles per second.'''
        return self._velocity_tiles

    @property
    def accelerate_tiles(self):
        '''Authored acceleration, in tiles per second squared.'''
        return self._accelerate_tiles

    def reinit(self):
        ''' Recompute the pixel speeds after a change of TILE_RES_PX.

        Joins Camera and FlagShowInventory as the components that survive a
        config reinit. Without this, a resolution change would leave speed at
        the old pixel scale while the world moved to the new one.
        '''
        tiles_v = self._velocity_tiles
        tiles_a = self._accelerate_tiles

        self._velocity_px = tiles_v * GAME["TILE_RES_PX"]
        self._accelerate_px = tiles_a * GAME["TILE_RES_PX"]

        # Restore the authored values - the assignments above went through the
        # plain attributes, not the setters, so nothing drifted.
        self._velocity_tiles = tiles_v
        self._accelerate_tiles = tiles_a

    def stop_movement(self):
        ''' If some entity needs to freeze temporarily, this function is called
        and the original velocity is stored for later restoration by restore_movement
        function.
        '''

        # Store the original velocity for later restoration
        self._last_velocity = self.velocity
        self._last_accelerate = self.accelerate

        # Set velocity to 0 - through the properties, so the tile values follow
        self.velocity = 0
        self.accelerate = 0

        # Set last movement time
        self._last_move_time = pygame.time.get_ticks()

    def restore_movement(self):
        ''' Restore velocity to the last known value.
        '''

        # Set velocity to the previous value
        self.velocity = self._last_velocity
        self.accelerate = self._last_accelerate

        self._last_velocity = None
        self._last_accelerate = None

        self._last_move_time = pygame.time.get_ticks()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
```

Two notes for the implementer. `self.velocity = None` before setting `_velocity_tiles` exists only to create the `_velocity_px` slot; `reinit()` immediately overwrites it. And `reinit()` assigns the private slots directly rather than via the setters, because the setters derive tiles *from* pixels — using them here would round-trip the authored value through the new resolution and lose it.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/example_game/test_movable.py -v`
Expected: 14 passed (the resolution test is parametrised over 32/64/96).

- [ ] **Step 5: Run the doctests**

Run (from `example_game/`): `python -m core.components.movable -v`
Expected: 3 doctests pass.

- [ ] **Step 6: Widen the schema from integer to number**

In `example_game/core/schemas/components/movable.schema.json` the migrated values are fractional, so `"type": "integer"` would reject every one of them. Update both properties and the examples:

```json
	"examples" : [
		{"type" : "movable:Movable", "params" : {"velocity" : 1.5625}},
		{"type" : "movable:Movable", "params" : {"velocity" : 3.125, "accelerate" : -2.8125}},
		{"type" : "movable:Movable", "params" : {"velocity" : 7.8125, "accelerate" : -2.8125}}
	],
```

```json
				"velocity" : {
					"title": "Velocity",
					"description": "Speed of the movement, in tiles per second. May also be a template variable, since entity and template definitions are parameterised before instantiation.",
					"anyOf": [
						{
							"type": "number",
							"exclusiveMinimum": 0,
							"maximum": 15.625
						},
						{ "$ref": "../definitions.schema.json#/definitions/template_var" }
					]
				},
				"accelerate" : {
					"title": "Acceleration Rate",
					"description": "Pace of acceleration, in tiles per second squared. May also be a template variable, since entity and template definitions are parameterised before instantiation.",
					"default" : 0,
					"anyOf": [
						{ "type": "number" },
						{ "$ref": "../definitions.schema.json#/definitions/template_var" }
					]
				}
```

The `maximum` matches `MAX_VELOCITY_TILES`, so an unmigrated pixel value now fails schema validation as well as warning at runtime — two independent guards.

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/`
Expected: `tests/example_game/test_resource_schemas.py` now **FAILS**, because the shipped scenes still hold pixel values that exceed `maximum: 15.625`. That is correct and expected — Task 8 migrates the data. Every other test passes.

Record the failure count so Task 8 can confirm it returns to zero.

- [ ] **Step 8: Checkpoint**

Report: `example_game/core/components/movable.py`, `example_game/core/schemas/components/movable.schema.json`, `tests/example_game/test_movable.py`. State clearly that `test_resource_schemas.py` is expected to fail until Task 8.

---

### Task 7: Integrate acceleration over time

**Files:**
- Modify: `example_game/core/processors/movement_system/perform_movement_processor.py:74,89-98`
- Modify: `example_game/core/processors/render_system/perform_render_debug_info_processor.py:275`
- Create: `tests/example_game/test_movement_acceleration.py`

**Interfaces:**
- Consumes: `MAX_VELOCITY_TILES` from Task 6.

- [ ] **Step 1: Write the failing tests**

```python
"""Acceleration must integrate over elapsed time, not over frames.

Before this change `movable.velocity += movable.accelerate` ran once per frame
with no dt, so a projectile's deceleration rate was a property of the CPU.
"""

import pytest

import pgrpg.core.config as config
from pgrpg.core.ecs import World
from core.components.position import Position
from core.components.movable import Movable
from core.components.flag_do_move import FlagDoMove
from core.processors.movement_system.perform_movement_processor import PerformMovementProcessor


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def build(world, velocity, accelerate=0):
    return world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=velocity, accelerate=accelerate),
        FlagDoMove(moves=["right"]),
    )


def step(world, proc, entity, dt_ms):
    world.add_component(entity, FlagDoMove(moves=["right"]))
    proc.process(dt=dt_ms)


def test_acceleration_is_independent_of_step_count(tile_res):
    """Two 30 ms steps must reach the same velocity as one 60 ms step."""
    tile_res(64)

    coarse_world = World()
    coarse = build(coarse_world, velocity=7.8125, accelerate=-2.8125)
    proc = PerformMovementProcessor()
    proc.world = coarse_world
    step(coarse_world, proc, coarse, 60)

    fine_world = World()
    fine = build(fine_world, velocity=7.8125, accelerate=-2.8125)
    proc = PerformMovementProcessor()
    proc.world = fine_world
    step(fine_world, proc, fine, 30)
    step(fine_world, proc, fine, 30)

    coarse_v = coarse_world.component_for_entity(coarse, Movable).velocity
    fine_v = fine_world.component_for_entity(fine, Movable).velocity
    assert coarse_v == pytest.approx(fine_v)


def test_deceleration_reaches_zero_in_the_expected_time(tile_res):
    """7.8125 tiles/s decelerating at 2.8125 tiles/s^2 stops in ~2.78 s."""
    tile_res(64)
    world = World()
    entity = build(world, velocity=7.8125, accelerate=-2.8125)
    proc = PerformMovementProcessor()
    proc.world = world

    step_ms = 1000 / 60
    steps = 0
    while world.component_for_entity(entity, Movable).velocity > 0 and steps < 1000:
        step(world, proc, entity, step_ms)
        steps += 1

    elapsed_s = steps * step_ms / 1000
    assert elapsed_s == pytest.approx(7.8125 / 2.8125, rel=0.02)


def test_velocity_is_clamped_in_tile_relative_terms(tile_res):
    """The ceiling must scale with resolution, not sit at a hardcoded 1000 px."""
    tile_res(32)
    world = World()
    entity = build(world, velocity=15.0, accelerate=100.0)
    proc = PerformMovementProcessor()
    proc.world = world

    for _ in range(120):
        step(world, proc, entity, 1000 / 60)

    movable = world.component_for_entity(entity, Movable)
    assert movable.velocity == pytest.approx(15.625 * 32)


def test_velocity_never_goes_negative(tile_res):
    tile_res(64)
    world = World()
    entity = build(world, velocity=1.5625, accelerate=-100.0)
    proc = PerformMovementProcessor()
    proc.world = world

    for _ in range(60):
        step(world, proc, entity, 1000 / 60)

    assert world.component_for_entity(entity, Movable).velocity == 0


def test_dt_off_entity_does_not_leak_into_later_entities(tile_res):
    """A dt_on=False entity must not disable dt scaling for the rest of the frame.

    The original code rebound the loop-local `dt` inside the per-entity loop, so
    once one entity opted out, every entity processed after it in the same frame
    silently moved at dt=1.
    """
    tile_res(64)
    world = World()

    absolute = world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=1.5625),
        FlagDoMove(moves=["right"], dt_on=False),
    )
    normal = world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=1.5625),
        FlagDoMove(moves=["right"]),
    )

    proc = PerformMovementProcessor()
    proc.world = world
    proc.process(dt=1000 / 60)

    # The dt-scaled entity moves 100 px/s for 1/60 s = 1.667 px, not a full 100.
    moved = world.component_for_entity(normal, Position).x
    assert moved == pytest.approx(100 / 60)
    assert world.component_for_entity(absolute, Position).x == pytest.approx(100)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/example_game/test_movement_acceleration.py -v`
Expected: FAIL — `test_acceleration_is_independent_of_step_count`, `test_velocity_is_clamped_in_tile_relative_terms` and `test_dt_off_entity_does_not_leak_into_later_entities` all fail against the current per-frame code.

- [ ] **Step 3: Fix the movement processor**

In `perform_movement_processor.py`, add the import:

```python
from core.components.movable import Movable, MAX_VELOCITY_TILES
```

and the config import for the clamp:

```python
from pgrpg.core.config import GAME # for TILE_RES_PX
```

Then replace the body of the per-entity loop from the position update through the velocity clamp:

```python
            # Update the position by the velocity. flag_do_move.dt_on=False opts
            # this entity out of dt scaling - use a separate name, because
            # rebinding dt here would leak the opt-out into every later entity
            # processed in the same frame.
            dt_scale = dt if flag_do_move.dt_on else 1
            velocity = 1 if flag_do_move.absolute else movable.velocity # ignore velocity and move using absolute vector
            position.x += flag_do_move.vector[0] * velocity * dt_scale
            position.y += flag_do_move.vector[1] * velocity * dt_scale
            logger.debug(f'({self.cycle}) - Entity {ent} - new position: [{position.x}, {position.y}] {flag_do_move.dt_on=}, {dt_scale=}, {velocity=}')

            # Adjust the velocity by acceleration/deceleration. Integrated over
            # elapsed time, so the rate does not depend on the frame rate.
            movable.velocity += movable.accelerate * dt
            max_velocity = MAX_VELOCITY_TILES * GAME["TILE_RES_PX"]
            movable.velocity = min(movable.velocity, max_velocity) if sign(movable.accelerate) == 1 else max(movable.velocity, 0)
            logger.debug(f'({self.cycle}) - Entity {ent} - new velocity {movable.velocity}, accelerate {movable.accelerate}')
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/example_game/test_movement_acceleration.py -v`
Expected: 5 passed.

- [ ] **Step 5: Fix the hardcoded debug-arrow divisor**

`perform_render_debug_info_processor.py:275` sizes the debug movement arrow with `moveable.velocity // 5` — a pixel count that grows with resolution and now with fractional speeds. Replace with a tile-relative length:

```python
                    tuple(map(camera.apply, get_arrow_points(position.dir_name, moveable.velocity_tiles * GAME["TILE_RES_PX"] / 5, (position.x, position.y)))),
```

Confirm `GAME` is already imported in that module (it is — `TILE_RES_PX` is used elsewhere in the file); if not, add `from pgrpg.core.config import GAME`.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests/`
Expected: same result as Task 6 Step 7 — only `test_resource_schemas.py` failing, awaiting Task 8. The golden trace from Task 1 still fails at this point too, because the scene data still says `velocity: 100`, which `Movable` now reads as tiles. Task 8 resolves both.

- [ ] **Step 7: Checkpoint**

Report: `perform_movement_processor.py`, `perform_render_debug_info_processor.py`, `tests/example_game/test_movement_acceleration.py`.

---

### Task 8: Migrate the shipped data to tiles per second

**Files:**
- Create: `pgrpg/utils/migrate_velocity_to_tiles.py`
- Modify: ~170 occurrences across `example_game/resources/**/*.jsonc`
- Modify: `tests/example_game/test_movement_golden_trace.py`
- Create: `tests/example_game/test_movement_scaling.py`

**Interfaces:**
- Consumes: `Movable` from Task 6.

- [ ] **Step 1: Write the migration script**

Per `CLAUDE.md`, file-processing logic goes through Python with `pathlib`, never shell text tools.

```python
"""One-shot migration of Movable speeds from pixels to tiles per second.

`velocity` was pixels/second and `accelerate` was pixels/second *per frame*.
Both are now tile-relative and time-integrated:

    velocity_tiles   = velocity_px / REF_TILE_PX
    accelerate_tiles = accelerate_px_per_frame * SIM_HZ / REF_TILE_PX

Every shipped velocity divides by 64 exactly - they are dyadic rationals, so
behaviour at TILE_RES_PX 64 is numerically unchanged. Acceleration cannot be
preserved, because its old values encoded the developer's frame rate; the
conversion reproduces "as if the game had run at SIM_HZ" and the results are
re-tuned by eye afterwards (see the plan's Task 11).

Template placeholders such as "$velocity" and "$acc" are substituted at
instantiation from numeric literals elsewhere in the data, so they are skipped.

Run from the repository root:

    python -m pgrpg.utils.migrate_velocity_to_tiles --dry-run
    python -m pgrpg.utils.migrate_velocity_to_tiles
"""

import argparse
import re
from pathlib import Path

REF_TILE_PX = 64
SIM_HZ = 60

RESOURCES = Path("example_game/resources")

# Matches `"velocity" : 100` and `"accelerate": -3`, capturing the key, the
# separator run and the numeric literal. A quoted value (a "$var" placeholder)
# does not match, because the value group admits no quote character.
_PARAM = re.compile(r'("(?:velocity|accelerate)"\s*:\s*)(-?\d+(?:\.\d+)?)(?=\s*[,}\]])')


def convert(key: str, value: float) -> float:
    """Return the tile-relative value for one authored pixel value."""
    if key == "velocity":
        return value / REF_TILE_PX
    return value * SIM_HZ / REF_TILE_PX


def _format(value: float) -> str:
    """Render a converted value without a trailing `.0` on whole numbers."""
    if value == int(value):
        return str(int(value))
    # repr gives the shortest round-tripping form, e.g. 1.5625 not 1.5625000001
    return repr(value)


def migrate_text(text: str) -> tuple[str, int]:
    """Convert every numeric velocity/accelerate literal in one file's text.

    Returns the new text and the number of substitutions made.

    Tests:
        >>> migrate_text('{"velocity" : 100}')
        ('{"velocity" : 1.5625}', 1)
        >>> migrate_text('{"accelerate" : -3}')
        ('{"accelerate" : -2.8125}', 1)
        >>> migrate_text('{"velocity" : "$velocity"}')       # placeholder untouched
        ('{"velocity" : "$velocity"}', 0)
        >>> migrate_text('{"velocity" : 500, "accelerate" : -2}')
        ('{"velocity" : 7.8125, "accelerate" : -1.875}', 2)
    """
    count = 0

    def _sub(match):
        nonlocal count
        count += 1
        prefix, raw = match.group(1), match.group(2)
        key = "velocity" if "velocity" in prefix else "accelerate"
        return prefix + _format(convert(key, float(raw)))

    return _PARAM.sub(_sub, text), count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    args = parser.parse_args()

    total_files = 0
    total_subs = 0

    for path in sorted(RESOURCES.rglob("*.jsonc")):
        original = path.read_text(encoding="utf-8")
        migrated, count = migrate_text(original)

        if not count:
            continue

        total_files += 1
        total_subs += count
        print(f"{path}: {count} value(s)")

        if not args.dry_run:
            path.write_text(migrated, encoding="utf-8")

    verb = "would change" if args.dry_run else "changed"
    print(f"\n{verb} {total_subs} value(s) across {total_files} file(s)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the script's own doctests**

Run: `python -m doctest pgrpg/utils/migrate_velocity_to_tiles.py -v`
Expected: 4 doctests pass. These pin the exact conversions — `100 → 1.5625`, `-3 → -2.8125`, `500 → 7.8125`, `-2 → -1.875`, and placeholders untouched.

- [ ] **Step 3: Dry-run the migration and check the counts**

Run: `python -m pgrpg.utils.migrate_velocity_to_tiles --dry-run`
Expected: 150 `velocity` values plus 20 `accelerate` values = **170 substitutions**, and no `"$velocity"` / `"$acc"` placeholder reported. If the totals differ from 150/20, stop and reconcile against the spec's §5.3 and §5.4 tables before writing anything.

- [ ] **Step 4: Run the migration**

Run: `python -m pgrpg.utils.migrate_velocity_to_tiles`

Then spot-check one file by hand:

```bash
grep -n "velocity\|accelerate" example_game/resources/scenes/games/kill_all/kill_all_level01.jsonc | head
```

Expected at line ~150: `{"type" : "movable:Movable", "params" :  {"velocity" : 7.8125, "accelerate" : -2.8125}}`.

- [ ] **Step 5: Update the golden trace to the migrated unit**

In `tests/example_game/test_movement_golden_trace.py`, change the one authored value and nothing else — the asserted trace must stay byte-identical, which is exactly the point:

```python
def test_golden_trace_at_64px(tile_res):
    """velocity 100 px/s at 64 px, 60 Hz, 10 steps: 1.5625 tiles/s."""
    tile_res(64)
    world = World()
    # Migrated from `velocity=100` (px/s). The asserted trace is unchanged.
    entity = build_moving_entity(world, velocity=100 / 64)

    trace = run_trace(world, entity)

    assert trace[0] == pytest.approx((100 * STEP_MS / 1000, 0.0))
    assert trace[-1] == pytest.approx((100 * STEPS * STEP_MS / 1000, 0.0))
    assert len(trace) == STEPS
```

- [ ] **Step 6: Run the golden trace**

Run: `pytest tests/example_game/test_movement_golden_trace.py -v`
Expected: PASS with the **same asserted numbers as Task 1**. This is the verification that speed at 64 px is unchanged.

- [ ] **Step 7: Write the resolution-scaling test**

```python
"""The same authored speed must cover the same ground at any TILE_RES_PX.

This is the regression test for the reported symptom: changing TILE_RES_PX from
64 to 32 made the character move twice as fast relative to the world, because
velocity was in pixels while everything else scaled with the tile size.
"""

import pytest

import pgrpg.core.config as config
from pgrpg.core.ecs import World
from core.components.position import Position
from core.components.movable import Movable
from core.components.flag_do_move import FlagDoMove
from core.processors.movement_system.perform_movement_processor import PerformMovementProcessor

STEP_MS = 1000 / 60
CHARACTER_TILES_PER_S = 100 / 64


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def tiles_moved_in_one_second(tile_res_px):
    """Run one simulated second of movement, returning distance in tiles."""
    world = World()
    entity = world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=CHARACTER_TILES_PER_S),
        FlagDoMove(moves=["right"]),
    )
    proc = PerformMovementProcessor()
    proc.world = world

    for _ in range(60):
        world.add_component(entity, FlagDoMove(moves=["right"]))
        proc.process(dt=STEP_MS)

    return world.component_for_entity(entity, Position).x / tile_res_px


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_distance_in_tiles_is_resolution_independent(tile_res_px, tile_res):
    tile_res(tile_res_px)

    assert tiles_moved_in_one_second(tile_res_px) == pytest.approx(CHARACTER_TILES_PER_S)


def test_pixel_distance_still_scales_with_resolution(tile_res):
    """The world is bigger at 96 px, so the same journey is more pixels."""
    tile_res(32)
    small = tiles_moved_in_one_second(32) * 32
    tile_res(96)
    large = tiles_moved_in_one_second(96) * 96

    assert large == pytest.approx(small * 3)
```

- [ ] **Step 8: Run the scaling test and the whole suite**

Run: `pytest tests/example_game/test_movement_scaling.py -v`
Expected: 4 passed.

Run: `pytest tests/`
Expected: **all green**, including `test_resource_schemas.py`, which was failing since Task 6. Total is the Task 5 figure plus 23 new tests (14 from Task 6, 5 from Task 7, 4 here).

- [ ] **Step 9: Play the game and sanity-check speed**

Run: `python example_game/game.py -f tests/01_movements/test_movement_10.jsonc`
Expected: the character moves at the same speed it did before the whole change.

Then edit `example_game/config.jsonc` to `"TILE_RES_PX": 32`, relaunch the same scene, and confirm the character now crosses the map in **the same time** as at 64 px — the original reported bug. Restore `64` afterwards.

- [ ] **Step 10: Checkpoint**

Report: `pgrpg/utils/migrate_velocity_to_tiles.py`, the migrated `.jsonc` files (list the count, not all 100+ names), `tests/example_game/test_movement_golden_trace.py`, `tests/example_game/test_movement_scaling.py`.

---

### Task 9: Position interpolation

**Files:**
- Modify: `example_game/core/components/position.py:49,111-113`
- Modify: `example_game/core/processors/functions.py`
- Modify: `example_game/core/processors/teleport_system/perform_teleportation_processor.py:78`
- Modify: `example_game/core/processors/render_system/perform_render_model_processor.py:69`
- Modify: `example_game/core/processors/render_system/perform_render_armed_weapon_processor.py`, `perform_render_armed_ammo_processor.py`, `perform_render_debug_info_processor.py`
- Create: `tests/example_game/test_position_interpolation.py`

**Interfaces:**
- Consumes: `alpha` kwarg delivered by `run_render` (Task 5).
- Produces:
  - `Position.prevx`, `Position.prevy`, `Position.prevmap` — declared slots.
  - `Position.snapshot()` — records the current position as the previous one.
  - `interp_xy(position, alpha) -> tuple[float, float]` in `example_game/core/processors/functions.py`.

- [ ] **Step 1: Write the failing tests**

```python
"""Rendering interpolates between the last two simulation states.

With the simulation at 60 Hz and rendering free-running, drawing the raw
position would show the same pixel for several consecutive frames and then
jump. Interpolating by alpha - the fraction of the way to the next simulation
step - is what turns a fixed timestep into smooth motion.
"""

import pytest

import pgrpg.core.config as config
from core.components.position import Position
from core.processors.functions import interp_xy


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def test_snapshot_collapses_previous_onto_current(tile_res):
    tile_res(64)
    pos = Position(x=100, y=200, map="test_map")

    assert (pos.prevx, pos.prevy) == (100, 200)
    assert pos.prevmap == "test_map"


def test_alpha_zero_draws_the_previous_state(tile_res):
    tile_res(64)
    pos = Position(x=100, y=100, map="test_map")
    pos.snapshot()
    pos.x, pos.y = 200, 300

    assert interp_xy(pos, 0.0) == pytest.approx((100, 100))


def test_alpha_one_draws_the_current_state(tile_res):
    tile_res(64)
    pos = Position(x=100, y=100, map="test_map")
    pos.snapshot()
    pos.x, pos.y = 200, 300

    assert interp_xy(pos, 1.0) == pytest.approx((200, 300))


def test_alpha_half_draws_the_midpoint(tile_res):
    tile_res(64)
    pos = Position(x=100, y=100, map="test_map")
    pos.snapshot()
    pos.x, pos.y = 200, 300

    assert interp_xy(pos, 0.5) == pytest.approx((150, 200))


def test_a_map_change_is_never_interpolated(tile_res):
    """Interpolating across a map change would smear the entity across it."""
    tile_res(64)
    pos = Position(x=1000, y=1000, map="first_map")
    pos.snapshot()
    pos.x, pos.y, pos.map = 10, 10, "second_map"

    assert interp_xy(pos, 0.5) == pytest.approx((10, 10))


def test_prev_is_untouched_by_collision_scratch_writes(tile_res):
    """prevx and lastx have different lifetimes and must not be conflated.

    resolve_collisions_processor rewrites lastx mid-step; the interpolation
    baseline has to survive that, or a corrected collision would rubber-band.
    """
    tile_res(64)
    pos = Position(x=100, y=100, map="test_map")
    pos.snapshot()

    pos.x = 150
    pos.lastx = pos.x          # what resolve_collisions_processor does
    pos.x = 140                # ... then corrects the position

    assert pos.prevx == 100
    assert interp_xy(pos, 1.0) == pytest.approx((140, 100))


def test_snapshot_is_idempotent_within_a_step(tile_res):
    tile_res(64)
    pos = Position(x=100, y=100, map="test_map")
    pos.x = 150
    pos.snapshot()
    pos.snapshot()

    assert pos.prevx == 150
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/example_game/test_position_interpolation.py -v`
Expected: FAIL — `ImportError: cannot import name 'interp_xy'`.

- [ ] **Step 3: Add the interpolation state to `Position`**

In `example_game/core/components/position.py`, extend `__slots__` at line 49. Note that `lastx`, `lasty` and `lastmap` are currently assigned but *not* declared — they work only because `Component` declares no `__slots__` of its own, so every component carries a `__dict__`. Declare all six properly:

```python
    __slots__ = ['x', 'y', 'map', 'direction', 'dir_name',
                 'lastx', 'lasty', 'lastmap',
                 'prevx', 'prevy', 'prevmap']
```

Then extend the initialisation that currently sets only the `last*` trio (lines 111-113):

```python
        # Remember last possition, on collision return to the last known pos
        # Required for resolution of collisions with the map
        self.lastx = self.x
        self.lasty = self.y
        self.lastmap = self.map

        # Position at the start of the current simulation step. Distinct from
        # last* above, which is collision scratch space rewritten mid-step:
        # prev* is stable for the whole frame so the render stage can
        # interpolate against it.
        self.prevx = self.x
        self.prevy = self.y
        self.prevmap = self.map
```

And add the method:

```python
    def snapshot(self):
        '''Record the current position as the start of a simulation step.

        Called once per simulation step, before anything moves the entity, and
        again immediately after a teleport so the jump is not interpolated.
        '''
        self.prevx = self.x
        self.prevy = self.y
        self.prevmap = self.map
```

This replaces the placeholder added in Task 5 Step 3.

- [ ] **Step 4: Add the interpolation helper**

In `example_game/core/processors/functions.py`, alongside the existing filters:

```python
def interp_xy(position: Position, alpha: float) -> tuple:
    '''Position to draw at, interpolated between the last two simulation steps.

    The simulation advances in fixed steps while rendering runs at the display's
    own rate, so a frame usually falls *between* two simulation states. `alpha`
    is how far between them, in [0, 1). Drawing the raw position instead would
    show several identical frames and then a jump.

    A change of map is a discontinuity, not motion, so it is never interpolated -
    otherwise the entity would be drawn sliding across the gap between maps.

    Parameters:
        :param position: The entity's Position component.
        :param alpha: Fraction of the way to the current simulation state.

    Returns:
        Tuple (x, y) in pixels, as floats.
    '''
    if position.map != position.prevmap:
        return (position.x, position.y)

    return (position.prevx + (position.x - position.prevx) * alpha,
            position.prevy + (position.y - position.prevy) * alpha)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/example_game/test_position_interpolation.py -v`
Expected: 7 passed.

- [ ] **Step 6: Collapse the snapshot after a teleport**

In `example_game/core/processors/teleport_system/perform_teleportation_processor.py`, after the block that assigns the destination (line 78 onward, `position.x = flag_is_about_to_be_teleported_by.dest_x` and its `y`/`map` siblings), add:

```python
            # A teleport is a discontinuity, not motion. Collapse the
            # interpolation baseline onto the new position so the render stage
            # does not draw the entity sliding to it.
            position.snapshot()
```

- [ ] **Step 7: Draw interpolated positions**

In `perform_render_model_processor.py`, add the import and use the helper:

```python
from ..functions import filter_only_visible_on_camera # for filtering only entities with position on the cameras
from ..functions import interp_xy # for smooth motion between simulation steps
```

```python
    def process(self, *args, **kwargs):
        ''' Blit RenderableModel onto the screen.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # How far between the last two simulation steps this frame falls.
        # Defaults to 1.0 - the current state - for callers that do not
        # interpolate, e.g. progress rendering during scene load.
        alpha = kwargs.get('alpha', 1.0)

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Blit all the Entities that have Renderable and Position components + only visible entities + are not picked up
            for ent, (position, renderable) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, RenderableModel)):
                camera.screen.blit(renderable.get_current_frame(position.dir_name), camera.apply(renderable.topleft(interp_xy(position, alpha))))
```

Apply the same three-part change — import, `alpha = kwargs.get('alpha', 1.0)`, `interp_xy(position, alpha)` in place of `(position.x, position.y)` — to `perform_render_armed_weapon_processor.py`, `perform_render_armed_ammo_processor.py` and `perform_render_debug_info_processor.py`.

Culling (`filter_only_visible_on_camera`) deliberately keeps using the raw position. A sub-pixel interpolation offset cannot change whether an entity is on screen, and the existing cull margin absorbs the difference.

- [ ] **Step 8: Run the suite and the game**

Run: `pytest tests/`
Expected: the Task 8 total plus 7.

Run: `python example_game/game.py -f tests/01_movements/test_movement_10.jsonc`
Expected: motion is smooth. Then raise `DISPLAY["MAX_FPS"]` in `example_game/config.jsonc` to `144`, relaunch, and confirm motion is smoother still rather than juddering — that is the interpolation doing its job. Restore `60`.

Also walk through a teleport scene and confirm no smear:

```bash
python example_game/game.py -f tests/11_teleport/test_teleport_01.jsonc
```

Check the actual filename first with `ls example_game/resources/scenes/tests/` — use whichever teleport scene exists.

- [ ] **Step 9: Checkpoint**

Report: `position.py`, `functions.py`, `perform_teleportation_processor.py`, the four render processors, `tests/example_game/test_position_interpolation.py`.

---

### Task 10: Camera interpolation

Deferrable per spec §3.6. If the delayed camera's fixed-fraction lerp fights interpolation, stop and report rather than blocking the rest.

**Files:**
- Modify: `example_game/core/processors/render_system/perform_scroll_camera_processor.py:71,103,107`
- Modify: `example_game/core/processors/render_system/perform_scroll_delayed_camera_processor.py:81,117,121`

**Interfaces:**
- Consumes: `interp_xy` (Task 9).

- [ ] **Step 1: Interpolate the plain scrolling camera**

The camera must follow the *interpolated* player position, or the world judders relative to the player even though both are individually smooth. In `perform_scroll_camera_processor.py`, add the import and alpha read as in Task 9 Step 7, then replace each `position.x` / `position.y` used to compute the camera offset:

```python
        alpha = kwargs.get('alpha', 1.0)
        ...
            draw_x, draw_y = interp_xy(position, alpha)
            x = -draw_x + camera.screen_width_half
```

and correspondingly at the `x1`/`x2` bounds computation (lines 103 and 107) and their `y` counterparts. Leave `pos_map_ref.width` / `.height` clamping untouched — those are map bounds, not positions.

- [ ] **Step 2: Verify by playing**

Run: `python example_game/game.py -f tests/01_movements/test_movement_10.jsonc`
Expected: the map scrolls smoothly and the player stays visually locked to the camera centre. If the player appears to vibrate against the background, the camera and the model are using different alphas — check both read `kwargs.get('alpha', 1.0)`.

- [ ] **Step 3: Interpolate the delayed camera**

`perform_scroll_delayed_camera_processor.py` applies `self.delay` as a fixed fraction per call (lines 117, 121), which was frame-rate dependent and is now render-rate dependent. Make the same `interp_xy` substitution for `position.x`/`position.y` at lines 81, 117 and 121.

Do **not** attempt to convert `self.delay` into a time constant in this task — that is a behavioural change to camera feel, separate from #74. Note it for a follow-up issue.

- [ ] **Step 4: Verify the delayed camera**

Find a scene using it:

```bash
grep -rln "PerformScrollDelayedCameraProcessor" --include=*.jsonc example_game/resources
```

Run one and confirm the lag still reads as intentional smoothing rather than stutter. **If it stutters or oscillates, revert this step, report it, and leave the delayed camera for a follow-up issue** — spec §3.6 explicitly permits this.

- [ ] **Step 5: Run the suite**

Run: `pytest tests/`
Expected: the Task 9 total, unchanged — this task adds no tests, it is verified by eye.

- [ ] **Step 6: Checkpoint**

Report: the two camera processors, plus a clear statement of whether Step 3 was kept or reverted.

---

### Task 11: Re-tune the values that encoded the old frame rate

Two behaviours cannot be preserved, because their shipped values were tuned against an uncapped frame rate. Both are now machine-independent; both need a one-time re-tune.

**Files:**
- Modify: `example_game/resources/scenes/**` — `max_no_of_calcs` values
- Modify: `example_game/resources/scenes/**` — projectile `accelerate` values
- Modify: `example_game/resources/scenes/tests/02_commands/recorded_commands.rec`
- Create: `tests/example_game/test_movement_determinism.py`

**Interfaces:**
- Consumes: the `measured_fps / 60` ratio from Task 1.

- [ ] **Step 1: Raise the pathfinding budget**

`pathfind_manager.continue_pathfinding(max_steps)` budgets A* work **per cycle**. Cycles were previously frames; they are now fixed simulation steps, so at 60 Hz the wall-clock budget dropped by the Task 1 ratio.

Find the call sites and multiply each `max_no_of_calcs` by that ratio, rounded to a round number:

```bash
grep -rn "max_no_of_calcs" --include=*.jsonc example_game/resources
```

For example, if Task 1 measured 300 fps, the ratio is 5, so `100` becomes `500`.

- [ ] **Step 2: Verify AI responsiveness**

Run: `python example_game/game.py -f tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear.jsonc`
Expected: guards react and path to the player without visible hesitation. If they stall, raise the budget further; if the frame rate drops, lower it. This is a judgement call for the repository owner — report the value chosen and what it looked like.

- [ ] **Step 3: Re-tune projectile deceleration**

Task 8 converted `accelerate` mechanically as `px_per_frame × 60 ÷ 64`, which reproduces "as if the game had run at 60 fps". Because the values were tuned at ~1000 fps, arrows and fireballs now travel considerably further.

Run the projectile scenes and adjust the ~20 migrated `accelerate` values by eye:

```bash
python example_game/game.py -f games/kill_all/kill_all_level01.jsonc
python example_game/game.py -f tests/09_projectiles/test_projectile_collision.jsonc
```

Aim for the range the scenes were designed around — an arrow should die at roughly the far edge of its intended reach, not cross the whole map. Report before/after values.

- [ ] **Step 4: Write the determinism test**

```python
"""Simulation results must not depend on real frame timing.

This is the regression test for "a recording made on one computer plays back
differently on another". Under a fixed timestep, a jittery sequence of real
frame times must produce exactly the same simulation trace as a steady one,
because plan_steps converts real time into a whole number of identical steps.
"""

import pytest

import pgrpg.core.config as config
from pgrpg.core.ecs import World
from pgrpg.core.timestep import plan_steps
from core.components.position import Position
from core.components.movable import Movable
from core.components.flag_do_move import FlagDoMove
from core.processors.movement_system.perform_movement_processor import PerformMovementProcessor

STEP_MS = 1000 / 60
MAX_CATCHUP = 5


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def trace_for(real_frame_times):
    """Drive the movement processor through a loop of real frame times.

    Returns the position after each *simulation step*, which is what a
    recording replays against.
    """
    world = World()
    entity = world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=1.5625, accelerate=-0.5),
        FlagDoMove(moves=["right"]),
    )
    proc = PerformMovementProcessor()
    proc.world = world

    accumulator = 0.0
    trace = []

    for real_dt in real_frame_times:
        steps, accumulator = plan_steps(accumulator, real_dt, STEP_MS, MAX_CATCHUP)
        for _ in range(steps):
            world.add_component(entity, FlagDoMove(moves=["right"]))
            proc.process(dt=STEP_MS)
            pos = world.component_for_entity(entity, Position)
            trace.append((pos.x, pos.y))

    return trace


def test_jittery_and_steady_timing_produce_identical_traces(tile_res):
    """A fast machine and a struggling one must simulate the same world."""
    tile_res(64)

    steady = trace_for([STEP_MS] * 120)
    jittery = trace_for([3.0] * 40 + [40.0] * 20 + [9.5] * 60 + [70.0] * 10)

    shared = min(len(steady), len(jittery))
    assert shared > 60, "the jittery run must produce a comparable number of steps"
    assert steady[:shared] == jittery[:shared]


def test_a_long_stall_does_not_teleport_the_entity(tile_res):
    """Catch-up is capped, so a stall costs simulated time rather than a jump."""
    tile_res(64)

    trace = trace_for([STEP_MS, 5000.0])

    assert len(trace) == 1 + MAX_CATCHUP
```

- [ ] **Step 5: Run the determinism test**

Run: `pytest tests/example_game/test_movement_determinism.py -v`
Expected: 2 passed.

- [ ] **Step 6: Re-record the command recording**

`example_game/resources/scenes/tests/02_commands/recorded_commands.rec` was captured under a variable timestep, so its cycle numbers refer to frames that no longer exist. Re-record it:

```bash
python example_game/game.py -f tests/02_commands/record_commands.jsonc
```

Move the character around for 10-20 seconds, then quit cleanly so `finalize()` closes the file.

- [ ] **Step 7: Verify playback in all three modes**

```bash
python example_game/game.py -f tests/02_commands/play_commands_01.jsonc
python example_game/game.py -f tests/02_commands/play_commands_02.jsonc
python example_game/game.py -f tests/02_commands/play_commands_03.jsonc
```

Expected: `play_commands_01` (`total_control`) replays your recorded movement and ignores your input. Compare the path against what you performed while recording — they should match.

- [ ] **Step 8: Run the full suite**

Run: `pytest tests/`
Expected: the Task 9 total plus 2.

- [ ] **Step 9: Checkpoint**

Report: the scene files with changed `max_no_of_calcs` and `accelerate`, `recorded_commands.rec`, `tests/example_game/test_movement_determinism.py`. Include the before/after values and how playback looked — this is the task whose success is a judgement call, so the owner needs the detail.

---

### Task 12: Knowledge base updates

Required by `CLAUDE.md` Hard Rule 6 and `kb/RULES.md` Rule 12. Read `kb/RULES.md` first — it governs where facts go, the provenance-label format, and deduplication.

**Files:**
- Modify: `.claude/kb/core/bootstrap-and-loop.md`
- Modify: `.claude/kb/core/configuration.md`
- Modify: `.claude/kb/_shared/resolution.md`
- Modify: `.claude/kb/ecs/processors.md`
- Modify: `.claude/kb/ecs/components.md`
- Modify: `.claude/kb/authoring/component-params.md`
- Modify: `.claude/kb/reference/index.md`
- Modify: `.claude/kb/SCOPE.md`

- [ ] **Step 1: Read the KB rules**

Run: read `.claude/kb/RULES.md` in full, paying attention to Rule 12 and the provenance-label format used in each page's header (`> Last updated: … | Verified by: … @ <commit>`).

- [ ] **Step 2: Rewrite the loop documentation**

In `.claude/kb/core/bootstrap-and-loop.md`, replace the per-frame section with the two-clock model. Cover: `plan_steps` and the accumulator; `GAME["SIM_HZ"]` vs `DISPLAY["MAX_FPS"]`; the catch-up cap and the slow-motion degradation mode; that discrete `key_events` reach only the first sub-step while `key_pressed` reaches all of them; that `run_render` is opt-in per state module and only `game.py` defines it; and the `drew` flag that stops menu states flipping an untouched buffer.

- [ ] **Step 3: Document the new configuration**

In `.claude/kb/core/configuration.md`, add `GAME["SIM_HZ"]` and `GAME["MAX_CATCHUP_STEPS"]`, and correct `DISPLAY["MAX_FPS"]` to state that it caps **rendering only**.

- [ ] **Step 4: Add speed to the resolution page**

In `.claude/kb/_shared/resolution.md`, add `Movable` to the "Tile-relative params" table:

```markdown
| `Movable` | `velocity` (tiles/s), `accelerate` (tiles/s²) | — |
```

`Movable` is unusual in that page's terms: it has no separate absolute form, because `velocity` itself was redefined. Say so explicitly, note the `MAX_VELOCITY_TILES` ceiling and the `> 20 tiles/s` legacy warning, and add `Movable` to the list of components implementing `reinit()` in the "Set it at start-up only" section — that section currently states only `Camera` and `FlagShowInventory` do.

- [ ] **Step 5: Document `STAGE`**

In `.claude/kb/ecs/processors.md`, document `Processor.STAGE`: the two values, that `'sim'` is the default so existing processors need no change, that classification lives on the class rather than in scene data, that stages are orthogonal to the scene-authored group (`'pause'`), and that render processors read `kwargs.get('alpha', 1.0)`. Mention the `perform_gui_press` / `perform_gui_draw` split as the worked example of separating the two concerns.

- [ ] **Step 6: Document the two position histories**

In `.claude/kb/ecs/components.md`, document `Position.prevx`/`prevy`/`prevmap` versus `lastx`/`lasty`/`lastmap` — different lifetimes, and why they must not be conflated (`last*` is collision scratch space rewritten mid-step; `prev*` is the interpolation baseline, stable for the frame). Note that the snapshot is taken in `game.py::run()` rather than by a processor, and why: a processor would have to be listed first in all 78 scene files.

Record the `Component.__slots__` finding as a neutral fact: the base class declares no `__slots__`, so components carry a `__dict__` and undeclared attributes silently work. Note that `Position` now declares all eleven of its attributes.

- [ ] **Step 7: Update the authoring and reference pages**

In `.claude/kb/authoring/component-params.md`, update the `Movable` entry to tiles/second and tiles/second², with the `n/64` migration note.

Also record the `FlagDoMove` flags that deliberately bypass `dt` (spec §3.7), since their units are now surprising and nothing else documents them. Update `.claude/kb/authoring/handlers-and-actions.md` or `.claude/kb/core/commands-and-ai.md` — whichever already covers `move_dir` / `move_vect`; `commands-and-ai.md:93` already shows the `FlagDoMove(..., dt_on=…, absolute=…)` construction, so prefer that page. State: `dt_on=False` moves by the vector **per simulation step**, so its distance per second is proportional to `SIM_HZ`; `absolute=True` moves by exactly the vector **in raw pixels**, so it does *not* scale with `TILE_RES_PX`. Both are now machine-independent, which is all #74 requires; making them resolution-independent is explicitly out of scope.

In `.claude/kb/reference/index.md`, add `PerformGUIDrawProcessor` and note the new `STAGE` column concept if the page tabulates processors.

In `.claude/kb/SCOPE.md`, move command record/playback to reproducible, and update the `TILE_RES_PX` entry — changing it no longer changes game speed, though it still requires a restart.

- [ ] **Step 7b: Correct the stale test count in CLAUDE.md**

`CLAUDE.md` states `tests/                  pytest suite — 186 tests`. The real
figure on `master` was **194** before this plan and 242 after it (194 + 48).
Update that line, and re-check the neighbouring counts in the same block (scene,
entity, component and processor totals) rather than trusting them.

- [ ] **Step 8: Verify the KB is internally consistent**

Run:

```bash
grep -rn "MAX_FPS\|velocity\|per frame\|dt" .claude/kb/ | grep -v "SIM_HZ"
```

Read each hit and confirm none still describes the old single-clock behaviour or pixel-per-second speeds. Update the provenance line at the top of every page touched.

- [ ] **Step 9: Final full verification**

Run: `pytest tests/`
Expected: the Task 11 total, unchanged — 194 original tests plus 48 added across this plan (1 + 8 + 7 + 14 + 5 + 4 + 7 + 2 from Tasks 1, 2, 3, 6, 7, 8, 9 and 11).

Run: `python example_game/game.py -s MAIN_MENU`
Expected: menu works, a scene loads from it, gameplay is smooth at the correct speed.

- [ ] **Step 10: Checkpoint**

Report: all eight KB files, and a short summary for the issue #74 comment — what changed, the measured performance delta against Task 1's baseline, and the two re-tuned behaviours with their justification.

---

## Deviations from the spec

Flag these to the repository owner; each is a reduction in scope or churn, not a change in outcome.

1. **Spec §3.5 said all nine state modules split into `run_sim`/`run_render`.** Only `game.py` calls `ecs_manager.process`; the other eight draw menus directly inside `run()`. So `run()` keeps its name as the simulation entry point and `run_render` is opt-in via `getattr`. Eight fewer files touched, same behaviour. Requires the `drew` flag in the loop so menu states never flip an untouched buffer (Task 5).

2. **Spec §3.3 said "no scene file changes".** Almost true: the new `PerformGUIDrawProcessor` must be *listed* in the scenes that use the GUI, because an unlisted processor is never instantiated (Task 4 Step 5). The change is additive — no existing entry is modified — and it is confined to GUI scenes rather than all 78.

3. **`Movable` uses properties rather than the spec's two plain field pairs.** `perform_adjust_movement_processor` writes `movable.velocity` in pixels; with plain fields the tile value would drift and `reinit()` would resurrect a stale speed. Property setters keep the two representations in sync by construction (Task 6).

4. **Two bugs fixed in passing, both discovered while writing this plan.** `perform_movement_processor` rebound the loop-local `dt` inside the per-entity loop, so one `dt_on=False` entity silently disabled `dt` scaling for every entity processed after it in the same frame (Task 7, with a regression test). And `World.remove_processor` mutated the list it was iterating, which could skip an element when a group held two instances of one type (Task 3).

5. **`World.get_processor` now searches every group by default** instead of only `'default'`. Required, since a processor's registry key now includes its stage — and it incidentally fixes `PREREQ` checks for processors registered into the `'pause'` group, which were previously invisible (Task 3).
