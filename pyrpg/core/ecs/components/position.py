''' Module "pyrpg.core.ecs.components.position" contains
Position component implemented as a Position class.

Use 'python -m pyrpg.core.ecs.components.position -v' to run
module tests.
'''

from .component import Component

# TODO - is self.direction necessary? is not enough dir_name?
class Position(Component):
    ''' Entity has possition in the game world specified by x, y and map.

    Used by:
        - UpdateCameraOffsetProcessor
        - MovementProcessor
        - RenderMapProcessor
        - RenderWorldProcessor
        - RenderDebugProcessor
        - CollisionMapProcessor
        - CollisionEntityGeneratorProcessor
        - CollisionTeleportProcessor
        - CollisionEntityProcessor
        - CollisionCorrectorProcessor
        - RenderMapProcessorFullScan (OBSOLETE)

    Examples of JSON definition:
        {"type" : "Position", "params" : {"x" : 0, "y" : 0, "map" : "test_map"}}

    Tests:
        >>> c = Position(**{"x" : 0, "y" : 0, "map" : "test_map"})
        >>> c.x
        0
        >>> c.map
        'test_map'
    '''

    __slots__ = ['x', 'y', 'map', 'direction', 'dir_name']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Position component.

        Parameters:
            :param x: X-axis position in pixels on the map (mandatory).
            :type x: int

            :param y: Y-axis position in pixels on the map (mandatory).
            :type y: int

            :param map: Name of the map where entity is present (mandatory).
            :type map: str

            :param dir_name: Name of the direction where entity is heading (optional).
            :type dir_name: str

            :raise: ValueError - in case mandatory parameters are missing.
        '''

        super().__init__()

        # Coordinates in the world
        try:
            self.x = kwargs.get('x')
            self.y = kwargs.get('y')
            self.map = kwargs.get('map')
            self.dir_name = kwargs.get('dir_name', 'down')
        except KeyError:
            # Notify component factory that initiation has failed
            print(f'Mandatory parameters are missing.')
            raise ValueError

        # Assert that map exists in the global list of all initiated maps engine
        try:
            # Following assertion commented in order not to address global 'maps' directory from component.
            #assert self.map in engine.maps.keys(), f'Map {self.map} is not initialized for {self.__class__} component.'
            assert isinstance(self.map, str), f'Map "{self.map}" is not a string for {self.__class__} component.'
            assert isinstance(self.x, int), f'Position x is not an integer for {self.__class__} component.'
            assert isinstance(self.y, int), f'Position y is not an integer for {self.__class__} component.'
            assert self.dir_name in ('up', 'down', 'left', 'right'), f'Position direction is not defined for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Direction SOUTH (0,1) NORD (0,-1) WEST (-1,0) EAST (1,0)
        # Necessary for correct rendering of sprites and text boxes etc.
        
        if self.dir_name == 'down': self.direction = (0, 1)
        if self.dir_name == 'up': self.direction = (0, -1)
        if self.dir_name == 'left': self.direction = (-1, 0)
        if self.dir_name == 'right': self.direction = (1, 0)

        # Remember last possition, on collision return to the last known pos
        # Required for resolution of collisions with the map
        self.lastx = self.x
        self.lasty = self.y
        self.lastmap = self.map

    def set_direction(self, dir_name):
        '''
        '''
        try:
            assert dir_name in ('up', 'down', 'left', 'right'), f'Position direction is not defined for {self.__class__} component.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError
        
        self.dir_name = dir_name

        if self.dir_name == 'down': self.direction = (0, 1)
        if self.dir_name == 'up': self.direction = (0, -1)
        if self.dir_name == 'left': self.direction = (-1, 0)
        if self.dir_name == 'right': self.direction = (1, 0)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
