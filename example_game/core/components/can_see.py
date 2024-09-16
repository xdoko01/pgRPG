''' Module "pyrpg.core.ecs.components.new.can_see" contains
CanSee component implemented as a CanSee class.

Use 'python -m pyrpg.core.ecs.components.new.can_see -v' to run
module tests.
'''
from math import radians, sin, cos

from pyrpg.core.ecs.components.component import Component
from pyrpg.core.config import GAME # for TILE_RES_PX - in order to re-calculate tile distance to px

class CanSee(Component):
    ''' Component is holding information about the capability of the
    entity to see other entities in the game.

    Used by:
        - GenerateEntitiesInSightProcessor

    Examples of JSON definition:
        {"type" : "CanSee", "params" : {"angle": 90, "distance_px": 1000}}
        {"type" : "CanSee", "params" : {"angle": 90, "distance_tiles": 1000}}

    Tests:
        >>> c = CanSee(**{"angle": 90, "distance_tiles": 10})
    '''

    __slots__ = ['angle', 'angle_deg', 'angle_rad', 'angle_rad_div2', 'distance', 'ent_in_sight']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the CanSee component.

        Parameters:
            :param angle: Angle of sight.
            :type angle: int (0-360)

            :param distance_px: Distance of sight in pixels.
            :type distance_px: int

            :param distance_tiles: Distance of sight in tiles.
            :type distance_tiles: int

            :param ent_in_sight: List of entity ids in sight.
            :type ent_in_sight: list
        '''
        super().__init__()

        # Get the angle - mandatory
        self.angle = kwargs['angle']

        # Supporting variables for calculations
        self.angle_deg = self.angle
        self.angle_rad = radians(self.angle_deg)
        self.angle_rad_div2 = radians(self.angle_deg // 2)
        self.sin_angle = sin(self.angle_rad_div2)
        self.cos_angle = cos(self.angle_rad_div2)

        # Get the distance in px - mandatory
        self.distance = kwargs.get('distance_px', kwargs.get('distance_tiles', 10) * GAME["TILE_RES_PX"])

        # Get the list of entities in sight - optional
        self.ent_in_sight = set(kwargs.get('ent_in_sight', []))

        # Check the validity of input parameters
        try:
            assert isinstance(self.angle, int) and self.angle in range(360), f'Incorrect angle value on input.'
            assert isinstance(self.distance, int) and self.distance > 0, f'Incorrect distance value on input.'
            assert isinstance(self.ent_in_sight, set), f'Incorrect ent_in_sight value on input.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

if __name__ == '__main__':
    import doctest
    doctest.testmod()
