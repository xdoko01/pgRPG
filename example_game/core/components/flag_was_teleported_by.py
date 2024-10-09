''' Module "pyrpg.core.ecs.components.flag_was_teleported_by" contains
FlagWasTeleportedBy component implemented as a FlagWasTeleportedBy class.

Use 'python -m pyrpg.core.ecs.components.flag_was_teleported_by -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagWasTeleportedBy(Component):
    ''' Entity was teleported by some teleport.

    Used by:
        -   PerformTeleportationProcessor

    '''

    __slots__ = ['teleport']

    def __init__(self, teleport=None):
        ''' Initiate value for the new FlagWasTeleportedBy component.

        Parameters:
            :param teleport: Entity ID that has teleported given entity
            :type teleport: int

        '''
        super().__init__()

        self.teleport = teleport


if __name__ == '__main__':
    import doctest
    doctest.testmod()
