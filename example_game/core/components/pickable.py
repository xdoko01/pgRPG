''' Module "example_game.core.components.pickable" contains
Pickable component implemented as a Pickable class.

Use 'python -m example_game.core.components.pickable -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class Pickable(Component):
    ''' Entity is pickable by HasInventory component.

    Used by:
        - CollisionItemProcessor

    Examples of JSON definition:
        {"type" : "Pickable", "params" : {}}
        {"type" : "Pickable", "params" : {"category" : "items.coins.golden"}}


    Tests:
        >>> c = Pickable()
    '''

    __slots__ = ['category']

    def __init__(self, *args, **kwargs):
        ''' Just a tag marking the entity that it can
        be picked.
        '''

        super().__init__()

        self.category = kwargs.get('category', '')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
