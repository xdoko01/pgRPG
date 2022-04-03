# Support weight for the collisions - it is hard to push heavy entities
m1v1 = m2v2???

# Player is not corrected by collision from anyone
player ... `position_fix_self_denylist = {"ALL"}`

# NPC is not corrected by collision from anyone except the player
NPC ... `position_fix_self_allowlist = {"player"}`

# LAVA that can be walked by player but all other entities will omit it
lava ... no movable component and default collidable component
player ... `position_fix_self_denylist = {"LAVA"}` ... is not corrected by lava
other entities ... `position_fix_self_denylist = {}` ... correction is accepted by lava

# Stone that is moved only by player, all other entities are corrected and not moving the stone
stone ... `position_fix_self_allowlist = {"player"}` + `position_fix_walkaround_mode = False`

# Available parameters

## Substitution for `ignore_collision_with`
If Entity XYZ has `collision_allowlist = {}`    + `collision_denylist = {}`      = allow collision with *everybody* (DEFAULT)
If Entity XYZ has `collision_allowlist = {}`    + `collision_denylist = {"ALL"}` = allow collision with *nobody*
If Entity XYZ has `collision_allowlist = {1,2}` + `collision_denylist = {}`      = allow collision *only with entity 1 and 2*
If Entity XYZ has `collision_allowlist = {}`    + `collision_denylist = {3,4}`   = allow collision *with everybody except entity 3 and 4*

## Substitution for `ignore_position_fix`
If Entity XYZ has `collision_position_fix_others_allowlist = {}` + `collision_position_fix_others_denylist = {}` = allow fixing of collision of *every* entity that collided with Entity XZY (DEFAULT)
If Entity XYZ has `collision_position_fix_others_allowlist = {}` + `collision_position_fix_others_denylist = {"ALL"}` = allow fixing of collision of *no entity* that collided with Entity XZY
If Entity XYZ has `collision_position_fix_others_allowlist = {1,2}` + `collision_position_fix_others_denylist = {}` = allow fixing of collision of *entities 1 and 2 only* that collided with Entity XZY
If Entity XYZ has `collision_position_fix_others_allowlist = {}` + `collision_position_fix_others_denylist = {3,4}` = allow fixing of collision of *every entity except 3 and 4* that collided with Entity XZY

## Substitution for `position_fix_for_self`
If Entity XYZ has `collision_position_fix_self_allowlist = {}` + `collision_position_fix_self_denylist = {}` = allow fixing of position of Entity XYZ in case it collides everyone (DEFAULT)
If Entity XYZ has `collision_position_fix_self_allowlist = {}` + `collision_position_fix_self_denylist = {"ALL"}` = disable fixing of position of Entity XYZ in case it collides anyone
If Entity XYZ has `collision_position_fix_self_allowlist = {1,2}` + `collision_position_fix_self_denylist = {}` = allow fixing of position of Entity XYZ in case it collides with *entities 1 and 2 only* 
If Entity XYZ has `collision_position_fix_self_allowlist = {}` + `collision_position_fix_self_denylist = {3,4}` = allow fixing of position of Entity XYZ in case it collides *every entity except 3 and 4* 

# How to implement

## Stone that can be moved only by player and movement is happening only in straight direction
### Player
  - `Collidable()`
### Stone
  - `Collidable("collision_position_fix_self_allowlist" : ["player"], "position_fix_walkaround_mode" : false )`

## Danger zone that only player can enter (and collisions must be generated there)
### Player
  - `Collidable()`
### Danger zone
  - `Collidable("collision_position_fix_others_denylist" : ["player"])`
  - no `Movable` component

## Arrow/projectile
### Player
  - `Collidable()`
### Arrow
  - `Collidable("collision_denylist" : ["player"])`

