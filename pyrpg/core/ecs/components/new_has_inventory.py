''' Module "pyrpg.core.ecs.components.new_has_inventory" contains
NewHasInventory component implemented as a NewHasInventory class.

Use 'python -m pyrpg.core.ecs.components.new_has_inventory -v' to run
module tests.
'''

from .component import Component

class NewHasInventory(Component):
    ''' Entity has inventory - can pick items and add it to the inventory.

    Used by:
        - NewPerformPickupProcessor

    Examples of JSON definition:
        {"type" : "NewHasInventory", "params" : {}},
        {"type" : "NewHasInventory", "params" : {"inventory" : ["key", "other_key", "money", 4]} }

    Tests:
        >>> c = NewHasInventory()
        >>> c = NewHasInventory(**{"inventory" : ["key", "other_key", "money", 4]})
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

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
