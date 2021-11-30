''' Module "pyrpg.core.ecs.components.flag_is_about_to_be_teleported_by" contains
FlagIsAboutToBeTeleportedBy component implemented as a FlagIsAboutToBeTeleportedBy class.

Use 'python -m pyrpg.core.ecs.components.flag_is_about_to_be_teleported_by -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagIsAboutToBeTeleportedBy(Component):
    ''' Entity (potential teleportee) is about to be teleported by teleport, 
    if capable of teleportation.

    Used by:
        -   GenerateTeleportationProcessor

    '''

    __slots__ = ['teleport', 'dest_x', 'dest_y', 'dest_map', 'key']

    def __init__(self, teleport, dest_x, dest_y, dest_map, key=None):
        ''' Initiate value for the new FlagIsAboutToBeTeleportedBy component.

        Parameters:
            :param teleport: Entity ID of teleport entity
            :type teleport: int

            :param dest_x: X-position of teleportation destination
            :type dest_x: int

            :param dest_y: Y-position of teleportation destination
            :type dest_y: int

            :param dest_map: Map of teleportation destination
            :type dest_map: int

            :param key: Entity ID of key necessary for teleportation
            :type key: int
        '''
        super().__init__()

        self.teleport = teleport
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.dest_map = dest_map
        self.key = key


if __name__ == '__main__':
    import doctest
    doctest.testmod()
