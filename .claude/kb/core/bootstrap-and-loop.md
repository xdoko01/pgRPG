# Bootstrap, the Frame, and the State Machine

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/__init__.py`,
> `pgrpg/core/main.py`, `pgrpg/core/config/__init__.py`, `pgrpg/core/config/states.py`,
> `example_game/game.py`, `example_game/core/states/game.py` @ `c7b9a5f1`

## Boot sequence

A game is one call. `example_game/game.py:22`:

```python
import pgrpg
pgrpg.init(config_file="example_game/config.jsonc", scene_file=..., state=...)
```

`pgrpg.init()` (`pgrpg/__init__.py:11`) does exactly three things, in order:

1. `pgrpg.core.config.load(config_file=...)` — read and merge the two config files into the global
   config dicts. **No pygame objects are created yet** beyond the bare `pygame.init()` that
   `pgrpg.core.config` runs at import time (`pgrpg/core/config/__init__.py:10`).
2. `pgrpg.core.main.init(scene_file=..., state=...)`.
3. `pgrpg.core.main.run()` — the loop. Never returns.

### What `main.init()` does

Importing `pgrpg.core.main` is itself a side effect: at module level it calls
`config.init(main_module=sys.modules[__name__])` (`pgrpg/core/main.py:16`), which brings up display,
console, logging, fonts, frames, GUI, sound and the state machine. `main` passes a reference to
itself so the dev console can introspect the running game. See
[configuration.md §init phase](configuration.md#phase-2--init-building-live-objects).

Then `init()` (`pgrpg/core/main.py:55`):

```
_init_engine()          # import pgrpg.core.engine, call engine.init()  → wires managers
_init_state_modules()   # call .init() on every registered state module
                        # then, depending on arguments:
scene_file given  → engine.load_scene(scene_file, show_progress=True); change_state(State.GAME)
state given       → change_state(State[state])
neither           → change_state(State.CONSOLE) and run console script "default.scr"
```

`engine.init()` is idempotent-guarded only by a warning: calling it twice logs
`Engine already initiated.` and re-runs `engine.init()` anyway (`pgrpg/core/main.py:39-40`).

### Boot diagram

```
game.py
 └─ pgrpg.init(config_file, scene_file, state)
     ├─ config.load()                     merge defaults.jsonc + game config.jsonc
     ├─ main.init()
     │   ├─ [import side effect] config.init(main_module=main)
     │   │     _init_display  _init_console  _init_logging
     │   │     _init_fonts    _init_frames   _init_gui  _init_sound  _init_states
     │   ├─ engine.init()                  build game_functions → ecs_manager.initialize()
     │   ├─ state_module.init() for each state module
     │   └─ engine.load_scene(...) / change_state(...)
     └─ main.run()                         the frame loop, forever
```

## The frame

`main.run()` (`pgrpg/core/main.py:107`) is deliberately thin. It owns input, the console overlay,
the FPS readout and the buffer flip; **all game logic is delegated to the active state module.**

```python
gui_manager.clock.tick(DISPLAY["MAX_FPS"])
dt = 1000 / DISPLAY["MAX_FPS"]          # ms — seeded, not measured (see note below)

while True:
    key_events  = pygame.event.get()
    key_pressed = pygame.key.get_pressed()

    state_manager.change_state(
        state_manager.state_modules[state_manager.state].run(
            key_events=key_events, key_pressed=key_pressed, dt=dt))

    cons.update(key_events)               # console overlay ticks regardless of state
    cons.show(gui_manager.window)

    not DISPLAY["SHOW_FPS"] or gui_manager.blit_text("FPS: " + ...)
    gui_manager.flip()
    dt = gui_manager.clock.tick(DISPLAY["MAX_FPS"])   # ms since last tick
```

Two details worth knowing:

- **`dt` is in milliseconds**, not seconds, and is the value returned by `Clock.tick`.
- The **first** `dt` is computed from `MAX_FPS` rather than measured. Without this the first frame
  gets a huge `dt` and every entity teleports on frame 1 (`pgrpg/core/main.py:115-120`).
- The state module's `run()` **returns the next state**, which is fed straight into
  `change_state()`. Returning your own state means "stay".

### What a state module's `run()` does

`example_game/core/states/game.py:75` is the canonical example:

```python
def run(key_events, key_pressed, dt, debug=False) -> State:
    for event in key_events:
        if event.type == pygame.QUIT:                       return State.EXIT_GAME_DIALOG
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:                return State.MAIN_MENU
            elif event.key == KEYS["K_PAUSE_GAME"]:
                proc_group_id = 'pause' if proc_group_id == 'default' else 'default'
            ...
        elif event.type == pygame.KEYUP:
            if event.key == KEYS["K_CONSOLE_TOGGLE"]:       return State.CONSOLE

    engine.ecs_manager.process(proc_group_id=proc_group_id,
                               events=key_events, keys=key_pressed, dt=dt, debug=debug)
    return State.GAME
