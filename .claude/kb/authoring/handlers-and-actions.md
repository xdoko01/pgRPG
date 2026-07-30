# Handlers and Actions

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/functions/json_logic.py`
> (incl. its `__main__` examples), `pgrpg/core/managers/event_manager.py`,
> `pgrpg/core/managers/script_manager.py`, `pgrpg/functions/str_utils.py`,
> `example_game/core/scripts/*.py`; cross-checked against
> `example_game/resources/scenes/games/sokoban/sokoban_level01.jsonc` @ `c7b9a5f1`

A **handler** binds an event type to an **action tree**. The tree is evaluated by `json_logic`, whose
only side-effecting operator is `SCRIPT`.

## Handler syntax

```jsonc
"handlers": [
    ["SCENE_START", {
        "id": "ev_start_game",
        "description": "optional, ignored by the engine",
        "actions": ["SCRIPT", "show_msg_window", {"html_text": "Welcome to <b>%id</b>."}]
    }]
]
```

A two-element list: `[event_type, handler_dict]`.

| Field | Rule |
|-------|------|
| `event_type` | Any string. Not validated — a scene may invent its own types (`CUST_UI_CONFIRM`). |
| `id` | Required. Unique per event type; **re-registering the same id overwrites**. Targeted by `cleanup/handlers` patterns. |
| `actions` | A `json_logic` tree. Absent → the handler does nothing. |
| anything else | Stored and ignored. `description` is conventional. |

All handlers registered for an event type fire, in registration order, when the event is processed.
An event with no handler is silently dropped, as is an event excluded by the
`GameEventsExProcessor`'s `process` / `ignore` filter — see
[../core/events-and-scripts.md §Dispatch](../core/events-and-scripts.md#dispatch).

Handlers can also live nested in a component's `params.handlers` — same syntax, registered globally.
See [ai-definitions.md §Event-driven AI](ai-definitions.md#event-driven-ai).

## `json_logic` operators

`json_logic(expr, value_fnc, script_fnc, data)`. A non-list expression is passed to `value_fnc`
(identity, for handler actions). A list is `[OPERATOR, *args]`, evaluated recursively. Operator
matching is **case-insensitive** (`expr[0].upper()`), so `"if"`, `"If"` and `"IF"` are the same.

| Operator | Arity | Semantics |
|----------|-------|-----------|
| `SEQ` | n | Evaluate every argument, return `None`. **This is how you run several actions.** |
| `IF` | 2 | `["IF", cond, action]` — evaluate `action` only if `cond` is truthy. **No `else` branch.** |
| `SCRIPT` | 2 | `["SCRIPT", "<module>", {kwargs}]` → run the script. |
| `VAR` | 1 | Look up a key in `data` (i.e. `event.params`). Missing key → `None`, never an error. |
| `LIST` | 1 | Return the literal list — needed because a bare list would be parsed as an operator call. |
| `AND` / `ALLOF` | n | `reduce(a and b)` |
| `OR` / `ANYOF` | n | `reduce(a or b)` |
| `ONEOF` | n | True iff **exactly one** argument is `True` (counts literal `True`, so non-boolean truthy values do not count) |
| `IN` | 2 | `item in list` |
| `==`, `!=` | n | `reduce` pairwise — see the caveat below |
| `>`, `>=`, `<`, `<=` | 2 | Strictly binary |

Special cases:

- An **empty list** `[]` returns `True`.
- An unknown operator raises `ValueError: Not supported logical operator: "..."`.
- A list whose first element is not a string raises
  `ValueError: Cannot evaluate the following expression: ...`.

> ⚠️ `==` and `!=` with more than two arguments are `reduce`d, so `["==", a, b, c]` computes
> `(a == b) == c` — comparing a boolean against `c`. Use nested `AND` for three-way equality.

> ⚠️ There is **no `NOT`**. Invert by comparing: `["==", ["VAR", "x"], false]`. Inside a behaviour
> tree, use an `Inverter` node instead.

`LIST` is easy to forget:

```jsonc
["IN", ["VAR", "score"], ["LIST", [10, 20, 30]]]     // correct
["IN", ["VAR", "score"], [10, 20, 30]]               // ValueError — 10 is not an operator
```

### Worked examples from shipped scenes

Run three things in order:

```jsonc
"actions": ["SEQ",
              ["SCRIPT", "load_image", {"image_file": "sokoban_splash.png"}],
              ["SCRIPT", "play_music", {"music_file": "dungeon_theme.flac", "volume": 0.5}],
              ["SCRIPT", "load_quest", {"scene_file": "games/sokoban/sokoban_level01"}]]
```

Conditional on an event param:

```jsonc
"actions": ["IF",
              ["==", ["VAR", "from"], "ev_all_crates_in_place"],
              ["SCRIPT", "load_quest", {"scene_file": "games/sokoban/sokoban_level02"}]]
```

A win condition — every crate must be on target:

```jsonc
["ON_POS_TARGET", {
    "id": "ev_all_crates_in_place",
    "actions": ["IF",
                  ["AND",
                     ["IN", "crate01", ["VAR", "on_target"]],
                     ["IN", "crate02", ["VAR", "on_target"]],
                     ["IN", "crate03", ["VAR", "on_target"]]],
                  ["SEQ",
                     ["SCRIPT", "show_msg_window", {"html_text": "WELL DONE!"}],
                     ["SCRIPT", "show_confirm_dlg", {
                        "title": "Proceed to the next level",
                        "long_desc": "Do you want to proceed?",
                        "event_type": "CUST_UI_CONFIRM",
                        "event_params": {"from": "ev_all_crates_in_place"}}]]]
}]
```

Note what `"crate01"` is doing here. `execute_event_actions` alias-translates the whole tree **before**
evaluation, so by the time `IN` runs, `"crate01"` is an integer id and `["VAR", "on_target"]` is a
list of integer ids. The comparison works because both sides were translated.

The `show_confirm_dlg` script emits a **caller-defined** event (`event_type` + `event_params`) when
the user confirms, which a second handler catches. That is the callback pattern for modal UI, and it
requires the invented event type to be in the `GameEventsExProcessor`'s `process` list.

## Event-param substitution with `%`

`%name` is **not** a `json_logic` feature. It is substituted **inside individual scripts**, by
`translate_str(for_trans=..., trans_dict=event.params, prefix='%')`:

```python
trans_str = for_trans
for k, v in trans_dict.items():
    trans_str = trans_str.replace(prefix + str(k), str(v))
```

Consequences:

- It is a plain textual replace, so `%name` works **inside** a longer string — unlike `$` and `^`,
  which are whole-value only.
- It only works in scripts that call `translate_str`. Currently: `show_msg_window` (`html_text`,
  `title`), `show_confirm_dlg` (`long_desc`), `add_msg` (`text`), `set_bb_value` (`entity`,
  `bb_value`). Passing `%id` to any other script leaves the literal `%id`.
- Replacement is **unordered and unanchored**: a param named `id` will also rewrite the `%id` inside
  `%identifier`. Prefer distinct param names.
- An unmatched `%name` is shown to the player verbatim.

The `SCENE_START` params available for substitution (from `Scene.stats` and metadata) are `filepath`,
`id`, `alias`, `title`, `description`, `objective`, `stats`. The near-universal scene-start handler:

```jsonc
["SCENE_START", {
    "id": "ev_scene_start",
    "actions": ["SCRIPT", "show_msg_window", {
        "title": "%filepath",
        "html_text": "<b>Scene ID:</b> %id<br/><b>Title:</b> %title<br/><b>Description:</b> %description<br/><b>Objective:</b> %objective<br/><br/><b>Stats:</b> %stats"}]
}]
```

`html_text` is rendered by `pygame_gui`'s `UIMessageWindow`, so a useful subset of HTML works
(`<b>`, `<br/>`, `<i>`, `<font>`).

## The three prefixes at a glance

| | Resolved against | Resolved when | Whole value only? | On miss |
|---|---|---|---|---|
| `$var` | template arguments | template expansion (load) | yes | left as literal → usually a component `ValueError` |
| `^key` | generator global blackboard | command's first tick | yes | **`KeyError`** |
| `%key` | `event.params` | inside the script | no — substring | left as literal, shown to the player |

Plus the prefix-less, unconditional **entity alias translation** applied to every params dict and
every action tree. See [../_shared/aliases.md](../_shared/aliases.md).

## Available scripts

Referenced as `["SCRIPT", "<name>", {kwargs}]`. Names come from the module name under
`MODULEPATHS["SCRIPT_MODULE_PATH"]`, plus any extra alias the module registers.

| Script | Key kwargs |
|--------|-----------|
| `show_msg_window` | `html_text`, `title` — **modal**, runs its own loop until dismissed |
| `show_confirm_dlg` | `title`, `long_desc`, `event_type`, `event_params` — modal; emits the given event on confirm |
| `show_dlg_window` | dialog id from `dialog_manager` |
| `add_msg` | `text` (+ TTL) → the in-game message log |
| `load_quest` | `scene_file` — additive load (`clear_before_load=False`) |
| `restart_quest` | — reload the current scene |
| `load_image` | `image_file` |
| `play_music` | `music_file`, `volume` |
| `fade_in`, `shake_screen` | visual effects |
| `set_bb_value` | `entity`, `bb_key`, `bb_value`, `only_if_not_set` |
| `restart_brain`, `modify_brain` | AI control |
| `disable_teleport` | — |
| `exec_python_code` | arbitrary Python — dev/debug only |
| `exit` | quit the game |
| `do_nothing` | placeholder |
| `condition_always_true`, `condition_example` | condition-script examples |

Plus `collect_coins/` and `kill_all/` game-specific script packages. Full list:
[../reference/index.md §Scripts](../reference/index.md#scripts).

To add one, write a module with `initialize(register, name)` — see
[../core/events-and-scripts.md §The script module contract](../core/events-and-scripts.md#the-script-module-contract).

## Debugging a handler that does not fire

Check, in this order:

1. Is a `GameEventsExProcessor` in the scene's `processors` list at all?
2. Is the event type in its `process` list (or absent from its `ignore` list)? Filtered events are
   **dropped**, not deferred.
3. Is the handler's `id` unique? A later handler with the same id for the same event type overwrote it.
4. Did a `cleanup/handlers` pattern in a later-loaded scene remove it? `["*"]` removes everything.
5. Is the event actually emitted? Grep for `Event('YOUR_TYPE'` — the list of emitted types is in
   [../core/events-and-scripts.md §Event types](../core/events-and-scripts.md#event-types-in-practice).
6. Is an operator raising? An unknown operator raises `ValueError` from inside event processing.

## Related

- [../core/events-and-scripts.md](../core/events-and-scripts.md) — the dispatch machinery.
- [ai-definitions.md](ai-definitions.md) — handlers nested in `BrainAI`.
- [scene-format.md §handlers](scene-format.md#handlers) — placement in the scene file.
