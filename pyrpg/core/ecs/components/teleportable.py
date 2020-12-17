''' Module "pyrpg.core.ecs.components.teleportable" contains
Teleportable component implemented as a Teleportable class.

Use 'python -m pyrpg.core.ecs.components.teleportable -v' to run
module tests.
'''

from .component import Component

class Teleportable(Component):
    ''' Entity is a teleportable - i.e. on collision with entity having
    Teleport component can be teleported.

    Used by:
        - CollisionTeleportProcessor

    Examples of JSON definition:
        {"type" : "Teleportable", "params" : {}},

    Tests:
        >>> c = Teleportable()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Teleportable component.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
