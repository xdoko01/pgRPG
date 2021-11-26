''' Module "pyrpg.core.ecs.components.new_teleportable" contains
NewTeleportable component implemented as a NewTeleportable class.

Use 'python -m pyrpg.core.ecs.components.new_teleportable -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewTeleportable(Component):
    ''' Entity is a teleportable - i.e. on collision with entity having
    Teleport component can be teleported.

    Used by:
        - NewPerformTeleportationProcessor

    Examples of JSON definition:
        {"type" : "NewTeleportable", "params" : {}},
        {"type" : "NewTeleportable", "params" : {"keys" : [1, 2, 3]}},

    Tests:
        >>> c = NewTeleportable()
        >>> c.keys
        {None}
        >>> d = NewTeleportable(keys=[1, 2, 3])
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
