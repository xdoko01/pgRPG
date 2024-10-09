''' Module "pyrpg.core.ecs.components.has_inventory" contains
HasInventory component implemented as a HasInventory class.

Use 'python -m core.components.has_inventory -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component
from pyrpg.functions.dict_utils import get_all_dict_values

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

    __slots__ = ['inventory', 'categories']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new HasInventory component.

        Parameters:
            :param inventory: List of entities that are in the inventory
            :type inventory: List of string or list of integers

            :param categories: Dictionary where the categorization of entities in inventory is stored
            :type categories: dict

        '''

        super().__init__()

        # Inventory is implemented as a set to enable easy adding and deletion of items
        # and prevent double membership.
        self.inventory = set(kwargs.get('inventory', []))
        self.categories = kwargs.get('categories', {})

        # Check that inventory is a list
        try:
            assert isinstance(self.inventory, set), f'Inventory must be a set of entities.'
            assert isinstance(self.categories, dict), f'Categories of inventory must be a dict.'

            # Every entity stored as a value in categories must be also in inventory
            assert set(get_all_dict_values(self.categories)).issubset(self.inventory), f'All items in categories must be also part of the inventory set.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
