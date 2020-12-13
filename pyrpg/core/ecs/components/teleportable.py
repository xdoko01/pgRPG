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
