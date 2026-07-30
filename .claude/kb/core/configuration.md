# Configuration

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/config/__init__.py`,
> `pgrpg/core/config/defaults.jsonc`, `example_game/config.jsonc` @ `c7b9a5f1`

## Two files, merged per section

Configuration is the merge of exactly two files:

| File | Role |
|------|------|
| `pgrpg/core/config/defaults.jsonc` | Engine defaults. Path is **hardcoded** at `pgrpg/core/config/__init__.py:14` as a path *relative to the process CWD*, so the game must be started from the repository root. Do not put game values here. |
| `<game>/config.jsonc` | Game overrides. Passed as `config_file` to `pgrpg.init()`. |

The merge is per top-level section, not whole-file:

```python
_merge_conf(default_config, game_config, conf_key)
  → merge_dicts(default_config.get(conf_key, {}), game_config.get(conf_key, {}))
```

`merge_dicts` (`pgrpg/functions/dict_utils.py:550`) is a recursive dict merge — the game value wins
at the leaf, but sibling default keys inside a nested dict survive. That is why
`example_game/config.jsonc` can define only `KEY_CONTROLS_1` under `KEYS` and still inherit
`DEFAULT`, `K_NAV_UP` and friends from the engine defaults.

`FILEPATHS.GAME_PATH` and `FILEPATHS.pgrpg_PATH` are **mandatory in the game config** — the engine
defaults do not supply them, and `_prep_conf_filepaths` reads `GAME_PATH` unconditionally.

## Two phases: `load()` then `init()`

This split matters. `load()` produces plain data; `init()` produces live pygame objects.

### Phase 1 — `load()`: data only

`config.load(config_file, hide_res=True)` fills the module-level global dicts. Each section goes
through a `_prep_conf_<section>()` function that normalises the raw data. **Order is significant**
and is enforced by the code, not by convention:

| # | Section | `_prep_` does | Why this position |
|---|---------|---------------|-------------------|
| 1 | `pgrpg` | nothing | — |
| 2 | `FILEPATHS` | prefixes every path with `GAME_PATH` and wraps in `Path`; `GAME_PATH` / `pgrpg_PATH` stay bare | **must be first** — later sections consume paths |
| 3 | `DISPLAY` | queries `pygame.display.list_modes()` and `Info()`; resolves `"DEFAULT"` resolution/bitdepth; wraps resolution in a `Resolution` namedtuple (`.width`, `.height`) | needs pygame initialised (done at import) |
| 4 | `KEYS` | `eval("pygame." + name)` per binding; builds `K_PROFILE`; **deletes** the original per-profile keys and `KEY_PROFILES` | — |
| 5 | `GUI` | derives `DLG_DIM_PX` and `DLG_START_PX` from resolution × `GUI_WINDOW_RATIO` | needs `DISPLAY` |
| 6 | `SOUND` | nothing | — |
| 7 | `GAME` | nothing | — |
| 8 | `MESSAGES` | nothing | — |
| 9 | `MODULEPATHS` | nothing | — |
| 10 | `FONTS` | resolves each font filename against `FONT_PATH` | needs `FILEPATHS` |
| 11 | `FRAMES` | resolves each frame filename against `FRAME_PATH` | needs `FILEPATHS` |
| 12 | `CONSOLE` | resolves background images against `IMAGE_PATH`, fonts against `FONT_PATH`; injects `cmd_pckg_path` and `script_path`; sets `CLI_MODULE` | **must be after `MODULEPATHS`** — it imports `pgrpg` internals that read `KEYS` |
| 13 | `LOGGING` | prefixes every file handler's `filename` with `GAME_PATH` | **must be after `CONSOLE`** — a handler may stream to the in-game console |
| 14 | `STATES` | nothing | — |

`load()` may be called repeatedly; passing `config_file=None` re-reads the last file. The
`hide_res=False` flag pretty-prints each section as it is prepared — useful for debugging a merge.

> ⚠️ **`KEYS` uses `eval`.** `_trans_key_from_str` (`config/__init__.py:279`) evaluates
> `"pygame." + key_string`. A key name in config is executed as Python. A `null` binding becomes
> `pygame.K_CLEAR`, chosen as an "unused" sentinel.

### Phase 2 — `init()`: building live objects

`config.init(main_module=..., **flags)` creates the objects. Each step is individually skippable
via a boolean flag, which is how `main.reinit()` restricts itself to display concerns:

| Step | Flag | Builds |
|------|------|--------|
| `_init_display()` | `display_init` | Validates resolution via `pygame.display.mode_ok`, raising `ValueError` on an unsupported one. First call: `set_mode` + window caption. Subsequent calls (reinit): copies the current surface, re-`set_mode`s, restores cursor, blits the copy back. |
| `_init_console()` | `cons_init` | Creates or re-inits the `pgconsole.Console` and points it at `CONSOLE["CLI_MODULE"]`. |
| `_init_logging()` | `log_init` | `logging.config.dictConfig(LOGGING)`. |
| `_init_fonts()` | `font_init` | `BitmapFont` objects into `FONTS[..._OBJ]`. |
| `_init_frames()` | `frame_init` | `BitmapFrame` objects into `FRAMES[..._OBJ]`. |
| `_init_gui()` | `gui_init` | Recomputes `GUI` dialog geometry, then background animation + GUI manager. |
| `_init_sound()` | `sound_init` | `pgrpg.core.config.sound.init()`. |
| `_init_states()` | `state_init` | `pgrpg.core.config.states.init(states=STATES)` — builds the state machine and imports state modules. |

`init()` asserts that a `main_module` has been supplied at least once; it is stored in
`MAIN_GAME_MODULE` so the console can introspect the running game.

## The config sections

Access them by importing the global dict, e.g. `from pgrpg.core.config import GAME`. They are
**mutable module globals**, so a mutation is visible everywhere — this is how `reinit()` propagates
a new resolution.

| Section | Contents |
|---------|----------|
| `pgrpg` | `TIMED` (bool) — when true, `World` is created with per-processor timing. Reachable via the `proc_perf` console command. |
| `STATES` | `ALL_STATES`, `NON_GAME_STATES`, `START_STATE`, `STATES_GRAPH`. See [bootstrap-and-loop.md §The state machine](bootstrap-and-loop.md#the-state-machine). |
| `DISPLAY` | `RESOLUTION` (or `"DEFAULT"`), `BITDEPTH`, `FULLSCREEN`, `MAX_FPS`, `SHOW_FPS`, `WIN_TITLE`. Post-prep also `SUPPORTED_RESOLUTIONS`, `DEFAULT_RESOLUTION`, `DEFAULT_BITDEPTH`, `WINDOW`. |
| `FILEPATHS` | `GAME_PATH`, `pgrpg_PATH` (both mandatory) plus `FONT_PATH`, `FRAME_PATH`, `DIALOG_PATH`, `MODEL_PATH`, `IMAGE_PATH`, `SCENE_PATH`, `ENTITY_PATH`, `BTREE_PATH`, `MAP_PATH`, `SOUND_PATH`, `MUSIC_PATH`, `LOG_PATH`, `SAVE_PATH`, `CONSOLE_SCRIPT_PATH`, `MENU_BACKGROUND_PATH`. See [../_shared/filepaths-modulepaths.md](../_shared/filepaths-modulepaths.md). |
| `MODULEPATHS` | `COMPONENT_MODULE_PATH`, `PROCESSOR_MODULE_PATH`, `SCRIPT_MODULE_PATH`, `COMMAND_MODULE_PATH`, `STATE_MODULE_PATH`, `CONSOLE_COMMAND_MODULE_PATH`. Not defaulted by the engine — the game must supply them. |
| `KEYS` | Game-management keys (`K_CONSOLE_TOGGLE`, `K_SAVE_GAME`, `K_LOAD_GAME`, `K_PAUSE_GAME`), menu-navigation keys, `K_PROFILE` (per-profile action→pygame-key maps), `KEY_FEEDBACK` (`HOLD` / `UP` / `DOWN` per action). |
| `GUI` | `GUI_WINDOW_RATIO`, `MENU_BACKGROUND_ANIMATION_DELAY_MS`, derived `DLG_DIM_PX`, `DLG_START_PX`. |
| `GAME` | Game constants. Engine default supplies only `TILE_RES_PX` (64). `example_game` adds `MOVE_SPEED_PX_PER_SEC` and `DEAD_TIME_TO_DISAPPEAR_MS`. See [../_shared/resolution.md](../_shared/resolution.md). |
| `MESSAGES` | `ON_EVENT`: per-event-type `[format_string, [Event attribute names]]` used by `Event.to_string()`; `DEFAULT_TTL_MS`. An event type absent from `ON_EVENT` produces no in-game message — that is how high-frequency events like `COLLISION` are silenced. |
| `FONTS` / `FRAMES` | Bitmap font / frame filenames, colours and spacing, plus the `_OBJ` instances built in `init()`. |
| `SOUND` | Sound manager settings. |
| `CONSOLE` | `pgconsole` layout: `global`, `header`, `output`, `input`, `footer` sub-dicts. `global.cli_module` names the module whose functions supply header/footer text (defaults to `pgrpg.core.main`; `example_game` uses `pgrpg.core.config.console`). |
| `LOGGING` | A `logging.config.dictConfig` document. See below. |
| `debug` | Per-flag switches read by `PerformRenderDebugInfoProcessor`: `show_health`, `show_state`, `show_weapons`, `show_wearables`, `show_inventory`, `show_labels`, `show_position`, `show_brain`, `show_collision`, `show_direction`, `show_map_screen_area`. Note the **lowercase** section name — unlike every other section, `debug` has no `_prep_conf_` step and no module-level global; it is read straight out of the merged file data by whoever needs it. |

## Logging

`LOGGING` is a standard `dictConfig`. Two things are pgrpg-specific:

- The `in_game_console` handler streams to a **module**, not a file:
  `"stream": "ext://pgrpg.core.config.console"`. That module exposes a `write` function so the
  standard `StreamHandler` can print into the dev console. (The engine default still points at
  `ext://pgrpg.core.managers.console_manager`, a module that no longer exists — the game config
  overrides it. See [../SCOPE.md](../SCOPE.md).)
- The logger names to target are: `core.components`, `core.processors`, `core.commands` (game-side,
  named after `MODULEPATHS`), and `pgrpg`, `pgrpg.core.engine`, `pgrpg.core.config`,
  `pgrpg.core.managers`, `pgrpg.core.ecs`, `pgrpg.core.commands.generators.btree`,
  `pgrpg.core.commands.generators.blist` (engine-side).

Every one of them can be switched to the `null` handler, and the comments in both config files say
why: **file logging at DEBUG is the main frame-rate cost in this engine.** The engine defaults ship
most loggers on `null` "for speed"; `example_game` turns several on. If the game is inexplicably
slow, check the handlers before profiling anything else.

## Related

- [bootstrap-and-loop.md](bootstrap-and-loop.md) — when `load()` and `init()` are called.
- [../_shared/filepaths-modulepaths.md](../_shared/filepaths-modulepaths.md) — how each path and
  module path is consumed.
- [../_shared/resolution.md](../_shared/resolution.md) — `GAME.TILE_RES_PX`.
