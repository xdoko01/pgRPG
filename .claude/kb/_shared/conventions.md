# Conventions for Editing This Repository

> Last updated: 2026-07-30 | Verified by: Source-verified `pyproject.toml`,
> `.github/workflows/python-package.yml`, `tests/conftest.py`, `example_game/game.py`,
> module headers across `pgrpg/` and `example_game/`; Runtime-verified `pytest tests/` →
> **186 passed in 2.26 s** on the bundled `venv/` (Python 3.14.2) @ `c7b9a5f1`

House conventions for *changing* this codebase, as opposed to understanding it. Getting these wrong
produces a technically-correct change that does not fit.

## Stated priorities

From the project's own `CLAUDE.md` and README:

- **Clarity and readability over performance.** Prefer explicit code and clear names. The exceptions
  where performance *was* the deciding factor are commented as such in the source (the event `deque`,
  the `set` conversion in `process_events`, `Map`'s pre-rendered static surfaces, the `__slots__`
  requirement). Follow the same practice: if you optimise, say why in a comment.
- **No new files unless necessary.** Extend an existing component or processor rather than adding one.
- **Aliases everywhere.** Use entity string aliases in data files; let the engine resolve them.

## Environment

| Fact | Value |
|------|-------|
| Package | `pgrpg`, version `0.1.0`, MIT |
| Python floor | **3.9** — `str.removeprefix` in `functions/translate.py` sets it, per the comment in `pyproject.toml` |
| CI matrix | 3.9 – 3.13 on ubuntu-latest |
| Bundled venv | `venv/` (Python 3.14.2) — use `./venv/Scripts/python.exe` on this machine |
| Dependencies | `pygame-ce`, `pygame-gui>=0.6.4`, `pytmx`, `pgbitmapfont>=0.1.5`, `pgconsole>=0.1.1`, `psutil`, `pyyaml`, `toml` |
| Packaged | `pgrpg*` only — `experiments*` and `example_game*` are excluded |

Two modules keep `from __future__ import annotations` specifically so `X | None` annotations work on
3.9 (`ecs_manager.py`, `config/states.py`). Keep that import if you add such an annotation there, or
use `Optional[...]`.

## Running

Always from the **repository root** — `FILEPATHS.GAME_PATH` is relative and
`pgrpg/core/config/defaults.jsonc` is a hardcoded relative path.

```bash
pip install -e .

python example_game/game.py                                    # → dev console (runs default.scr)
python example_game/game.py -s MAIN_MENU                       # → main menu
python example_game/game.py -f games/sokoban/sokoban.jsonc      # → a scene (path relative to SCENE_PATH)
python example_game/game.py -c path/to/other_config.jsonc       # → different config
python example_game/game.py -h
```

> ⚠️ `example_game/game.py:148` passes `state=args.file or state` — the `-f` value is fed to the
> **state** argument. Because `main.init()` checks `scene_file` first, `-f` still works, but combining
> `-f` and `-s` does not do what it looks like.

The dev console (F9 by default, `KEYS.K_CONSOLE_TOGGLE`) is the main introspection tool. Commands live
in `example_game/core/console/commands/`: `get_entities`, `get_components`, `get_processors`,
`get_events`, `proc_perf`, `load_scene`, `init_engine`, `set_value`, `change_res`,
`toggle_fullscreen`, `toggle_cons`, `list_commands`, `exit`. `.scr` scripts in
`core/console/scripts/` are batch files — `script <name>`; `!<python>` evaluates Python inline.

## Testing

```bash
pytest tests/                                              # 186 tests, ~2 s
pytest tests/test_ecs.py::test_processor_execution_control  # one test
python -m core.components.brain -v                         # doctests, run from example_game/
```

`tests/conftest.py` sets `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy` **at import time**, not
in a fixture — `pgrpg.core.config` calls `pygame.init()` at module level and that can happen during
collection. A session-scoped autouse `init_pygame` fixture then calls `pygame.init()`, because
`BTreeBlackboard` and `BListBlackboard` both `assert pygame.get_init()`. Do not move either into a
narrower scope.

Fixtures available: `init_pygame` (autouse), `mock_pygame_ticks` (freezes `get_ticks` at 0),
`simple_graph` (a 4×2 pathfinding grid).

CI additionally runs `python -m doctest -v` over **every** `.py` file and `flake8` with
`--select=E9,F63,F7,F82` as a hard gate (`--max-line-length=127` as warnings only). So a broken
doctest anywhere fails the build.

## Docstring and module style

Both packages follow a consistent shape — copy the nearest neighbour.