```

Note how **pause is implemented**: not by a flag, but by switching which *processor group* the
world processes. A `pause` group containing only render processors freezes the simulation while
still drawing. See [../ecs/processors.md §Groups](../ecs/processors.md#groups-and-priority).

### Full per-frame data flow

```
pygame events + pressed keys
 └─ state_module.run(key_events, key_pressed, dt)
     └─ ecs_manager.process(proc_group_id, events, keys, dt, debug)
         └─ World.process()
             ├─ _clear_dead_entities()          deferred deletions land here
             └─ each Processor in the group, priority desc:
                  Processor.process(events=…, keys=…, dt=…, debug=…)
                    ├─ may call event_manager.add_event(...)
                    ├─ may call command_manager.add_command(...)
                    ├─ CommandsProcessor  → command_manager.process_commands()
                    └─ GameEventsExProcessor → event_manager.process_events(process=…, ignore=…)
                          └─ handler match → script_manager.execute_event_actions()
                                └─ translate(alias → entity_id)
                                   json_logic(actions)
                                      └─ execute_script(name)   lazy import + call
 └─ console overlay update/show
 └─ gui_manager.flip()
```

The ordering of `add_event` / `process_events` and `add_command` / `process_commands` **is decided
in the scene file**, by where you place `GameEventsExProcessor` and `PerformCommandProcessor` in the
`processors` list. Put the event processor last and events raised this frame are handled this frame;
put it first and they are handled next frame.

## The state machine

`pgrpg/core/config/states.py` builds the `State` enum **from configuration at import time**:

```python
State = Enum("State", STATES["ALL_STATES"])
```

So the set of states is a data decision, not a code decision. The module then converts
`START_STATE`, `ALL_STATES`, `NON_GAME_STATES` and every key/value in `STATES_GRAPH` from strings
into `State` members, in place inside the config dict.

### Concepts

| Concept | Meaning |
|---------|---------|
| `ALL_STATES` | Every state that exists. Becomes the enum members. |
| `NON_GAME_STATES` | States that are *not* gameplay (menus, console, dialogs). |
| `game_states` | Derived: `ALL_STATES - NON_GAME_STATES`. |
| `STATES_GRAPH` | Adjacency list: which states each state may transition to. |
| `state` / `prev_state` | Current and previous state. |
| `game_state` / `prev_game_state` | The last *gameplay* state — survives a trip through a menu. |
| `changed` / `changed_game_state` | Whether a transition happened this frame. |

### Transition rules (`change_state`, `states.py:114`)

- Transitioning to the current state is a no-op that clears both `changed` flags.
- A transition is allowed **only if the target is listed in `STATES_GRAPH[current]`**. An
  illegal transition logs a warning and is silently ignored — the state does not change and no
  exception is raised. If a state transition "does nothing", check the graph first.
- `revert_state()` goes to `prev_state`.

### State module registration

`_initialize_state_modules()` (`states.py:86`) imports, for each state `S`:

```
{MODULEPATHS["STATE_MODULE_PATH"]}.{S.name.lower()}
```

e.g. `State.MAIN_MENU` → `core.states.main_menu`. A missing module is **not an error** — it logs
`State module not found` and that state simply has no behaviour. Each found module must expose
`initialize(state, register_fnc)` and call `register_fnc(state=..., module=sys.modules[__name__])`.

A state module's required surface (`example_game/core/states/game.py` header):

| Function | Purpose |
|----------|---------|
| `initialize(state, register_fnc)` | Register self with the state manager. Called by `states.py`. |
| `init(*args, **kwargs)` | Receive whatever the module needs to operate. Called by `main._init_state_modules()` and again on `reinit()`. |
| `run(key_events, key_pressed, dt)` | One frame in this state. Returns the next `State`. |
| `clear()` | Called when the program ends. |

The example game defines: `start_program`, `main_menu`, `settings`, `game`, `pause_game`,
`console`, `end_program`, `exit_game_dialog`, `load_scene_menu`. Note that `example_game`'s config
adds a `SETTINGS` state that the engine defaults do not have — see
[configuration.md](configuration.md).

## `reinit()` — display config changes

`main.reinit()` (`pgrpg/core/main.py:83`) is called by the settings screen and by the
`change_res` / `toggle_fullscreen` console commands. It:

1. Re-runs `config.init()` with `log_init`, `font_init`, `frame_init`, `sound_init` and
   `state_init` all `False` — i.e. **display + console + GUI only**.
2. Calls `ecs_manager.reinit_processors()` → `Processor.reinit()` on every registered processor.
3. Calls `ecs_manager.reinit_components()` → `Component.reinit()` on every component instance.
4. Re-runs `_init_state_modules()`.

Only two components in the example game implement a meaningful `reinit()`: `Camera` (resizes its
screen surface when `screen_fill` is set) and `FlagShowInventory`. Everything else inherits the
no-op.

**`reinit()` is scoped to display configuration.** It is not a general "config changed" hook. In
particular it does *not* re-normalise already-loaded maps and models, which is why `TILE_RES_PX`
must be set before start-up — see
[../_shared/resolution.md §Set it at start-up only](../_shared/resolution.md#set-it-at-start-up-only).

## Program teardown

`engine.exit_game()` calls `_clear_game()`, which clears maps, dialogs, messages, the command
queue, the event queue, the ECS (entities, components, processors) and the script registry, then
clears the scene registry. `ecs_manager.clear_processors()` first calls `World.finalize()` so every
processor gets a chance to close files; a processor without `finalize()` implemented raises
`NotImplementedError`, which `World._finalize` converts to `ValueError(processor)` and
`clear_processors` catches and downgrades to a warning.

## Related

- [configuration.md](configuration.md) — what `config.load()` and `config.init()` actually build.
- [scene-pipeline.md](scene-pipeline.md) — what `engine.load_scene()` does.
- [managers.md](managers.md) — what `engine.init()` wires together.
- [../ecs/processors.md](../ecs/processors.md) — processor groups, priority, throttling.
