''' Module "example_game.core.components.teleportable" contains
Teleportable component implemented as a Teleportable class.

Use 'python -m example_game.core.components.teleportable -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class Teleportable(Component):
    ''' Entity is a teleportable - i.e. on collision with entity having
    Teleport component can be teleported.

    Used by:
        - PerformTeleportationProcessor

    Examples of JSON definition:
        {"type" : "Teleportable", "params" : {}},
        {"type" : "Teleportable", "params" : {"keys" : [1, 2, 3]}},

    Tests:
        >>> c = Teleportable()
        >>> c.keys
        {None}
        >>> d = Teleportable(keys=[1, 2, 3])
        >>> d.keys
        {1, 2, 3, None}
    '''

    __slots__ = ['keys']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Teleportable component.
        '''
        super().__init__()

        self.keys = set(kwargs.get("keys", {}))

        # Add also always None value to the set of keys for the cases when teleport.key=None 
        self.keys.add(None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
