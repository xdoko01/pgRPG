# *ARM AMMO SYSTEM*

ArmAmmo system is using `AmmoPack` and `HasWeapon` components to identify the entity that can be armed as ammo (`AmmoPack`) and the entity that can use the weapon (`HasWeapon`).

1. The `NewGenerateArmAmmoProcessor` scans all entities that act as ammo pack (`AmmoPack`) and that has been picked in given cycle (`FlagWasPickedBy`) and assigns new flag `NewFlagIsAboutToArmAmmo` to all potential fighters, i.e. all entities that have collided with `AmmoPack` entity in the given cycle.

2. The `NewPerformArmAmmoProcessor` scans all entities that are potential fighters (`NewFlagIsAboutToArmAmmo` + `HasWeapon`) and performs the actual arming of the ammo. The arming is done by updating the `HasWeapon`. In order to mark that arming of ammo has happened, fighter is assigned new component `NewFlagHasArmedAmmo` and the ammo entity is assigned component `NewFlagWasArmedAsAmmoBy`. Those can be later use in further processors for implementation of other logic.

3. Set of processors `NewRemoveFlagIsAboutToArmAmmoProcessor`, `NewRemoveFlagHasArmedAmmoProcessor` and `NewRemoveFlagWasArmedAsAmmoByProcessor` are deleting the temporary flags at the end of the cycle.

## What happens if the ammo of the same type is picked
  - *PICKUP SYSTEM* manages to put the new ammo entity to the inventory (`NewHasInventory`). Ammo entity has `NewFlagWasPickedBy` flag
  - `NewGenerateArmAmmoProcessor` detects this newly picked up ammo entity - entity is having both `AmmoPack` and `Factory` component (no AmmoPack will work without `Factory` component) and puts the details about the ammo and about the units available in the `Factory` component to the `NewFlagIsAboutToArmAmmo` component.
  - `NewPerformArmAmmoProcessor` arms the ammo from generic part of the inventory to the specific part of the inventory.
    - if there is no ammo entity so far, then we will store the new ammo entity there and we are done
    - if there is already some ammo entity stored there we do the following
      - add the remaining projectiles on the original entity to the new entity (by modifying the `Factory` component)
      - remove the original ammo entity from inventory and destroing it completely (all the ammo was transfered to the new entity anyway)
  - `NewPerformArmAmmoProcessor` detects that the ammo entity was picked and arms it and that is it

## Notes
  - it would be possible to delete the flag `NewFlagIsAboutToArmAmmo` in the `NewPerformArmAmmoProcessor` and get rid of additional processor `NewRemoveFlagIsAboutToArmAmmoProcessor`. The reason is that this flag is used only internally by the *ARM AMMO SYSTEM* and it is not expected to use it outside of the system.