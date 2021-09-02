# *PICKUP SYSTEM*

Pickup system is using `Pickable` and `HasInventory` components to identify the entity that can be picked-up (`Pickable`) and the entity that can pick (`HasInventory`).

1. The `NewGeneratePickupProcessor` scans all entities that can be picked-up (`Pickable`) and that has collided in given cycle (`FlagHasCollided`) and assigns new flag `NewFlagIsAboutToPickEntity` to all potential pickers, i.e. all entities that have collided with `Pickable` entity in the given cycle.

2. The `NewPerformPickupProcessor` scans all entities that are potential pickers (`NewFlagIsAboutToPickEntity` + `HasInventory`) and performs the actual picking. The picking is done by updating the `HasInventory` content by the new entity and deletion of potential `Position` and `Camera` component from the picked item. In order to mark that pickup has happened, picker is assigned new component `NewFlagHasPicked` and the picked entity is assigned component `NewFlagWasPickedBy`. Those can be later use in further processors for implementation of other logic.

3. Set of processors `NewRemoveFlagIsAboutToPickEntityProcessor`, `NewRemoveFlagHasPickedProcessor` and `NewRemoveFlagWasPickedByProcessor` are deleting the temporary flags at the end of the cycle.

## Notes
  - it would be possible to delete the flag `NewFlagIsAboutToPickEntity` in the `NewPerformPickupProcessor` and get rid of additional processor `NewRemoveFlagIsAboutToPickEntityProcessor`. The reason is that this flag is used only internally by the *PICKUP SYSTEM* and it is not expected to use it outside of the system.