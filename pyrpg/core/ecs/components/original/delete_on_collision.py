''' Module "pyrpg.core.ecs.components.delete_on_collision" contains
DeleteOnCollision component implemented as a DeleteOnCollision class.

Use 'python -m pyrpg.core.ecs.components.delete_on_collision -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class DeleteOnCollision(Component):
    ''' Entity is deleted after collision with other entity

    Used by:
        - CollisionDeletionProcessor

    Examples of JSON definition:
        {"type" : "DeleteOnCollision", "params" : {}}

    Tests:
        >>> c = DeleteOnCollision()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiate the new DeleteOnCollision component.
        '''

        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
