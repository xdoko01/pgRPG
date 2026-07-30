# Entity Aliases

> Last updated: 2026-07-30 | Verified by: Source-verified `pgrpg/core/managers/ecs_manager.py`,
> `pgrpg/functions/translate.py`, `pgrpg/core/managers/script_manager.py`,
> `pgrpg/core/commands/__init__.py` (`cmd_factory`) @ `c7b9a5f1`;
> Test-verified `tests/functions/test_translate.py`

An **entity in the ECS is an integer.** An **alias** is the string name a data file uses for it. The
translation between them is the seam between the data layer and the engine, and it is worth
understanding precisely because it is both convenient and slightly dangerous.

## The two lookup tables

`ecs_manager` keeps two module-level dicts, maintained in lockstep:

```python
_alias_to_entity = {"player01": 1, "crate01": 2, ...}
_entity_to_alias = {1: "player01", 2: "crate01", ...}
```

| Function | Direction |
|----------|-----------|
| `get_entity_id(alias)` | alias → id, or `None`. Returns `None` for an unhashable argument rather than raising. |
| `get_entity_alias(id)` | id → alias, or `None`. Same tolerance. |
| `get_alias_to_entity_dict()` | the whole `_alias_to_entity` dict — this is what `script_manager` holds a callback to |
| `check_lookup_tables()` | `True` if the two dicts are the same length |
| `get_entities_with_alias()` / `get_entities_wo_alias()` | diagnostics |

Registration happens in `_create_empty_entity`, un-registration in `delete_entity`. Un-registration
swallows `KeyError`, so deleting an entity that was never aliased is fine.

**An entity can exist without an alias.** `_create_empty_entity(entity_alias=None)` creates the entity
and skips registration — that is how anonymous runtime entities (some factory output) work. Those
entities are invisible to alias translation and can only be reached by an id that some component holds.

## Aliases are not unique per scene — they are unique per world

`_create_empty_entity` returns the **existing** id if the alias is already registered:

```python
entity_id = get_entity_id(entity_alias=entity_alias)
if entity_id is not None:
    logger.info(f'Entity alias "{entity_alias}" already exists for {entity_id=}. Skipping ...')
    return entity_id
```

This is deliberate and is what makes additive scene loading work: a level scene loaded on top of a
base scene can *extend* an entity the base already created, simply by reusing its `id`. It also means
two unrelated scenes that happen to use `"player01"` will collide when loaded together.

`_clear_game()` clears both tables via `_clear_entities_and_components()`.

## Translation: `translate()`

`pgrpg/functions/translate.py`. One recursive function, used in three places with three different
configurations.

```python
translate(trans_dict, value, prefix='')
```

It walks dicts (values only, not keys), lists and tuples, preserving structure, and at each leaf:

| `prefix` | Leaf behaviour |
|----------|----------------|
| `''` (default) | `trans_dict.get(value, value)` — substitute if found, **pass through unchanged if not** |
| set, e.g. `'^'` | Only strings starting with the prefix are considered; the prefix is stripped and the lookup **must** succeed or `KeyError` is raised |

A non-prefix `KeyError` is re-raised as-is (the message is meaningful); any other exception becomes
`ValueError(f'Cannot translate "{value}" by using translation dictionary "{trans_dict}"')`.

### The three call sites

| Call site | `trans_dict` | `prefix` | Purpose |
|-----------|--------------|----------|---------|
| `ecs_manager.create_component_from_def` | `_alias_to_entity` | `''` | Alias → id in component params |
| `script_manager.execute_event_actions` | `_alias_to_entity` (via callback) | `''` | Alias → id in handler action trees |
| `command_manager.execute_command_init` | `cmd_ctx.globals.__dict__` | `'^'` | Blackboard lookup in command params |
| `get_dict_params` | template `vars` map | `''` | `$var` → argument value |

So the *same* function implements alias translation, blackboard lookup and template substitution. The
`prefix` argument is the only difference, and it also flips the missing-key behaviour from
"pass through" to "raise".

## Why entities are loaded in two passes

Component params are translated **at construction time**. A component that references `"player01"`
can only resolve it if `player01` is already in `_alias_to_entity`.

