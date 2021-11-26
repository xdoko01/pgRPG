''' Module "pyrpg.core.ecs.components.container" contains
Container component implemented as a Container class.

Use 'python -m pyrpg.core.ecs.components.container -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class Container(Component):
    ''' Component containing back reference to the
    master component.

    Used by:
        - Factory component
        - HasWeapon component
        - ClearTemporaryEntityProcessor
        - CollisionDeletionProcessor

    Examples of JSON definition:
        {"type" : "Container", "params" : {}}

    Tests:
        >>> c = Container()
    '''

    __slots__ = ['contained_in']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Container component.
        '''
        super().__init__()

        self.contained_in = kwargs.get("contained_in", None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

