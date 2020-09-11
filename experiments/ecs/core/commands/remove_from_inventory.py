''' Module implementing remove_from_inventory command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_remove_from_inventory(*args, **kwargs):
    ''' Input
        - giver's entity
        - item's entity
    '''

    # Get entity of the giver and of the item
    giver_ent = kwargs.get("entity", None)
    item_ent = kwargs.get("item", None)

    # First try to find value based on key in alias_to_entity. If nothing found, use item (integer)
    # If entity nod defined by integer, raise error
    item = kwargs.get("item", None)
    item_ent = engine.alias_to_entity.get(item, item)
    assert(isinstance(item_ent, int), f'Entity {item} is not defined and/or must be an integer')

    # Get HasInventory component for giver entity - if it has one
    try:
        has_inventory = engine.world.component_for_entity(giver_ent, components.HasInventory)

        # If the item is passed, remove it from the inventory
        if item_ent in has_inventory.inventory: 
            has_inventory.inventory.remove(item_ent)

        print(f'Entity {item_ent} successfully removed from the inventory')
        # Successful finished
        return 0

    except KeyError:
        return -1
