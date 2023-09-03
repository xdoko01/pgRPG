''' Module implementing add_to_inventory command
'''

import backup.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_add_to_inventory, alias=module_name)

def cmd_add_to_inventory(*args, **kwargs):
    ''' Input
        - receiver's entity
        - item's entity
    '''

    # Get entity of the receiver and of the item
    receiver_ent = kwargs.get("entity", None)
    item_ent = kwargs.get("item", None)

    # First try to find value based on key in alias_to_entity. If nothing found, use item (integer)
    # If entity nod defined by integer, raise error
    item = kwargs.get("item", None)
    item_ent = engine.alias_to_entity.get(item, item)
    assert(isinstance(item_ent, int), f'Entity {item} is not defined and/or must be an integer')

    # Get HasInventory component for receiver entity - if it has one
    try:
        has_inventory = engine.world.component_for_entity(receiver_ent, components.HasInventory)

        # If the item is passed, add it to the inventory
        if item_ent: has_inventory.inventory.append(item_ent)

        print(f'Entity {item_ent} successfully added to the inventory')

        # Successful finished
        return 0

    except KeyError:
        return -1
