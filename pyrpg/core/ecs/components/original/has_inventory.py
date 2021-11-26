''' Module "pyrpg.core.ecs.components.has_inventory" contains
HasInventory component implemented as a HasInventory class.

Use 'python -m pyrpg.core.ecs.components.has_inventory -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class HasInventory(Component):
    ''' Entity has inventory - can pick items and add it to the inventory.

    Used by:
        - RenderDebugProcessor
        - CollisionTeleportProcessor
        - CollisionItemProcessor

    Examples of JSON definition:
        {"type" : "HasInventory", "params" : {}},
        {"type" : "HasInventory", "params" : {"inventory" : ["key", "other_key", "money", 4]}},

    Tests:
        >>> c = HasInventory()
        >>> c = HasInventory(**{"inventory" : ["key", "other_key", "money", 4]})
    '''

    __slots__ = ['inventory']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new HasInventory component.

        Parameters:
            :param inventory: List of entities that are in the inventory
            :type inventory: List of string or list of integers
        '''

        super().__init__()

        # Check that inventory is a list
        try:
            assert isinstance(kwargs.get('inventory', []), list), f'Inventory must be a list of entities.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        self.inventory = kwargs.get('inventory', [])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
