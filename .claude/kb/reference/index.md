# Reference — Inventories

> Last updated: 2026-07-30 | Verified by: Source-verified by enumerating
> `example_game/core/{components,processors,commands,scripts,states,console}/**` and grepping every
> `Event(...)` construction @ `c7b9a5f1`

Flat lists of everything the reference game defines, so you can find the right name without grepping.
These are `example_game` inventories — a different game supplies its own.

**Authoritative details live in each module's docstring.** This page is an index, not a spec.

---

## Components

`example_game/core/components/` — 86 modules, 88 `Component` classes. Reference in JSON as
`"<module>:<ClassName>"`.

### Identity and world state

| Module | Class | Purpose |
|---|---|---|
| `position` | `Position` | `x`/`y` in px (or `tile_x`/`tile_y`), `map`, `dir_name`, `direction` |
| `movable` | `Movable` | `velocity`, `accelerate` |
| `collidable` | `Collidable` | Collision zone + six allow/deny lists + walkaround mode |
| `camera` | `Camera` | Viewport surface, offset, `always_center`, `screen_fill` |
| `renderable_model` | `RenderableModel` | Binds an animated model file; current action/direction/frame |
| `render_data_from_parent` | `RenderDataFromParent` | Inherit render state from a parent entity |
| `debug` | `Debug` | Free-form `info` dict rendered by the debug overlay |

### Combat and survival

| Module | Class |
|---|---|
| `damageable` | `Damageable` (`health`) |
| `damaging` | `Damaging` (`damage`) |
| `weapon` | `Weapon` (`type`, `max_projectiles`) |
| `weapon_in_use` | `WeaponInUse` (`type`) |
| `has_weapon` | `HasWeapon` (`weapons` map of type → `{weapon, generator}`) |
| `ammo_pack` | `AmmoPack` (`weapon`, `type`) |
| `factory` | `Factory` (`prescription` — a full entity definition) |
| `is_destroyed` | `IsDestroyed` |
| `destroy_on_collision` | `DestroyOnCollision` (`ttl`) |
| `destroy_on_no_health` | `DestroyOnNoHealth` (`ttl`) |
| `destroy_on_no_movement` | `DestroyOnNoMovement` (`ttl`) |

### AI and control

| Module | Class | Note |
|---|---|---|
| `brain_ai` | `BrainAI` | **Current.** `cmd_tree` → BTree, `cmd_list` → BList |
| `brain` | `Brain` | Superseded index-based command list |
| `btree_ai` | `BTreeAI` | Superseded — use `BrainAI` |
| `blist_ai` | `BListAI` | Superseded — use `BrainAI` |
| `controllable` | `Controllable` | `key_profile`, `key_feedback`, `control_cmds` |
| `can_see` | `CanSee` | `angle`, `distance_tiles` |
| `can_hear` | `CanHear` | `distance_tiles` |
| `has_target_position` | `HasTargetPosition` | `targets`: `[map, tile_x, tile_y, tolerance_px]` |

### Items, inventory, scoring

| Module | Class |
|---|---|
| `pickable` | `Pickable` |
| `has_inventory` | `HasInventory` |
| `has_score` | `HasScore` |
| `scorable_on_pickup` / `scorable_on_damage` / `scorable_on_no_health` | `ScorableOnPickup` / `ScorableOnDamage` / `ScorableOnNoHealth` |
| `teleport` | `Teleport` (destination + optional key requirement) |
| `teleportable` | `Teleportable` |

### Effects

`sound_fx_on_{arm_weapon,collision,creation,damage,generation,movement,no_health}` →
`SoundFXOn*` (`sound`, `volume`).
`visual_fx_on_{collision,creation,damage,generation,no_health}` → `VisualFXOn*` (`effect`).

### GUI

`gui_button` → `GUIButton`; `gui_pressable` → `Pressable`; `gui_flag_was_pressed` →
`GUIFlagWasPressed`.

### Flag components (39)

