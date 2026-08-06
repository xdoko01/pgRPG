# Separating Simulation and Render Frequency

> Design spec for GitHub issue [#74](https://github.com/xdoko01/pgRPG/issues/74)
> — "Make playback speed independent of machine speed"
>
> Status: **awaiting review** | Date: 2026-08-03 | Author: design session with Claude Code

## 1. Problem

Issue #74 asks that playback speed be independent of machine speed. The issue text notes the
wording is ambiguous. Investigation shows **both** readings are real defects, and they share a root
cause together with a third, separately-reported symptom.

### 1.1 Symptom A — changing `TILE_RES_PX` changes game speed

Reported directly: setting `GAME["TILE_RES_PX"]` from `64` to `32` makes the game and the player
character move roughly twice as fast relative to the world.

`Movable.velocity` is measured in **pixels per second**. `example_game/core/processors/movement_system/perform_movement_processor.py:92`:

```python
position.x += flag_do_move.vector[0] * velocity * dt
```

Every *other* world quantity already scales with `TILE_RES_PX` — tile images and `map.width` in
`pgrpg/core/maps/map.py`, model sprites in `pgrpg/core/models/model.py`, `Position.get_tile()`,
`Collidable._extent`, `CanSee`/`CanHear` `distance_tiles`. Speed is the one world quantity that never
received the tile-relative treatment documented in `.claude/kb/_shared/resolution.md`.

Consequence: at 32 px an entity with `velocity: 100` covers 3.125 tiles/second instead of 1.5625.
The *pixels* per second are unchanged; the *world* is half the size.

### 1.2 Symptom B — recordings do not reproduce on another machine

`RecordCommandToFileProcessor` keys each record by its own processor invocation count
(`record_command_to_file_processor.py:42,46`):

```python
self.cycle_counter += 1
new_rec = {'cycle': self.cycle_counter, 'commands': self.get_commands_fnc()}
```

`GenerateCommandFromFileProcessor` replays by matching that counter
(`generate_command_from_file_processor.py:97`):

```python
if self.cycle_counter == self.next_rec[0]:
```

Under a variable timestep, cycle *N* bears no fixed relationship to elapsed game time. On a machine
running 900 frames/second, cycle 4000 occurs ~4.4 s in; at 140 frames/second, ~28.6 s in. Each cycle
also advances positions by `velocity * dt` for a *different* `dt`. The same command stream therefore
produces different motion. The recording format is not wrong — the cycle counter simply has nothing
stable to count.

### 1.3 Symptom C — work that forgot `dt`

`dt` is threaded correctly from `main.run()` through every state module into processors, and movement
consumes it. But not everything does:

- `perform_movement_processor.py:97` — `movable.velocity += movable.accelerate`, applied **once per
  frame with no `dt`**. Acceleration therefore scales linearly with frame rate.
- `perform_movement_processor.py:98` — the velocity clamp is a hardcoded `1000` pixels/second.
- `perform_scroll_delayed_camera_processor.py:117,121` — camera smoothing applies a fixed fraction
  per frame, so smoothing rate tracks frame rate.
- `pgrpg/core/managers/pathfind_manager.py:97-114` — A* work is budgeted in **steps per cycle**
  (`max_no_of_calcs`, authored per scene, `100` in the `12_ai` scenes), so pathfinding latency in
  wall-clock terms is a property of the CPU.
- `perform_render_debug_info_processor.py:275` — debug arrow length is `velocity // 5`, a hardcoded
  pixel divisor.

Correct behaviour today depends on every processor author remembering `dt`. One omission silently
reintroduces machine dependence.

### 1.4 Root cause

`pgrpg/core/main.py:148` uses one number for two unrelated questions:

```python
dt = gui_manager.clock.tick(DISPLAY["MAX_FPS"])
```

`clock.tick(fps)` caps the frame rate *and* returns real milliseconds elapsed. That value becomes
`dt`. So "how fast can this machine draw?" and "how far should the world advance?" are the same
variable. They are different questions: the first is hardware, the second must be a property of the
game.

## 2. Goals and non-goals

### Goals

1. Identical game speed on machines of differing performance.
2. Identical game speed at any `TILE_RES_PX`.
3. Command recordings replay exactly on any machine.
4. Machine-independence should be **structural**, not dependent on each processor remembering `dt`.
5. Rendering frequency independently configurable from simulation frequency, without visual
   judder.

### Non-goals

- Networked or rollback determinism. Same-binary, same-scene reproducibility only.
- Bit-exact cross-platform float reproducibility.
- Making `TILE_RES_PX` changeable at runtime. It remains a start-up value
  (`.claude/kb/_shared/resolution.md` §"Set it at start-up only").
- Multi-cell entity footprints.

### Compatibility commitment

At `TILE_RES_PX: 64`, **movement speed after this change is numerically identical to today**. The
migration in §5.3 converts every shipped value exactly. Two behaviours deliberately do change, both
because their current values encode the developer's CPU speed: projectile deceleration (§5.4) and
pathfinding latency (§5.5).

## 3. Architecture

Two independent clocks, each with its own rate.

| Clock | Advances | Rate source | Steps per second |
|---|---|---|---|
| Simulation | fixed-size chunks of game time | `GAME["SIM_HZ"]` | 60, exactly |
| Rendering | once per real frame | `DISPLAY["MAX_FPS"]` | whatever the machine achieves, capped |

The simulation advances in constant chunks of `1000 / SIM_HZ` ms. The loop's job is to decide **how
many chunks** to run per real frame. Rendering happens once per real frame and interpolates between
the two most recent simulation states.

### 3.1 New configuration

`GAME` section of `pgrpg/core/config/defaults.jsonc`:

```jsonc
"SIM_HZ": 60,             // simulation steps per second — the fixed timestep
"MAX_CATCHUP_STEPS": 5    // most simulation steps a single real frame may run
```

`DISPLAY["MAX_FPS"]` keeps its meaning and becomes genuinely useful, since it now caps *rendering
only*. `example_game/config.jsonc:10` currently sets `MAX_FPS: 1000`; it will be set to a display
refresh rate with a comment, because rendering will otherwise expand to fill 1000 frames/second
(see §8).

### 3.2 `pgrpg/core/timestep.py` — new module

One pure function, no pygame import, directly unit-testable:

```python
def plan_steps(accumulator_ms: float,
               real_dt_ms: float,
               step_ms: float,
               max_steps: int) -> tuple[int, float]:
    """Return (n_steps, new_accumulator_ms) for one real frame."""
```

The accumulator is a bank of unspent real time. Real time arrives in messy amounts; it is withdrawn
only in exact `step_ms` units, and the remainder carries to the next frame. Over any interval,
simulated time therefore tracks real time without drift.

`real_dt_ms` is clamped to `max_steps * step_ms` **before** accumulating. This is what prevents the
*spiral of death*: after a long stall (scene load, debugger breakpoint, window drag) the naive loop
schedules hundreds of steps, each of which takes time, which enlarges the next `real_dt`, which
schedules more steps. Clamping means simulated time is **discarded** after a stall rather than
replayed — correct, because the player was not playing, and the alternatives are a frozen game or a
character teleporting across the map.

Behaviour on a machine that cannot sustain `SIM_HZ`: catch-up saturates and the game runs in **slow
motion**. This is a deliberate, predictable degradation mode, replacing today's "runs at whatever
speed the hardware gives".

### 3.3 Stage classification: `Processor.STAGE`

The engine already supports processor groups. `ecs_manager.create_processor():151`:

```python
proc_group = 'default' if len(processor_def) == 2 else processor_def[0]
```

A scene processor entry is `[group_id (optional), class_path, params]`; `World._processors` is a
`defaultdict(list)` keyed by group (`pgrpg/core/ecs/__init__.py:134`); seven scenes already use an
explicit `"pause"` group; `example_game/core/states/game.py` swaps `proc_group_id` between
`'default'` and `'pause'` at runtime.

The sim/render split is therefore derived **from the processor class**, not authored per scene:

```python
class Processor:
    STAGE = 'sim'      # default — every existing processor stays simulation-stage
```

Render processors declare it once:

```python
class PerformRenderMapProcessor(Processor):
    STAGE = 'render'
```

`World.add_processor` keys the internal dict on the pair, and `World.process` takes a stage:

```python
self._processors[(proc_group_id, processor_instance.STAGE)].append(processor_instance)
```

**No scene file changes.** The `"pause"` group becomes `('pause','sim')` and `('pause','render')`;
since the pause group contains only `PerformBlitPictureProcessor`, its sim list is empty and runs as
a no-op, preserving current behaviour.

Classification belongs on the class because it is a property of the processor. A scene author has no
business deciding whether `PerformRenderMapProcessor` is a renderer.

**Render-stage processors** — the 14 classes in `example_game/core/processors/render_system/`.
Everything else keeps the `'sim'` default.

**One processor must be split.** `gui_system/perform_gui_press.py` does both jobs in one
`process()`: it consumes discrete `UI_BUTTON_PRESSED` events and emits commands, an
`ON_BUTTON_PRESSED` event and a `GUIFlagWasPressed` component (simulation), then calls
`gui_manager.update(dt)` and `gui_manager.draw_gui()` (rendering, lines 106-107). It becomes two
processors: a sim-stage press handler and a render-stage GUI drawer.

### 3.4 The loop

`pgrpg/core/main.py:run()`:

```python
sim_step_ms = 1000 / GAME["SIM_HZ"]
accumulator = 0.0
real_dt     = sim_step_ms                     # replaces the existing first-frame fix (main.py:119-120)

while True:
    key_events  = pygame.event.get()
    key_pressed = pygame.key.get_pressed()

    # --- simulation: 0..N fixed steps, driven by real time elapsed ---
    n, accumulator = plan_steps(accumulator, real_dt, sim_step_ms, GAME["MAX_CATCHUP_STEPS"])
    step_events = key_events
    for _ in range(n):
        next_state = state_modules[state].run_sim(step_events, key_pressed, dt=sim_step_ms)
        step_events = ()                      # discrete events fire on the first sub-step only
        if next_state is not state:
            change_state(next_state)
            break

    # --- rendering: exactly once per real frame ---
    state_modules[state].run_render(dt=real_dt, alpha=accumulator / sim_step_ms)

    cons.update(key_events)
    cons.show(gui_manager.window)
    gui_manager.flip()

    real_dt = gui_manager.clock.tick(DISPLAY["MAX_FPS"])
```

Three load-bearing details:

1. **`step_events` is emptied after the first sub-step.** `key_pressed` is a *state* ("right arrow
   is down now") and legitimately applies to every sub-step. `key_events` are *discrete facts* ("ESC
   was pressed, once"). Passing the same `KEYDOWN` to two sub-steps would toggle pause twice
   (cancelling itself) or fire two attacks from one press — bugs that appear only on slow machines.
2. **A state change breaks the sub-step loop** immediately; the remaining accumulator carries into
   the next frame under the new state.
3. **`n` may legitimately be 0 or 2.** Rendering still happens every frame; with interpolation this
   is exactly what produces smooth motion between sim steps.

`dt` remains in **milliseconds** and remains a processor kwarg. No `Processor.process()` signature
changes — new values arrive as kwargs, which processors already read via `kwargs.get(...)`.

### 3.5 State module interface and `alpha` plumbing

`run()` splits into `run_sim(key_events, key_pressed, dt)` and `run_render(dt, alpha)` across all
nine modules in `example_game/core/states/`. Event handling and state transitions live in `run_sim`.
Mechanical, but it touches every module.

`ecs_manager.process()` (`pgrpg/core/managers/ecs_manager.py:60`) gains a `stage` argument, which it
forwards to `World.process()`:

```python
def process(proc_group_id, stage, events, keys, dt: float, debug: bool, **kwargs):
    _world.process(proc_group_id=proc_group_id, stage=stage,
                   events=events, keys=keys, dt=dt, debug=debug, **kwargs)
```

`alpha` travels the same path as `dt` — passed by `run_render` into `ecs_manager.process(...)` and
read by render processors as `kwargs.get('alpha', 1.0)`. The default of `1.0` matters: a render
processor that has not yet been converted to interpolate, or one called outside the main loop
(scene-load progress rendering), draws the current simulation state exactly as it does today.

### 3.6 Interpolation

Without interpolation, decoupling is worse than useless above `SIM_HZ`. Sim at 60 Hz with rendering
at 240 Hz draws four consecutive frames at the *identical* position, then jumps; because the 60 Hz
updates do not align with 240 Hz frames, the visible step sizes alternate irregularly. That is
**temporal aliasing**, and it can look worse than a locked 60 fps. Interpolation is the reason to
decouple, not an optional extra.

`alpha = accumulator / sim_step_ms` is the fraction of the way from the previous simulation state to
the current one. Render processors draw at:

```python
draw_x = position.prevx + (position.x - position.prevx) * alpha
```

**`Position` gains `prevx` / `prevy`**, snapshotted once per simulation step.

These **cannot** reuse the existing `lastx` / `lasty`. Those are collision scratch space with a
different lifetime: written by `perform_movement_processor.py:84`, rewritten mid-step by
`resolve_collisions_processor.py:75,179`, and read back by
`resolve_map_collisions_processor.py:75`. Interpolation needs a value stable for the whole frame.

Render processors reading positions and therefore requiring the interpolated value:
`perform_render_model_processor`, `perform_render_map_processor`, `perform_render_debug_info_processor`,
`perform_render_armed_weapon_processor`, `perform_render_armed_ammo_processor`, and both camera
processors.

**Incidental finding.** `Component` (`pgrpg/core/ecs/__init__.py:28`) declares no `__slots__` of its
own, so every component silently carries a `__dict__`. That is why `Position` can assign
`lastx`/`lasty`/`lastmap` (`position.py:111-113`) despite their absence from its `__slots__` list
(`position.py:49`), and why the base `__str__` — which iterates `self.__slots__` — does not print
them. This partially defeats `CLAUDE.md` Hard Rule 4. It is pre-existing and out of scope for #74,
but `prevx`/`prevy` **will** be declared in `__slots__` properly rather than copying the existing
pattern. Recommend a separate issue for the base class.

**The camera is the deferrable part.** It must scroll from the *interpolated* player position or the
world judders relative to the player. If that fights the existing fixed-fraction lerp in
`perform_scroll_delayed_camera_processor`, land everything else first and treat the camera as a
follow-up rather than blocking #74.

### 3.7 `dt_on` and `absolute` movement are unchanged

`FlagDoMove` has two flags that deliberately bypass `dt` scaling
(`perform_movement_processor.py:90-91`):

- `dt_on=False` — move by the vector without `dt` compensation, i.e. **per simulation step**.
- `absolute=True` — ignore `Movable.velocity` and move by exactly the vector, in pixels.

Both keep their current meaning. They are used for exact, teleport-like displacements
(`move_dir.py:149`, `move_vect.py:123`) where a fixed step is the point. Note the consequences:
distance per second for `dt_on=False` movement is proportional to `SIM_HZ`, and `absolute` vectors
are raw pixels and so do **not** scale with `TILE_RES_PX`. Both become machine-independent under a
fixed timestep, which is what #74 requires; making them resolution-independent as well is out of
scope and is recorded in the KB instead.

## 4. Why this fixes each symptom

| Symptom | Fixed by |
|---|---|
| A — `TILE_RES_PX` changes speed | §5 — speed authored in tiles/second, converted via `TILE_RES_PX` |
| B — recordings do not reproduce | §3.2/§3.4 — cycle *N* now always means simulated time `N × step_ms`. The cycle counter becomes a clock. **No change to the record/playback format or processors.** |
| C — work that forgot `dt` | §3.4 — `dt` becomes a constant, so code that omits it can no longer vary by machine. §5 fixes the units properly as well. |

Goal 4 is the systemic payoff: after this change, machine-independence holds unless a processor
deliberately reads the wall clock.

`RecordCommandToFileProcessor` is sim-stage, so its counter counts fixed steps and stays exact even
on a machine that cannot sustain 60 Hz — catch-up steps still execute every cycle, in order.

## 5. Speed in tiles per second

### 5.1 `Movable`

`velocity` is redefined as **tiles/second** and `accelerate` as **tiles/second²**. Both authored
values are retained so pixel values can be recomputed:

```python
self.velocity_tiles   = kwargs['velocity']            # authored, tiles/s
self.accelerate_tiles = kwargs.get('accelerate', 0)   # authored, tiles/s²
self.velocity   = self.velocity_tiles   * GAME["TILE_RES_PX"]   # px/s — what processors read
self.accelerate = self.accelerate_tiles * GAME["TILE_RES_PX"]   # px/s²
```

Processors keep reading `movable.velocity` in pixels, so `perform_adjust_movement_processor` and the
`FlagAdjustMovement` callables are unaffected. (Verified: `FlagAdjustMovement` is only ever
*removed* by scene data; it is constructed exclusively from Python.)

Retaining the authored values lets `Movable` implement **`reinit()`**, joining `Camera` and
`FlagShowInventory` as components that survive a config reinit.

The existing `isinstance(self.velocity, int)` assertion (`movable.py:57`) becomes a numeric check —
`1.5625` is now a legal and expected value.

### 5.2 Legacy-value guard

Redefining an existing key silently breaks any unmigrated scene. Mitigation: tiles/second above
`20` is not a plausible authored speed, while every legacy value was `≥ 50`. `Movable.__init__` logs
a `WARNING` naming the component and value when `velocity > 20`, suggesting `value / 64`.

### 5.3 Data migration

A script under `pgrpg/utils/` rewrites `velocity` and `accelerate` in `example_game/resources`.

`velocity` — 153 occurrences: 83× `100`, 35× `200`, 14× `500`, 9× `50`, 6× `300`, and one each of
`80`, `400`, `150`, plus 3 `"$velocity"` placeholders. Every value divides by 64 exactly:

| px/s | tiles/s | count |
|---|---|---|
| 50 | 0.78125 | 9 |
| 80 | 1.25 | 1 |
| 100 | 1.5625 | 83 |
| 150 | 2.34375 | 1 |
| 200 | 3.125 | 35 |
| 300 | 4.6875 | 6 |
| 400 | 6.25 | 1 |
| 500 | 7.8125 | 14 |

These are dyadic rationals, exact in binary floating point, so **behaviour at 64 px is unchanged** —
consistent with the `n/64` convention in `.claude/kb/_shared/resolution.md` §"Why the fractions look
strange".

`"$velocity"` and `"$acc"` are **template placeholders**, substituted at instantiation from the
numeric literals already counted above (e.g. `kill_all_level01.jsonc:150`). The script must convert
numeric literals only and **skip `"$…"` strings**.

Also fixed in the same pass: the hardcoded `1000` px/s clamp
(`perform_movement_processor.py:98`) becomes `MAX_VELOCITY_TILES * GAME["TILE_RES_PX"]`
(15.625 tiles/s, equal to 1000 px/s at 64 px), and the `velocity // 5` debug arrow divisor
(`perform_render_debug_info_processor.py:275`) becomes `TILE_RES_PX`-derived.

### 5.4 `accelerate` — an accepted, visible behaviour change

This is the one place where "identical at 64 px" cannot hold. `accelerate` is currently applied once
per frame with no `dt`, and the shipped values were hand-tuned against `MAX_FPS: 1000`. At ~1000
frames/second, `velocity: 500, accelerate: -3` decays a projectile to a standstill in ~0.17 s.

The integration is corrected to `movable.velocity += movable.accelerate * dt`, and values convert as
`px_per_frame × SIM_HZ ÷ 64` — reproducing "as if the game had run at 60 fps". `-3` becomes
`-2.8125` tiles/s², which decays in ~2.8 s.

**Arrows and fireballs will fly noticeably further than they do on the developer's machine today.**
That is the bug being fixed — their current range is a property of the CPU — but the fix is visible,
not invisible.

Affected: 23 `accelerate` occurrences across 17 files — 10× `-2`, 7× `-3`, 2× `-1`, 1× `5`, plus 3
`"$acc"` placeholders. After the mechanical conversion these are **re-tuned by eye** as an explicit,
separately-reviewable step.

### 5.5 Pathfinding budget — the second re-tune

`pathfind_manager.continue_pathfinding(max_steps)` budgets A* work per cycle, with the value authored
per scene (`perform_pathfinding_calculation_processor.py:18,35`; `"max_no_of_calcs": 100` in the
`12_ai` scenes). Today that is 100 steps × frame rate ≈ tens of thousands of steps/second. At 60 sim
steps/second it becomes 6 000/second.

Pathfinding latency becomes machine-independent for the first time — the same defect class as #74 —
but the absolute value must be raised (roughly by the ratio measured in Phase 0) or the `12_ai`
scenes will visibly hesitate. Re-tuned alongside §5.4.

## 6. Test plan

New tests in the existing `tests/` layout, run with `pytest tests/` from the repository root.

| Test file | Asserts |
|---|---|
| `tests/core/test_timestep.py` | `plan_steps` as a pure function: steady 60 Hz → exactly 1 step; a 3-second stall → clamped to `MAX_CATCHUP_STEPS`, not 180 steps; fractional accumulation over many frames conserves simulated time without drift |
| `tests/example_game/test_movable.py` | `velocity: 1.5625` → `velocity == 32 / 64 / 96` px at `TILE_RES_PX` 32/64/96; `accelerate` likewise; `reinit()` recomputes from the authored value; the §5.2 legacy warning fires for `velocity: 100` |
| `tests/example_game/test_movement_scaling.py` | The same authored velocity moves an entity the same number of **tiles** per simulated second at 32, 64 and 96 px — the regression test for symptom A. Joins the existing 32/64/96 suite |
| `tests/example_game/test_movement_determinism.py` | Driving the movement processor with a jittery sequence of *real* frame times yields a position trace identical to a steady sequence — the regression test for symptom B |
| `tests/example_game/test_movement_acceleration.py` | Acceleration integrates over time, not frames: two 30 ms steps reach the same velocity as one 60 ms step |
| `tests/example_game/test_interpolation.py` | Interpolated output equals `prev` at `alpha=0` and current at `alpha=1`; `prevx`/`prevy` are unaffected by the mid-step `lastx` rewrites in `resolve_collisions_processor` |
| `tests/core/ecs/test_processor_stages.py` | `STAGE` defaults to `'sim'`; a `'render'` processor lands in a separate group; running one stage does not run the other; a scene-authored `"pause"` group still resolves |
| Existing `tests/` (186) | Continue to pass |

Phase 0 additionally captures a **golden trace** of current 64 px movement, so §5.3's
"behaviour at 64 px is unchanged" is a verified claim rather than an argument from exact arithmetic.

## 7. Implementation phases

| Phase | Content | Verified by |
|---|---|---|
| 0 | Baseline measurement (§8) + golden-trace harness for current 64 px movement | Harness passes against unmodified code |
| 1 | `pgrpg/core/timestep.py` + `plan_steps` tests | Pure unit tests, no pygame |
| 2 | `Processor.STAGE`; `World`/`ecs_manager` group keying; split `perform_gui_press`; `run_sim`/`run_render` across 9 state modules; new loop | Game runs; `proc_perf` shows the two stages separately |
| 3 | `Movable` in tiles/s; `accelerate * dt`; tile-relative clamp; migration script; debug-arrow divisor | 32/64/96 scaling tests; Phase 0 golden trace still passes |
| 4 | Interpolation: `Position.prevx`/`prevy` (declared in `__slots__`), render processors read interpolated values | `alpha=0`/`alpha=1` tests |
| 5 | Camera interpolation — **deferrable** (§3.6) | Visual |
| 6 | Re-tune projectile `accelerate` (§5.4) and pathfinding budget (§5.5); re-record `recorded_commands.rec` | Playback determinism test |
| 7 | Knowledge-base updates (§9) | Rule 12 |

Phases 1–4 are the fix. Phases 5–6 are tuning that needs the repository owner's eye on the result.

The existing `example_game/resources/scenes/tests/02_commands/recorded_commands.rec` was recorded
under a variable timestep and becomes invalid; it is re-recorded in Phase 6.

## 8. Performance impact

The dominant effect: **simulation stops running at frame rate.** Today one `ecs_manager.process()`
call runs everything — AI, `generate_collisions`, event dispatch, pathfinding, and all rendering —
once per rendered frame, capped at `MAX_FPS: 1000`. After the split, the sim half runs 60×/second.

| | Direction | Magnitude |
|---|---|---|
| Sim processors (AI, collision, commands, events, pathfinding) | **↓ large** | Divides by `current_fps / 60` |
| Render processors | ~unchanged per frame | Same work, same rate |
| Interpolation | ↑ negligible | 2 multiply-adds per rendered entity per frame, against a `blit` |
| `prevx`/`prevy` snapshot | ↑ negligible | 2 float copies per `Position` per sim step |
| Memory | ↑ negligible | 2 floats per live `Position` |
| Catch-up on a slow machine | **↓** | Rendering happens once per frame, not once per catch-up step |

Net expectation: **meaningfully less CPU at the same frame rate, or a higher frame rate at the same
CPU**, because the per-frame cost loses everything except rendering.

**The one regression risk:** with sim work out of the frame path, frame rate rises toward
`MAX_FPS: 1000` and rendering expands to fill it, burning more total CPU/GPU than today on frames
the monitor never shows. Hence the `MAX_FPS` change in §3.1. This is configuration, not code.

These are estimates. **Phase 0 measures them** using tooling the engine already has — `"TIMED": true`
in the `pgrpg` config section, the `proc_perf` console command, and `SHOW_FPS` — on
`tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear.jsonc` (AI and pathfinding
heavy) and `games/kill_all/kill_all_level01.jsonc` (projectile heavy). The measured
`current_fps / 60` ratio also sets the §5.5 pathfinding multiplier.

## 9. Knowledge-base updates (RULES.md Rule 12)

| File | Change |
|---|---|
| `.claude/kb/core/bootstrap-and-loop.md` | Rewrite the frame section: two clocks, `plan_steps`, catch-up cap, first-sub-step-only event rule, `run_sim`/`run_render` |
| `.claude/kb/core/configuration.md` | `SIM_HZ`, `MAX_CATCHUP_STEPS`, `MAX_FPS`'s new render-only meaning |
| `.claude/kb/_shared/resolution.md` | Add `Movable` to the tile-relative table; speed is now a scaled world quantity |
| `.claude/kb/ecs/processors.md` | `STAGE`, and how to classify a new processor |
| `.claude/kb/ecs/components.md` | `Position.prevx`/`prevy` vs `lastx`/`lasty` — different lifetimes |
| `.claude/kb/authoring/component-params.md` | `Movable` units |
| `example_game/core/schemas/components/movable.schema.json` | New units and value ranges |
| `.claude/kb/reference/index.md`, `.claude/kb/SCOPE.md` | Command record/playback status → reproducible |

## 10. Decisions taken

| Decision | Choice | Rationale |
|---|---|---|
| Timing model | Fixed-timestep simulation | Makes machine-independence structural rather than per-processor discipline |
| Render coupling | Decoupled, with interpolation | Decoupling without interpolation buys nothing above `SIM_HZ` and can look worse (§3.6) |
| Speed units | Redefine `velocity` as tiles/second | No dual parameter; the §5.2 guard covers the silent-break risk |
| Stage classification | `Processor.STAGE` class attribute | Zero scene-file churn; classification is a property of the processor |
| `SIM_HZ` default | 60 | Collision has no swept-volume test; 500 px/s at 60 Hz is ~8 px/step, well within a tile |
| Recording format | Unchanged | Cycle indexing is correct once cycles are a clock |

## 11. Open items for review

1. **`SIM_HZ: 60`** — assumed. 30 or 120 are equally easy.
2. **§5.4 projectile behaviour change** — assumed accepted, with a by-eye re-tune in Phase 6.
3. **Camera interpolation (Phase 5)** — proposed as deferrable if it fights the existing delayed-camera lerp.
4. **`Component.__slots__`** (§3.6) — recommend a separate issue; not fixed here.