**Engine modules** (`pgrpg/`) use Google-style docstrings with an explicit `Module Globals:` section
where the module holds state:

```python
"""One-line summary.

Longer description.

Module Globals:
    _thing: What it holds.
"""
```

**Game modules** (`example_game/`) use reST-ish `:param x:` / `:type x:` blocks plus a `Tests:` block
of doctests, and a `Use 'python -m <module> -v' to run module tests.` line in the module docstring.

Component docstrings additionally carry `Used by:` (the consuming processors) and
`Examples of JSON definition:`. Processor docstrings carry `Involved components:`,
`Related processors:`, `What if this processor is disabled?` and `Where the processor should be
planned?`. **These are load-bearing** — they are the only record of the processor ordering contract.
Fill them in.

## Comment style

Inline comments explain **why**, at length where the reasoning is non-obvious, and they are kept even
when long. Examples of the house style worth imitating:

```python
# deque instead of list: list.pop(0) shifts every remaining element — O(n) per pop,
# meaning draining k events costs O(k²). deque.popleft() is O(1) ...
```

```python
# Keep `X | None` annotations working on Python 3.9, which evaluates them eagerly.
```

When you fix a subtle bug, leave a comment saying what the wrong behaviour was — several already do
(`remove_component`, `Model._resize`, `BList.reset`, `main.run`'s first `dt`).

Commented-out code is used deliberately in two places: the old class-based manager implementations at
the bottom of each manager module, and alternative processor lines in scene files. Do not delete them
as "dead code" without asking.

## Naming

| Thing | Convention |
|-------|------------|
| Component class | `PascalCase` noun / adjective — `Position`, `Collidable`, `Damageable` |
| Component module | `snake_case` matching the class — `collidable.py` → `Collidable` |
| Flag component | `Flag<Phase><Thing>` — see [../ecs/components.md §Flag components](../ecs/components.md#flag-components) |
| Processor class | `<Generate\|Perform\|Remove><Thing>Processor` |
| Processor module | `snake_case` matching the class, inside a `<name>_system/` package |
| Command module | the command name itself — `move_dir.py` is the `move_dir` command |
| Script module | the script name — `load_quest.py` |
| Injected engine callable | `FNC_*` for functions, `REF_*` for module references |
| Template id | `t_` prefix for scene-level templates — `t_crate`, `t_tile_pos` |
| Handler id | `ev_` prefix — `ev_start_game`, `ev_all_crates_in_place` |
| Private module global | leading underscore — `_world`, `_event_queue` |

## Data-file conventions

- `.jsonc` with **indented** `//` comments. Never `//` inside a string literal.
  See [filepaths-modulepaths.md §JSONC](filepaths-modulepaths.md#jsonc-comment-stripping--and-its-limits).
- A `$schema` pointer at the top of every scene file, with the right `../` depth.
- Tile-relative params for world geometry ([resolution.md](resolution.md)).
- Cleanup lists use fnmatch wildcards (`"wall*"`, `"crate*"`, `"*"`).
- Numbered test scenes under `resources/scenes/tests/NN_topic/` — a new subsystem gets the next number
  and a scene that demonstrates only that subsystem plus its prerequisites.

## Git

**The repository owner commits.** Never run `git commit` or `git push` — report the changed files and
let them commit. This is a standing instruction recorded in project memory.

Recent history shows the working pattern: a branch per issue (`fix/80-schema-ref-siblings`,
`fix/77-collision-zones-scale-with-tile-res`), a PR, a merge to `master`, with the commit subject
naming the issue (`Fix #80 $ref beside properties/required disabled params validation`).

## Where not to look

`experiments/` (~30 k lines) is a scratch directory: prototypes of the ECS, behaviour trees, the
console, pathfinding, scrolling, fonts. `experiments/ecs/` is an **older, whole copy** of the engine.
Nothing there is imported by `pgrpg` or `example_game`, it is excluded from the package, and it is
**gitignored** — so it exists only in a working tree that predates the ignore rule, not in a fresh
clone. Do not take it as a reference for current behaviour, and do not update it.

`docs/old/` is likewise historical. `docs/ADR_001_multiplayer_architecture.md` and
`docs/CHANGELOG_ARCHITECTURE.md` are current design documents.

`example_game/core/schemas/components/_old/` holds superseded schemas.

## Related

- [../RULES.md](../RULES.md) — how to maintain this knowledge base alongside a change.
- [filepaths-modulepaths.md](filepaths-modulepaths.md) — running from the right directory.
- [../ecs/components.md](../ecs/components.md) · [../ecs/processors.md](../ecs/processors.md) —
  the per-class conventions.
