# Where the Engine Looks for What

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/config/__init__.py`
> (`_prep_conf_filepaths`), `pgrpg/functions/get_dict_from_file.py`,
> `pgrpg/functions/get_dict_from_json.py`, `pgrpg/functions/get_class_object.py`,
> and every manager's load function; `example_game/config.jsonc` @ `c7b9a5f1`

Two config sections decide where the engine looks: `FILEPATHS` for **data** and `MODULEPATHS` for
**Python code**.

## `FILEPATHS`

`_prep_conf_filepaths` prefixes every entry with `GAME_PATH` and wraps it in a `pathlib.Path`, except
`GAME_PATH` and `pgrpg_PATH` themselves:

```python
for path_name, path_rel in filepaths_config.copy().items():
    filepaths_config[path_name] = (Path(filepaths_config["GAME_PATH"], path_rel)
                                   if path_name not in ("GAME_PATH", "pgrpg_PATH")
                                   else Path(path_rel))
```

`GAME_PATH` and `pgrpg_PATH` are **mandatory in the game config** — the engine defaults do not supply
them.

| Key | Default (under `GAME_PATH`) | Consumed by | Referenced from data as |
|-----|------------------------------|-------------|------------------------|
| `SCENE_PATH` | `resources/scenes/` | `engine.load_scene_from_file` | `-f` CLI arg; `prereqs`; `load_quest`'s `scene_file` |
| `ENTITY_PATH` | `resources/entities/` | `ecs_manager.load_stored_template` → `get_dict_params` | an entry in an entity's `templates` |
| `BTREE_PATH` | `resources/btrees/` | `BrainAI` → `BTree(template_path=...)` | a btree node's `template` key |
| `MAP_PATH` | `resources/maps/` | `Map.__init__` | an entry in a scene's `maps`; a `Position`'s `map` param |
| `MODEL_PATH` | `resources/models/` | `RenderableModel` → `load_model` | `RenderableModel`'s `model` param |
| `DIALOG_PATH` | `resources/dialogs/` | `dialog_manager.load_dialog` | a dialog's `templates` |
| `IMAGE_PATH` | `resources/images/` | console backgrounds, `load_image` script | `image_file` |
| `SOUND_PATH` | `resources/sounds/` | `sound_manager` | `SoundFX*` components' `sound` param |
| `MUSIC_PATH` | `resources/music/` | `play_music` script | `music_file` |
| `FONT_PATH` | `resources/fonts/` | `_prep_conf_fonts`, `_prep_conf_console` | `FONTS` config values |
| `FRAME_PATH` | `resources/frames/` | `_prep_conf_frames` | `FRAMES` config values |
| `LOG_PATH` | `logs/` | declared, but `LOGGING` handler filenames are prefixed with **`GAME_PATH`**, not `LOG_PATH` — `example_game` writes `"filename": "logs/components.log"` to compensate |
| `SAVE_PATH` | `save/` | reserved — save/load is unimplemented |
| `CONSOLE_SCRIPT_PATH` | `core/console/scripts/` | `_prep_conf_console` → `pgconsole` | `script <name>` in the dev console |
| `MENU_BACKGROUND_PATH` | `resources/images/menu_background/waterfall/` | `gui.init_background_animation` | — |

`GAME_PATH` is `"example_game"` — a **relative** path. Combined with the hardcoded
`pgrpg_DEFAULT_CONFIG_FILEPATH = Path("pgrpg/core/config/defaults.jsonc")`, this means the game must
be launched from the repository root:

```bash
python example_game/game.py -f games/sokoban/sokoban.jsonc     # correct
cd example_game && python game.py                              # will not find defaults.jsonc
```

Note the `-f` path is relative to `SCENE_PATH`, not to the CWD.

## `MODULEPATHS`

Dotted Python module paths, resolved with `importlib.import_module`, so they must be importable from
the process's `sys.path`. `example_game/game.py` prepends its own directory to `sys.path` before
importing `pgrpg`, which is why `"core.components"` (rather than `"example_game.core.components"`)
works.

| Key | `example_game` value | Resolves | Reference form |
|-----|----------------------|----------|----------------|
| `COMPONENT_MODULE_PATH` | `core.components` | `get_class_from_def(def, path)` | `"module:ClassName"` in a component's `type` |
| `PROCESSOR_MODULE_PATH` | `core.processors` | `get_class_from_def(def, path)` | `"module:ClassName"` in a scene's `processors` |
| `SCRIPT_MODULE_PATH` | `core.scripts` | `import_module(f"{path}.{name}")` | `["SCRIPT", "<name>", {...}]` |
| `COMMAND_MODULE_PATH` | `core.commands` | `str_to_package_module(None, f"{path}.{name}")` | `["<name>", {params}]` in a `command` |
| `STATE_MODULE_PATH` | `core.states` | `import_module(f"{path}.{state.name.lower()}")` | implicit — one module per `State` |
| `CONSOLE_COMMAND_MODULE_PATH` | `core.console.commands` | `pgconsole` | a word typed in the dev console |

The engine defaults supply **no** `MODULEPATHS`; a game must define all six (a missing one raises
`KeyError` when first needed).

### Class resolution

`get_class_from_def(class_def, class_package)`:

```python
module, name = class_def.split(':')
return get_class_object(None, class_package + '.' + module, name)
```

So `"collision_system.remove_flag_has_collided_processor:RemoveFlagHasCollidedProcessor"` becomes
`core.processors.collision_system.remove_flag_has_collided_processor.RemoveFlagHasCollidedProcessor`.
Dots navigate packages; the colon separates module from class. A class re-exported from a package
`__init__.py` can be addressed by the package alone — `"collision_system:GenerateCollisionsProcessor"`
— and those re-exports **rename** (see
[../authoring/scene-format.md §processors](../authoring/scene-format.md#processors)).

Missing colon → the unpacking raises `ValueError`, and the handler's error message itself references
an unbound `name`, producing a confusing `UnboundLocalError`. Always include the colon.

## File format detection

`get_dict_from_file(filepath, dir=Path(''))`:

- An **absolute** `filepath` is used as-is; a relative one is resolved as `dir / filepath`.
- With a suffix, it dispatches on it: `.toml`, `.yaml`, `.json`, `.jsonc`.
- **Without** a suffix it tries, in order: `.toml`, `.yaml`, `.json`, `.jsonc`.

That fallback chain is why scene and template references can omit the extension —
`"games/sokoban/sokoban"` finds `sokoban.jsonc`.

> ⚠️ **An explicit `.toml` suffix does not work.** `get_dict_from_file.py:46-51` opens the `.toml`
> branch with `if` where the others use `elif`, so after parsing the TOML the chain falls through to
> the `else` guess-the-extension branch, which then looks for `t.toml.toml`, `t.toml.yaml`,
> `t.toml.json`, `t.toml.jsonc` and raises `ValueError: Cannot load dict from file ...`.
> Runtime-verified: `get_dict_from_file(Path('t.toml'))` raises, while
> `get_dict_from_file(Path('t'))` on the same file returns `{'a': 1}` — **omit the suffix for TOML.**
>
> `.yml` is not recognised either; it takes the guess path and fails. Use `.yaml`.

## JSONC comment stripping — and its limits

`get_dict_from_json` strips C-style comments with a single regex before parsing:

```python
json.loads(re.sub("[^:]//.*", "", json_data, flags=re.MULTILINE))
```

This is why `.jsonc` works everywhere in this project. Understand the pattern's shape:

Runtime-verified behaviour:

- `[^:]` requires **one non-colon character before the `//`**, which is what preserves `"http://..."`
  inside a string. It also **consumes that character**, so `x//comment` loses the `x`. In practice a
  comment is preceded by a space, a tab, a comma or a newline, so the loss is invisible.
- A comment in **column 0** still works — the preceding newline is the consumed character. Only a `//`
  at byte 0 of the file would survive unstripped.
- A `//` **inside a string value is stripped**, truncating the value:
  `{"u": "a//b"}` → `{"u": "` → `json.JSONDecodeError`. Never put `//` in a string literal except
  after a colon-adjacent character, as in a URL.
- `/* ... */` block comments are **not** supported.
- Trailing commas are not permitted — this is still `json.loads` underneath.

YAML files go through `pyyaml` and support native YAML comments with none of these caveats;
`tests/04_collisions/test_collisions_05.yaml` is the reference.

## Storage-before-file lookup

`get_dict(dictpath, storage, dir)` — used for templates — checks the in-memory `storage` dict **first**
(via `get_dict_value(d=storage, path=dictpath, sep='/')`) and only then the filesystem. So a
scene-defined template id, or a loaded entity's alias, **shadows** a file of the same name. Keep the
two namespaces distinct. See [aliases.md §The two sharp edges](aliases.md#the-two-sharp-edges).

## Related

- [../core/configuration.md](../core/configuration.md) — how these sections are prepared.
- [../authoring/index.md](../authoring/index.md) — what lives in each data directory.
- [conventions.md](conventions.md) — running the game and the tests.
