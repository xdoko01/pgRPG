# *PICKUP SYSTEM*

Pickup system is using `Pickable` and `NewHasInventory` components to identify the entity that can be picked-up (`Pickable`) and the entity that can pick (`NewHasInventory`).

1. The `NewGeneratePickupProcessor` scans all entities that can be picked-up (`Pickable`) and that has collided in given cycle (`FlagHasCollided`) and assigns new flag `NewFlagIsAboutToPickEntity` to all potential pickers, i.e. all entities that have collided with `Pickable` entity in the given cycle.

2. The `NewPerformPickupProcessor` scans all entities that are potential pickers (`NewFlagIsAboutToPickEntity` + `NewHasInventory`) and performs the actual picking. 

The picking is done by: 
  - updating the `NewHasInventory` content by the new entity 
  - deletion of `Camera` component from the picked item
  - keeping the `Position` component on the pickedup entity
  - adding `NewIsPickedBy` component to the item that was picked - it will stay there until in inventory
  - adding `IsPositionParentFor` to the picker - to be used in *MOVEMENT SYSTEM* for updating of position of wearables and weapons that need to be animated based on parent information.
  
  In order to mark that pickup has happened, picker is assigned new component `NewFlagHasPicked` and the picked entity is assigned component `NewFlagWasPickedBy`. Those can be later use in further processors for implementation of other logic.

3. Set of processors `NewRemoveFlagIsAboutToPickEntityProcessor`, `NewRemoveFlagHasPickedProcessor` and `NewRemoveFlagWasPickedByProcessor` are deleting the temporary flags at the end of the cycle.

## Q&A

### What if in one cycle occurs collision with 2 pickable entities?
  1. Because *COLLISION SYSTEM* supports multiple collisions in one cycle, the picker (entity 1 in example below) is assigned `NewFlagIsAboutToPickEntity` twice.
  2. As ECS does not support one entity to have multiple components of the same time, the first instance of `NewFlagIsAboutToPickEntity` (entity 2) is overwritten by the latter occurance (entity 3).
  3. As a result, only the second entity (entity 3) is successfully picked up in the first cycle.
  4. The first entity (entity 2) is picked up in the nearest next cycle when the collision happens again.

new_generate_pickup_processor.py              - (1377) - Entity 1 is trying to pick entity 2.
new_generate_pickup_processor.py              - (1377) - Entity 1 is trying to pick entity 3.
new_perform_pickup_processor.py               - (1377) - Entity 1 has picked entity 3.
new_perform_pickup_processor.py               - (1377) - Entity 3 was picked by entity 1.
new_generate_pickup_processor.py              - (1378) - Entity 1 is trying to pick entity 2.
new_perform_pickup_processor.py               - (1378) - Entity 1 has picked entity 2.
new_perform_pickup_processor.py               - (1378) - Entity 2 was picked by entity 1.

### Notes
  - it would be possible to delete the flag `NewFlagIsAboutToPickEntity` in the `NewPerformPickupProcessor` and get rid of additional processor `NewRemoveFlagIsAboutToPickEntityProcessor`. The reason is that this flag is used only internally by the *PICKUP SYSTEM* and it is not expected to use it outside of the system.