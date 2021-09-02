''' Module "pyrpg.core.ecs.components.new_flag_has_teleported" contains
NewFlagHasTeleported component implemented as a NewFlagHasTeleported class.

Use 'python -m pyrpg.core.ecs.components.new_flag_has_teleported -v' to run
module tests.
'''

from .component import Component

class NewFlagHasTeleported(Component):
    ''' Entity (teleport) has teleported some other entity.

    Used by:
        -   NewPerformTeleportationProcessor

    '''

    __slots__ = ['teleportee']

    def __init__(self, teleportee=None):
        ''' Initiate value for the new NewFlagHasTeleported component.

        Parameters:
            :param teleportee: Entity ID that has been teleported
            :type teleportee: int

        '''
        super().__init__()

        self.teleportee = teleportee


if __name__ == '__main__':
    import doctest
    doctest.testmod()
