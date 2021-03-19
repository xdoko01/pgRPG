''' Module "pyrpg.core.ecs.components.pickable" contains
Pickable component implemented as a Pickable class.

Use 'python -m pyrpg.core.ecs.components.pickable -v' to run
module tests.
'''

from .component import Component

class Pickable(Component):
    ''' Entity is pickable by HasInventory component.

    Used by:
        - CollisionItemProcessor

    Examples of JSON definition:
        {"type" : "Pickable", "params" : {}}

    Tests:
        >>> c = Pickable()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Just a tag marking the entity that it can
        be picked.
        '''

        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
