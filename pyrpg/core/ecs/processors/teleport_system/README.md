# *TELEPORT SYSTEM*

Teleport system is using `Teleportable` and `Teleport` components to identify the entity that can be teleported (`Teleportable`) and the entity that acts as a teleport (`Teleport`).

1. The `NewGenerateTeleportationProcessor` scans all entities that act as teleport (`Teleport`) and that has collided in given cycle (`FlagHasCollided`) and assigns new flag `NewFlagIsAboutToBeTeleportedBy` to all potential teleportees, i.e. all entities that have collided with `Teleport` entity in the given cycle. The parameters of the flag contain all parameters from `Teleport` component necessary for successful teleportation processing in `NewPerformTeleportationProcessor`.

2. The `NewPerformTeleportationProcessor` scans all entities that are potential teleportees (`NewFlagIsAboutToBeTeleportedBy` + `Teleportable`) and performs the actual teleportation. The teleportation is done by updating the `Position` component of `Teleportable` entity. In order to mark that teleportation has happened, teleport is assigned new component `NewFlagHasTeleported` and the teleportee entity is assigned component `NewFlagWasTeleportedBy`. Those can be later use in further processors for implementation of other logic.

3. Set of processors `NewRemoveFlagIsAboutToBeTeleportedByProcessor`, `NewRemoveFlagHasTeleportedProcessor` and `NewRemoveFlagWasTeleportedByProcessor` are deleting the temporary flags at the end of the cycle.

## Notes
  - it would be possible to delete the flag `NewFlagIsAboutToBeTeleportedBy` in the `NewPerformTeleportationProcessor` and get rid of additional processor `NewRemoveFlagIsAboutToBeTeleportedByProcessor`. The reason is that this flag is used only internally by the *TELEPORT SYSTEM* and it is not expected to use it outside of the system.