The scene pipeline therefore runs `entities` twice: pass 1 creates every entity and registers every
alias; pass 2 fills in components. The result is that **every entity in a scene can reference every
other, in any order**:

```jsonc
{"id": "player01", "components": [
    {"type": "has_weapon:HasWeapon",
     "params": {"weapons": {"bow": {"weapon": "wooden_bow", "generator": "wooden_arrows_pack"}}}}]},
{"id": "wooden_bow", "components": [...]},              // declared later — still resolves
{"id": "wooden_arrows_pack", "components": [...]}
```

Details: [../core/scene-pipeline.md §Two-pass](../core/scene-pipeline.md#two-pass-entity-loading).

The exception is **entity-as-template**: `{"id": "crate02", "templates": ["crate01"]}` requires
`crate01` to appear *earlier* in the list, because templates are applied during pass 2, in list order.
Alias *references* are order-independent; template *inheritance* is not.

## Where translation happens — and where it does not

| Stage | Translated? |
|-------|-------------|
| Component `params` (any depth) | **Yes** |
| Handler `actions` trees (any depth) | **Yes** |
| Command params via a generator | **No** — must already be ints (see below) |
| Template `vars` arguments | Only `$var` substitution; alias translation happens later, when the resulting component is built |
| Processor params in a scene | **No** — passed to the constructor verbatim |
| Map, dialog, model names | **No** — those are not entity aliases |

Because processor params are *not* translated, a processor cannot take an entity alias in its scene
configuration. It must resolve one itself via `FNC_GET_ENTITY_ID`.

### Commands require pre-translated ints

`cmd_factory` asserts it:

```python
entity_id_from_cmd = cmd[1].pop('entity', None)
assert entity_id_from_cmd is None or isinstance(entity_id_from_cmd, int), \
    f'Entity alias "{entity_id_from_cmd}" is not translated to int!'
```

and `add_command` asserts the resolved target too:

```python
assert isinstance(entity_id, int), 'Here entity should be already translated, but it is not.'
```

Commands inside a `BrainAI`'s `cmd_tree` / `cmd_list` are fine because the whole component params dict
was translated when the component was constructed. A command assembled at runtime from a raw string
is not — translate it first.

## The two sharp edges

**1. Translation is unconditional and matches on exact string equality.** Any string value equal to a
registered alias is replaced, whether or not you meant it as an entity reference:

```jsonc
// if some entity is aliased "bow", this silently becomes {"type": 7}
{"type": "weapon_in_use:WeaponInUse", "params": {"type": "bow"}}
```

Keep entity aliases distinct from words you use as literal param values. The example game's habit of
suffixing aliases (`wooden_bow_for_NPC`, `wooden_arrows_pack_for_player`) is partly for this reason.

**2. Aliases and template file paths share a namespace.** Every loaded entity is registered as a
template under its own alias, and `get_dict` checks storage **before** the filesystem. An entity
aliased `model/body/male/human/white` would shadow the file of that name. Keep them separate.

## Debugging

```python
ecs_manager.get_alias_to_entity_dict()   # the whole table
ecs_manager.get_entities_wo_alias()      # entities you cannot name
ecs_manager.check_lookup_tables()        # tables consistent?
ecs_manager.get_debug_info()             # pretty-printed world + tables
```

All reachable from the dev console (`get_entities`, `get_components`). Symptoms and causes:

| Symptom | Likely cause |
|---------|--------------|
| A component receives a string where an id was expected | The alias was not registered — check spelling and that the entity is in the same world |
| `KeyError: Cannot find value '^x' in the translation dictionary` | Blackboard key missing, not an alias problem |
| `AssertionError: Entity alias "..." is not translated to int!` | A command param carrying a raw alias reached `cmd_factory` |
| A literal param value turned into a number | Alias collision — sharp edge 1 above |

## Related

- [../core/scene-pipeline.md](../core/scene-pipeline.md) — the two passes.
- [../authoring/entity-and-template.md](../authoring/entity-and-template.md) — `id` and templates.
- [../authoring/index.md §Three prefixes](../authoring/index.md#the-three-substitution-prefixes)
- [../core/commands-and-ai.md](../core/commands-and-ai.md) — the `^` blackboard prefix.
