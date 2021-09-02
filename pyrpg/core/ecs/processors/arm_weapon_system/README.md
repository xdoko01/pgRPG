# *ARM WEAPON SYSTEM*

ArmWeapon system is using `Weapon` and `HasWeapon` components to identify the entity that can be armed (`Weapon`) and the entity that can use the weapon (`HasWeapon`).

1. The `NewGenerateArmWeaponProcessor` scans all entities that act as weapon (`Weapon`) and that has been picked in given cycle (`FlagWasPickedBy`) and assigns new flag `NewFlagIsAboutToArmWeapon` to all potential fighters, i.e. all entities that have collided with `Weapon` entity in the given cycle.

2. The `NewPerformArmWeaponProcessor` scans all entities that are potential fighters (`NewFlagIsAboutToArmWeapon` + `HasWeapon`) and performs the actual arming of the weapon. The arming is done by updating the `HasWeapon`. In order to mark that arming of weapon has happened, fighter is assigned new component `NewFlagHasArmedWeapon` and the weapon entity is assigned component `NewFlagWasArmedAsWeaponBy`. Those can be later use in further processors for implementation of other logic.

3. Set of processors `NewRemoveFlagIsAboutToArmWeaponProcessor`, `NewRemoveFlagHasArmedWeaponProcessor` and `NewRemoveFlagWasArmedAsWeaponByProcessor` are deleting the temporary flags at the end of the cycle.

## Notes
  - it would be possible to delete the flag `NewFlagIsAboutToArmWeapon` in the `NewPerformArmWeaponProcessor` and get rid of additional processor `NewRemoveFlagIsAboutToArmWeaponProcessor`. The reason is that this flag is used only internally by the *ARM WEAPON SYSTEM* and it is not expected to use it outside of the system.