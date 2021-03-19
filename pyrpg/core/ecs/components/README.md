# Package pyrpg.core.ecs.components

This package contains all components that can be assign to pyrpg entities.

## Package __init__.py initiation
 - contains list of all components and imports all individual components
 - contains `create_component` function that takes data necessary for component creation in the form on string and manages creation of component class and returns its instance.

## Creating new component
 - create new module file named same as the conponent name
 - register the new component class in `__init__.py` `ALL_COMPONENTS` list
 - import the component module in `__init__.py` in the following manner `from .brain import *`
 - make the class of the new component visible by adding it to `__init__.py` `__all__` list
 - edit this documentation file

## Description and comments on components

### Brain Component

### Camera Component

### CanTalk Component

### CanWear Component

### Collidable Component

### Container Component

### Controllable Component

### Damageable Component

### Damaging Component

### Debug Component

### DeleteOnCollision Component

### Factory Component

### HasInventory Component

### HasWeapon COmponent

### IsDead Component

### Labeled Component

### LinearMotion Component

### Motion Component

### Pickable Component

### Position Component

### RenderableModel Component

### Renderable Component

### State Component (OBSOLETE)

### Teleport Component

### Teleportable Component

### Temporary Component

### Weapon Component

### Wearable Component





