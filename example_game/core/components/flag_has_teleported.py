''' Module "example_game.core.components.flag_has_teleported" contains
FlagHasTeleported component implemented as a FlagHasTeleported class.

Use 'python -m example_game.core.components.flag_has_teleported -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagHasTeleported(Component):
    ''' Entity (teleport) has teleported some other entity.

    Used by:
        -   PerformTeleportationProcessor

    '''

    __slots__ = ['teleportee']

    def __init__(self, teleportee=None):
        ''' Initiate value for the new FlagHasTeleported component.

        Parameters:
            :param teleportee: Entity ID that has been teleported
            :type teleportee: int

        '''
        super().__init__()

        self.teleportee = teleportee


if __name__ == '__main__':
    import doctest
    doctest.testmod()
