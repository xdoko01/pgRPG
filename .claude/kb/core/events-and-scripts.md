# Events, Handlers and Scripts

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/managers/event_manager.py`,
> `pgrpg/core/managers/script_manager.py`, `pgrpg/core/events/event.py`,
> `pgrpg/functions/json_logic.py`, `example_game/core/processors/event_system/game_events_processor.py`,
> `example_game/core/scripts/*.py`; the emitted event-type set re-derived from every
> `Event(...)` construction in `pgrpg/` and `example_game/` (#98) @ `093af889`

Events are how the ECS talks to the **data layer**. A processor detects something, enqueues an
`Event`, and the scene file decides what happens — without any Python change.

## The `Event` object

`pgrpg/core/events/event.py`:

```python
Event(event_type, generator_obj, other_obj, params={})
```

| Field | Meaning |
|-------|---------|
| `event_type` | String, e.g. `"COLLISION"`. **Not validated** — the `EVENT_TYPES` list exists but the assertion against it is commented out, so any string works. |
| `generator_obj` | Entity id that caused the event (or `None`). |
| `other_obj` | Entity id of the other participant (or `None`). |
| `params` | Dict passed to handlers as the `json_logic` data context. |

`Event.to_string()` formats a human-readable message using `MESSAGES["ON_EVENT"][event_type]`:
a `[format_string, [attribute_names]]` pair, where the attribute names are `Event` attributes
(`"generator_obj"`, `"other_obj"`) resolved to **aliases**, not ids. An event type absent from
`ON_EVENT` formats to `""` — that is the mechanism for silencing high-frequency events.

`event_manager.create_event(type, params)` is a convenience constructor that leaves both entity
fields `None`.

## The queue

`_event_queue` is a `collections.deque`. The choice is deliberate and documented in the source:
`list.pop(0)` shifts every remaining element (O(n) per pop, O(k²) to drain k events), while
`deque.popleft()` is a pointer move. Collision and damage processors enqueue continuously, so this
is on the hot path.

```python
add_event(event)      # append, O(1)
get_events()          # returns the live deque
clear_events()        # deque has no slice deletion — uses .clear()
```

## The handler registry

`_event_handlers` is `{event_type: {handler_id: {**everything except id}}}`.

`load_handler(handler_def)` takes a **two-element list**:

```jsonc
["SCENE_START", {
    "id": "ev_start_game",
    "actions": ["SCRIPT", "show_msg_window", {"html_text": "Hello"}]
}]
```

The `id` is popped out and used as the dict key; the rest of the dict becomes the value. So
re-registering the same `id` for the same event type **overwrites** — that is how an additively
loaded scene replaces a base scene's handler.

| Function | Behaviour |
|----------|-----------|
| `load_handler([type, data])` | Register / overwrite. |
| `delete_handler(handler_id)` | Remove that id from **every** event type. |
| `delete_handlers_pattern(pattern)` | fnmatch-based bulk removal (used by `cleanup/handlers`). |

Handlers can live in two places in a scene file: the top-level `handlers` key, and nested inside a
component's `params` — both are picked up by the pipeline. See
[scene-pipeline.md §The pipeline](scene-pipeline.md#the-pipeline).

## Dispatch

Nothing dispatches events automatically. A processor must call `process_events` — in the example
game that is `GameEventsExProcessor`, placed explicitly in the scene's `processors` list:

```jsonc
["event_system.game_events_processor:GameEventsExProcessor",
 {"process": ["SCENE_START", "ON_POS_TARGET", "CUST_UI_CONFIRM"]}]
```

`process_events(process=None, ignore=None)` drains the whole queue every call:

- `ignore` is checked first. An ignored event is **discarded, not deferred**.
- If `process` is given, event types not in it are also **discarded**.
- Both lists are converted to `set`s once per call, before the loop, so membership tests are O(1).

> ⚠️ Filtered-out events are dropped, not requeued. A scene with two `GameEventsExProcessor`s
> handling disjoint `process` lists will lose events to whichever runs first. Use one processor with
> the union of the types you care about.

There is also a `GameEventsProcessor` (no `Ex`) in the same module which calls
`game_event_handler()` with no filters and never calls `super().process()` — so it cannot be
throttled with `step` and is not exported by the module's `__all__`. Prefer the `Ex` variant.

### Fan-out: one event, many handlers

`_process_event` (`event_manager.py:145`) collects the `actions` of **every** handler registered for
that event type, and only then executes them:

```python
event_handlers = _event_handlers.get(event.event_type, _EMPTY).values()
_actions_for_execution = [h.get('actions', []) for h in event_handlers]
for action in _actions_for_execution:
    _exec_event_actions_fnc(event, action)
```

The two-phase collect-then-execute is not an optimisation — it is required. A handler action such as
`load_quest` re-enters the scene pipeline and mutates `_event_handlers`, which would invalidate the
iterator mid-loop. Collecting first makes that safe.

Handler execution order within one event type is dict insertion order, i.e. registration order.

## From actions to Python: `script_manager`

`event_manager` calls `script_manager.execute_event_actions` (wired at `engine.py:49`):

```python
def execute_event_actions(event, actions):
    translated_actions = translate(_alias_to_entity_dict_fnc(), actions)
    json_logic(expr=translated_actions,
               value_fnc  = lambda x: x,
               script_fnc = lambda *args: execute_script(args[0], event, **args[1]),
               data       = event.params)
```

Three things happen, in this order:

1. **Alias translation.** Every string in the action tree that matches a registered entity alias is
   replaced by its integer id, recursively through dicts/lists/tuples
   (`pgrpg/functions/translate.py`). This is why script arguments can name entities.
2. **`json_logic` evaluation** of the tree, with `event.params` as the `VAR` data context.
3. **`SCRIPT` nodes** call `execute_script(name, event, **kwargs)`.

> ⚠️ Alias translation is blind: it substitutes *any* string equal to an alias, including dict keys'
> values that were never meant as entity references. Avoid naming an entity after a word you also
> use as a literal action argument.

### Lazy script loading

`execute_script(script_module_name, *args, **kwargs)`:

```python
script_fnc = _scripts.get(script_module_name)
if not script_fnc:
    module = import_module(f"{MODULEPATHS['SCRIPT_MODULE_PATH']}.{script_module_name}")
    module.initialize(register_script, script_module_name)
    script_fnc = _scripts.get(script_module_name)
return script_fnc(*args, **kwargs)
```

A script module is imported on **first use** and cached in `_scripts` thereafter.
`clear_scripts()` empties the registry (called by `_clear_game()`).

### The script module contract

```python
def initialize(register, name):
    register(fnc=_run, alias=name)          # mandatory — register under the module name
    register(fnc=_run, alias='nicer_name')  # optional extra aliases

def _run(event, *args, **kwargs):
    # event      — the triggering Event; event.params holds the payload
    # kwargs     — the action's argument dict from the scene JSON
    return 0
```

Placed under `MODULEPATHS["SCRIPT_MODULE_PATH"]` (`core.scripts` in the example game). Referenced
from a handler as `["SCRIPT", "<module_name>", {args}]`.

Note the arity: the registered function is called as `script_fnc(event, **kwargs)`, so `event` is
positional-first. Several shipped scripts register themselves under two names (module name plus a
short alias) so a rename does not break scenes.

Scripts shipped with the example game: `add_msg`, `condition_always_true`, `condition_example`,
`disable_teleport`, `do_nothing`, `exec_python_code`, `exit`, `fade_in`, `load_image`, `load_quest`,
`modify_brain`, `play_music`, `restart_brain`, `restart_quest`, `set_bb_value`, `shake_screen`,
`show_confirm_dlg`, `show_dlg_window`, `show_msg_window`, plus `collect_coins/` and `kill_all/`
game-specific packages. See [../reference/index.md §Scripts](../reference/index.md#scripts).

### Scripts can block the loop

`show_msg_window` and `show_confirm_dlg` run their **own** inner pygame loop until the dialog is
dismissed, drawing and flipping the display themselves. The outer frame loop is suspended for the
duration. That is the engine's modal-dialog mechanism; it also means a script can starve the game if
its loop never exits.

## `json_logic` in one line

`json_logic(expr, value_fnc, script_fnc, data)` (`pgrpg/functions/json_logic.py`) evaluates a
JSON-encoded tree. A non-list expression is passed to `value_fnc`; a list is `[OPERATOR, *args]`
evaluated recursively. An empty list returns `True`. An unknown operator raises `ValueError`.

The same evaluator serves two very different jobs:

| Caller | `value_fnc` | `script_fnc` | Purpose |
|--------|-------------|--------------|---------|
| `script_manager.execute_event_actions` | identity | run a script module | Execute handler actions. |
| `ecs_manager.check_processor` | `check_proc_in_world` | default no-op | Evaluate a processor's `PREREQ` expression. |

Operator reference lives in
[../authoring/handlers-and-actions.md §json_logic operators](../authoring/handlers-and-actions.md#json_logic-operators).

## Event types in practice

Emitted by engine/game code (grepped from every `Event(...)` construction): `SCENE_START`,
`COLLISION`, `TELEPORTATION`, `ITEM_PICKUP`, `ITEM_DROP`, `WEAPON_ARMED`, `WEAPON_DISARMED`,
`WEAPON_SET_INTO_USE`, `AMMO_PACK_ARMED`, `AMMO_PACK_DISARMED`, `DAMAGE`, `KILLED`, `DESTROYED`,
`SCORE`, `ON_POS_TARGET`, `ON_BUTTON_PRESSED`, `CAN_SEE`, `CAN_HEAR`.

`Event.EVENT_TYPES` is exactly that list since #98; it used to carry `WEARABLE_WEARED`, `KILL` and
`PHASE_START`, which nothing emits. It remains **documentation only** — the `assert` in `Event.__init__`
is commented out, and it cannot become a closed set while scenes invent their own types (see
`CUST_UI_CONFIRM` below).

> ⚠️ `KILLED` has **no** `MESSAGES.ON_EVENT` template, so a kill still produces no in-game message.
> The dead `KILL` key was deleted rather than renamed. `ITEM_DROP`, `WEAPON_DISARMED`,
> `WEAPON_SET_INTO_USE`, `DESTROYED`, `ON_POS_TARGET`, `ON_BUTTON_PRESSED` are silent for the same
> reason; for `CAN_SEE` / `CAN_HEAR` that silence is deliberate.

Handled in shipped scenes: `SCENE_START` (83 handlers), `WEAPON_ARMED`, `CUST_UI_CONFIRM`,
`ITEM_PICKUP`, `ON_BUTTON_PRESSED`, `AMMO_PACK_ARMED`, `SCORE`, `DESTROYED`, `ON_POS_TARGET`.

`CUST_UI_CONFIRM` is **not** an engine event type — it is a name a scene invents and the
`show_confirm_dlg` script emits back, via that script's `event_type` / `event_params` arguments. Any
string works as an event type, so scenes can define their own protocol. See
[../reference/index.md §Event types](../reference/index.md#event-types).

## Related

- [../authoring/handlers-and-actions.md](../authoring/handlers-and-actions.md) — handler and action syntax.
- [managers.md](managers.md) — how a processor gets `FNC_ADD_EVENT` / `game_event_handler`.
- [commands-and-ai.md](commands-and-ai.md) — the parallel path for entity commands.
