# *ARM WEAPON SYSTEM*

ArmWeapon system is using `Weapon` and `HasWeapon` components to identify the entity that can be armed (`Weapon`) and the entity that can use the weapon (`HasWeapon`).

1. The `GenerateArmWeaponProcessor` scans all entities that act as weapon (`Weapon`) and that has been picked in given cycle (`FlagWasPickedBy`) and assigns new flag `FlagIsAboutToArmWeapon` to all potential fighters, i.e. all entities that have collided with `Weapon` entity in the given cycle.

2. The `PerformArmWeaponProcessor` scans all entities that are potential fighters (`FlagIsAboutToArmWeapon` + `HasWeapon`) and performs the actual arming of the weapon. The arming is done by updating the `HasWeapon`. In order to mark that arming of weapon has happened, fighter is assigned new component `FlagHasArmedWeapon` and the weapon entity is assigned component `FlagWasArmedAsWeaponBy`. Those can be later use in further processors for implementation of other logic.

3. Set of processors `RemoveFlagIsAboutToArmWeaponProcessor`, `RemoveFlagHasArmedWeaponProcessor` and `RemoveFlagWasArmedAsWeaponByProcessor` are deleting the temporary flags at the end of the cycle.

## Notes
  - it would be possible to delete the flag `FlagIsAboutToArmWeapon` in the `PerformArmWeaponProcessor` and get rid of additional processor `RemoveFlagIsAboutToArmWeaponProcessor`. The reason is that this flag is used only internally by the *ARM WEAPON SYSTEM* and it is not expected to use it outside of the system.