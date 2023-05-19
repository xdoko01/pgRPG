
# Sensor System

## Table of Contents  

[Purpose](#purpose)

[Interaction with Other Systems](#interaction-with-other-systems)

[Components](#components)

 * [CanSee](#the-cansee-component)
   * [Combination of Attributes and Behavior](#combination-of-attributes-and-the-behavior)
   * [Examples](#examples)

[Processors](#processors)

 * [GenerateEntitiesInSightProcessor](#the-generateentitiesinsightprocessor-processor)
 * [GenerateEntitiesWithinEarshotProcessor](#the-generateentitieswithinearshotprocessor-processor)


## Purpose
The aim of the *Sensor System* is to implement senses such as sight and hear to the entities. Information about what other entities can be sean or heard by the entity can be then further utilized within the game logic.

## Interaction with Other Systems
The *Sensor System* expects *Position System*, *Movement System*, *Render System* in place in order to work. The *Movement System* is used information about the moving entities ie. entities that can be heard. The *Render System* provides information that some entity is visible and hence can be spotted by the entity.

## Components

### The `CanSee` Component
The `CanSee` component when assigned on an entity tells the game that entity is capable of seeing other entities with `Position` and `RenderableModel` components within the `CanSee` component parameters.

#### Parameters
 - `angle` - specifies the view angle of the entity in degrees. To be practically usable, the `angle` should be set to more than 90 degrees. I find the 120 degrees value to be the most realistic.
 - `distance_px` - specifies the max distance in pixels from the entity where the other entities can be spotted. Entities that are further away are not spotted.
 - `distance_tiles` - same as `distance_px` but measured in tiles, not pixels. Hence, it is independent on the tile resolution.

#### Examples

```
        {"type" : "CanSee", "params" : {"angle": 120, "distance_px": 1000}}
        {"type" : "CanSee", "params" : {"angle": 90, "distance_tiles": 10}}
```

#### Notes
The sight area is also part of the `Debug` component - see below.
![CanSee](pyRPG%20-%20SensorSystem%20-%20CanSee%20comp.png "CanSee component parameters displayed in debug mode.").

### The `CanHear` Component
The `CanHear` component when assigned on an entity tells the game that entity is capable of hearing other entities with `Position` and `Movable` components within the `CanHear` component parameters.

#### Parameters
 - `distance_px` - specifies the max distance in pixels from the entity where the other entities can be heared. Entities that are further away are not heared. Neither are those behind the walls.
 - `distance_tiles` - same as `distance_px` but measured in tiles, not pixels. Hence, it is independent on the tile resolution.

#### Examples

```
        {"type" : "CanHear", "params" : {"distance_px": 1000}}
        {"type" : "CanHear", "params" : {"distance_tiles": 10}}
```

#### Notes
The hear area is also part of the `Debug` component - see below.
TBD

## Processors
The *Sense System* consists of `GenerateEntitiesInSightProcessor` for determination of entities in sight and `GenerateEntitiesWithinEarshotProcessor` for determination of entities that are being heard.

### The `GenerateEntitiesInSightProcessor` Processor
This processor looks for entities in sight by iterating through entities with `Position` and `RenderableModel` components that are in sight of the entity. Also, it is checking if there are any obstacles between the entity with `CanSee` component and other entities. Entities that are hidden behind a wall are not being seen.

### The `GenerateEntitiesWithinEarshotProcessor` Processor
This processor looks for entities within earshot by iterating through entities with `Position` and `FlagHasMoved` components within particular range. Also, it is checking if there are any obstacles between the entity with `CanHear` component and other entities. Entities that are hidden behind a wall are not being heard.
