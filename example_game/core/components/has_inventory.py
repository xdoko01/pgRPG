''' Module "example_game.core.components.has_inventory" contains
HasInventory component implemented as a HasInventory class.

Use 'python -m core.components.has_inventory -v' to run
module tests.
'''

from pyrpg.core.ecs import Component
from pyrpg.functions.dict_utils import get_all_dict_values
from pyrpg.functions.dict_utils import add_dict_value

class HasInventory(Component):
    ''' Entity has inventory - can pick items and add it to the inventory.

    Used by:
        - PerformPickupProcessor

    Examples of JSON definition:
        {"type" : "HasInventory", "params" : {}},
        {"type" : "HasInventory", "params" : {"inventory" : ["key", "other_key", "money", 4]} }
        {"type" : "HasInventory", "params" : {"inventory" : ["key", "other_key", "money", 4], "categories" : {"keys" : ["key", "other_key"], "money" : ["money"], "weapons" : [4]}} }


    Tests:
        >>> c = HasInventory()
        >>> c = HasInventory(**{"inventory" : ["key", "other_key", "money", 4]})
        >>> c = HasInventory(**{"inventory" : ["key", "other_key", "money", 4], "categories" : {"keys" : ["key", "other_key"], "money" : ["money"], "weapons" : [5]}})
    '''

    __slots__ = ['inventory', 'categories', 'max_items', 'slots']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new HasInventory component.

        Parameters:
            :param inventory: List of entities that are in the inventory
            :type inventory: List of string or list of integers

            :param categories: Dictionary where the categorization of entities in inventory is stored
            :type categories: dict

            :param max_items: Max number of items that can be in the inventory
            :type max_items: int

        '''

        super().__init__()

        # Inventory is implemented as a set to enable easy adding and deletion of items
        # and prevent double membership.
        self.inventory = set(kwargs.get('inventory', []))
        self.categories = kwargs.get('categories', {})
        self.max_items = kwargs.get('max_items', 10)
        self.slots = [None for i in range(self.max_items)] # all the slots are empty at the start

        # Check that inventory is a set
        try:
            assert isinstance(self.inventory, set), f'Inventory must be a set of entities.'
            assert isinstance(self.categories, dict), f'Categories of inventory must be a dict.'
            assert len(self.inventory) <= 10, f'Too many items in the inventory'

            # Add inventory to the slots - from start
            for slot_id, item in enumerate(self.inventory): self.slots[slot_id] = item

            # Every entity stored as a value in categories must be also in inventory
            assert set(get_all_dict_values(self.categories)).issubset(self.inventory), f'All items in categories must be also part of the inventory set.'

            # Every entity in the inventory must have some slot
            assert set(self.inventory).issubset(self.slots)
    
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

    def remove_by_entity_id(self, entity_id: int) -> None:
        '''Safely remove entity_id from the inventory's data structures.
        '''
        # Remove from set
        self.inventory.remove(entity_id) 
        
        # Remove from slots
        self.slots = [self.slots[slot_id] if self.slots[slot_id] != entity_id else None for slot_id in range(len(self.slots))]

        # TODO - REmove from categories
        pass

    def remove_by_slot_id(self, slot_id: int) -> None:
        '''Safely remove entity_id stored in the slots[slot_id] from the inventory's data structures.
        '''
        # Remove from set
        self.inventory.remove(self.slots[slot_id]) 
        
        # Remove from slots
        self.slots[slot_id] = None

        # TODO - REmove from categories
        pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