Transient markers, one frame long. Naming decodes the phase — see
[../ecs/components.md §Flag components](../ecs/components.md#flag-components).

`FlagDoMove`, `FlagDoAttack` ·
`FlagIsAboutTo{ArmAmmo,ArmWeapon,BeDamagedBy,BeTeleportedBy,DisarmAmmo,DisarmWeapon,DropEntity,PickEntity}` ·
`FlagHas{ArmedAmmo,ArmedWeapon,Collided,Damaged,DisarmedAmmo,DisarmedWeapon,Dropped,NoHealth,Picked,Scored,StoppedMovement,Teleported}` ·
`FlagWas{ArmedAsAmmoBy,ArmedAsWeaponBy,DamagedBy,DisarmedAsAmmoBy,DisarmedAsWeaponBy,DroppedBy,PickedBy,TeleportedBy}` ·
`FlagAdjust{Collidable,Damaging,Movement}` ·
`FlagCreateFromFactory`, `FlagGeneratedFromFactory`, `FlagSetWeaponIntoUse`,
`FlagIsAnimationActionFrame`, `FlagShowInventory`

---

## Processors

`example_game/core/processors/` — 22 `*_system/` packages. Reference as
`"<system>.<module>:<ClassName>"`, or `"<system>:<ClassName>"` for a class re-exported from the
package `__init__.py`.

> ⚠️ Package re-exports **rename**. `collision_system:GenerateCollisionsProcessor` is really
> `GenerateCollisionsOptimizedProcessor`; `damage_system:GenerateDamageProcessor` is really
> `GenerateDamageSingleProcessor`; `damage_system:PerformDamageProcessor` is really
> `PerformDamageSingleProcessor`. Check the `__init__.py` before grepping for a class.

| System | Count | Classes |
|---|---|---|
| `command_system` | 9 | `GenerateCommandFrom{Brain,BTree,BList,Input,Mouse,File}Processor`, `PerformCommandProcessor`, `PerformPathfindingCalculationProcessor`, `RecordCommandToFileProcessor` |
| `movement_system` | 5 | `PerformMovementProcessor`, `PerformAdjustMovementProcessor`, `RemoveFlag{DoMove,AdjustMovement,HasStoppedMovement}Processor` |
| `animation_system` | 7 | `Perform{Movement,Action,ActionIdle,Idle,Expire}AnimationProcessor`, `PerformFrameUpdateProcessor`, `RemoveFlagIsAnimationActionFrameProcessor` |
| `collision_system` | 6 modules / 9 classes | `GenerateCollisions{Optimized,OptimizedFull,NotOptimized,NotOptimizedFull}Processor`, `ResolveCollisions{Optimized,Old}Processor`, `ResolveMapCollisionsProcessor`, `PerformAdjustCollidableProcessor`, `RemoveFlag{HasCollided,AdjustCollidable}Processor` |
| `render_system` | 14 | `PerformClearWindowProcessor`, `PerformClearCameraProcessor`, `PerformScroll{,Delayed}CameraProcessor`, `PerformRender{Map,Model,ArmedWeapon,ArmedAmmo,Inventory,Messages,DebugInfo}Processor`, `PerformBlit{Camera,Picture}Processor`, `GenerateRenderDataFromParentProcessor` |
| `attack_system` | 2 | `GenerateProjectileFactoryDataProcessor`, `RemoveFlagDoAttackProcessor` |
| `factory_system` | 3 | `PerformFactoryGenerationProcessor`, `RemoveFlag{CreateFromFactory,GeneratedFromFactory}Processor` |
| `damage_system` | 8 modules / 10 classes | `GenerateDamage{Single,Full}Processor`, `PerformDamage{Single,Full}Processor`, `PerformAdjustDamagingProcessor`, `RemoveFlag{AdjustDamaging,HasDamaged,HasNoHealth,IsAboutToBeDamagedBy,WasDamagedBy}Processor` |
| `destroy_system` | 4 | `GenerateDestroyOn{Collision,NoHealth,StoppedMovement}Processor`, `PerformDestroyEntitiesProcessor` |
| `arm_weapon_system` | 11 | `Generate{Arm,Disarm}WeaponProcessor`, `Perform{Arm,Disarm}WeaponProcessor`, `PerformSetWeaponIntoUseProcessor`, 6 `RemoveFlag*Processor` |
| `arm_ammo_system` | 10 | `Generate{Arm,Disarm}AmmoProcessor`, `Perform{Arm,Disarm}AmmoProcessor`, 6 `RemoveFlag*Processor` |
| `pickup_system` | 5 | `GeneratePickupProcessor`, `PerformPickupProcessor`, `RemoveFlag{HasPicked,IsAboutToPickEntity,WasPickedBy}Processor` |
| `drop_system` | 4 | `PerformDropProcessor`, `RemoveFlag{HasDropped,IsAboutToDropEntity,WasDroppedBy}Processor` |
| `teleport_system` | 5 | `GenerateTeleportationProcessor`, `PerformTeleportationProcessor`, 3 `RemoveFlag*Processor` |
| `effects_system` | 12 | `GenerateSoundFXOn{ArmWeapon,Collision,Creation,Damage,Generation,Movement,NoHealth}Processor`, `GenerateVisualFXOn{Collision,Creation,Damage,Generation,NoHealth}Processor` |
| `score_system` | 5 | `GenerateScoreOn{Damage,NoHealth,Pickup}Processor`, `CalculateScoreProcessor`, `RemoveFlagHasScoredProcessor` |
| `sensor_system` | 2 modules / 4 classes | `GenerateEntitiesInSight{,Full}Processor`, `GenerateEntitiesWithinEarshot{,Full}Processor` |
| `position_system` | 1 | `PerformCheckOnTargetPositionProcessor` |
| `event_system` | 1 module / 2 classes | `GameEventsExProcessor` (use this), `GameEventsProcessor` (no filters, no throttling) |
| `gui_system` | 2 | `PerformGUIPress`, `RemoveFlagGUIFLagWasPressedProcessor` *(note the typo in the class name)* |
| `debug_system` | 2 | `DebugProcessorPerformanceProcessor`, `ListComponentsProcessor` |

`example_game/core/processors/functions.py` holds shared helpers — notably
`filter_only_visible_on_camera`, whose cull margin scales with `TILE_RES_PX`
(tested in `tests/example_game/test_processor_functions.py`).

The `*Optimized` / `*Full` / `*Single` / `*Old` variants are alternative implementations kept
side-by-side; the package `__init__.py` picks the default. Scene files sometimes name a variant
directly.

---

## Commands

`example_game/core/commands/` — 38 modules. Reference as `["<name>", {params}]`.

| Group | Commands |
|---|---|
| Movement — direct | `move_dir`, `move_dir_add`, `move_vect`, `move_auto` |
| Movement — to a point | `move_to`, `move_to_pos_px`, `move_to_pos_px_vect`, `move_to_pos_tile`, `move_to_pos_tile_vect`, `move_to_vect` |
| Movement — to a target entity | `move_to_target`, `move_to_pos_target`, `move_to_pos_target_vect` |
| Movement — pathed | `move_to_checkpoints` |
| Combat | `attack`, `use_weapon`, `face_target` |
| Equipment | `arm_weapon`, `disarm_weapon`, `arm_ammo`, `disarm_ammo` |
| Items | `pick_item`, `drop_item`, `inventory_action`, `inventory_move_dir`, `toggle_inventory` |
| Blackboard | `set_bb_value`, `test_bb_value` |
| Sensors | `test_can_see`, `test_can_hear`, `test_damaged` |
| Control flow | `do_parallel`, `wait`, `reset_brain` |
| Other | `load_from_template`, `toggle_controls`, `log`, `example` |

`example.py` is the template to copy when writing a new command.
`move_dir.py` is the best-documented real one.

The `*_vect` variants take a vector rather than axis-aligned steps. `move_to_*` variants that need a
path require `PerformPathfindingCalculationProcessor` in the scene.

---

## Scripts

`example_game/core/scripts/` — reference as `["SCRIPT", "<name>", {kwargs}]`.

| Script | Purpose |
|---|---|
| `show_msg_window` | Modal pygame_gui message box. `html_text`, `title`; supports `%param` |
| `show_confirm_dlg` | Modal confirm. `title`, `long_desc`, `event_type`, `event_params` — emits the given event on confirm |
| `show_dlg_window` | Show a dialog registered via the scene's `dialogs` key |
| `add_msg` | Append to the in-game message log; supports `%param` |
| `load_quest` | Additively load another scene (`scene_file`) |
| `restart_quest` | Reload the current scene |
| `load_image` | Blit an image (`image_file`) |
| `play_music` | `music_file`, `volume` |
| `fade_in`, `shake_screen` | Screen effects |
| `set_bb_value` | Write an AI blackboard slot: `entity`, `bb_key`, `bb_value`, `only_if_not_set` |
| `restart_brain`, `modify_brain` | AI control |
| `disable_teleport` | Turn a teleport off |
| `exec_python_code` | Run arbitrary Python — dev only |
| `exit` | Quit |
| `do_nothing` | Placeholder |
| `condition_always_true`, `condition_example` | Condition-script examples |
| `collect_coins/`, `kill_all/` | Game-specific script packages |

Only `show_msg_window`, `show_confirm_dlg`, `add_msg` and `set_bb_value` perform `%param`
substitution. See
[../authoring/handlers-and-actions.md](../authoring/handlers-and-actions.md#event-param-substitution-with-).

---

## Event types

Emitted by processors and the engine:

| Event | Emitted by | `params` |
|---|---|---|
| `SCENE_START` | `engine.load_scene` | `filepath`, `id`, `alias`, `title`, `description`, `objective`, `stats` |
| `COLLISION` | collision system (both directions) | `entity1`, `entity2` |
| `DAMAGE` | damage system | `damaging`, `damageable` |
| `KILLED` | destroy system | `killed` |
| `DESTROYED` | destroy system | `destroyed` |
| `SCORE` | score system | `scored`, `score`, `total` |
| `ITEM_PICKUP` | pickup system | pickup participants |
| `ITEM_DROP` | drop system | drop participants |
| `TELEPORTATION` | teleport system | `teleport`, `teleportee` |
| `WEAPON_ARMED` / `WEAPON_DISARMED` | arm-weapon system | `weapon`, `fighter` |
| `WEAPON_SET_INTO_USE` | arm-weapon system | `type`, `fighter` |
| `AMMO_PACK_ARMED` / `AMMO_PACK_DISARMED` | arm-ammo system | `ammo`, `fighter` |
| `CAN_SEE` / `CAN_HEAR` | sensor system | sighted/heard entities |
| `ON_POS_TARGET` | `PerformCheckOnTargetPositionProcessor` | `on_target` (list of entity ids) |
| `ON_BUTTON_PRESSED` | `PerformGUIPress` | `name` |

Declared but **never emitted**: `WEARABLE_WEARED`, `KILL`, `PHASE_START`. Their
`MESSAGES.ON_EVENT` templates are dead.

Scene-invented types (any string works): `CUST_UI_CONFIRM` — emitted by `show_confirm_dlg` because a
scene asked it to.

An event type must appear in a `GameEventsExProcessor`'s `process` list (or be absent from its
`ignore` list) to be dispatched at all.

---

## States

`example_game/core/states/` — one module per `State`, named `state.name.lower()`.

`start_program`, `main_menu`, `settings`, `game`, `pause_game`, `console`, `end_program`,
`exit_game_dialog`, `load_scene_menu`.

`SETTINGS` exists only in `example_game/config.jsonc`; the engine defaults do not declare it.
`game.py` is the reference state module — see
[../core/bootstrap-and-loop.md](../core/bootstrap-and-loop.md#what-a-state-modules-run-does).

---

## Console commands

`example_game/core/console/commands/` — typed in the dev console (F9). `.scr` batch scripts live in
`core/console/scripts/` (`default.scr`, `test_script.scr`) and run via `script <name>`;
`!<expression>` evaluates Python inline.

| Command | Purpose |
|---|---|
| `list_commands` | List available commands and scripts |
| `get_entities` | Dump entities and aliases |
| `get_components` | Dump components |
| `get_processors` | Dump processors per group |
| `get_events` | Dump the event queue |
| `proc_perf` | Per-processor timings (needs `pgrpg.TIMED: true`) |
| `load_scene` | Load a scene by path |
| `init_engine` | Initialise the engine |
| `set_value` | Set a config value at runtime |
| `change_res` | Change resolution (triggers `main.reinit()`) |
| `toggle_fullscreen` | Toggle fullscreen (triggers `main.reinit()`) |
| `toggle_cons` | Toggle the console |
| `exit` | Quit |

Header and footer text come from `pgrpg/core/config/console.py`
(`cons_get_info_header` shows memory, state and entity count; `cons_get_info_footer` shows loaded
scenes and queued events).

---

## Test scenes as documentation

`example_game/resources/scenes/tests/` is numbered so each level adds one subsystem to the previous.
When you need to know "which processors do I need for X", open the corresponding scene:

`00_render` · `01_movements` · `02_commands` · `03_animations` · `04_collisions` · `05_pickup&drop` ·
`06_teleportation` · `07_arm_weapon` · `08_arm_ammo` · `09_projectiles` · `10_effects` ·
`11_sensors` · `12_ai` (plus `12_ai/simple/` — one scene per AI command) · `UI`

Complete games: `games/sokoban/` (base + 2 levels), `games/collect_coins/`, `games/kill_all/`.
`tests/12_ai/scenarios.md` describes the intended AI behaviours in prose.

Check [../SCOPE.md](../SCOPE.md) before trusting a scene — `game.py`'s comment block flags several as
broken or problematic.

---

## Related

- [../ecs/components.md](../ecs/components.md) · [../ecs/processors.md](../ecs/processors.md)
- [../core/commands-and-ai.md](../core/commands-and-ai.md) ·
  [../core/events-and-scripts.md](../core/events-and-scripts.md)
- [../authoring/index.md](../authoring/index.md)
