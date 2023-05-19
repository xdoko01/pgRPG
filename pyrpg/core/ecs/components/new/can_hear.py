''' Module "pyrpg.core.ecs.components.new.can_hear" contains
CanHear component implemented as a CanHear class.

Use 'python -m pyrpg.core.ecs.components.new.can_hear -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component
from pyrpg.core.config.config import TILE_RES # in order to re-calculate tile distance to px

class CanHear(Component):
    ''' Component is holding information about the capability of the
    entity to hear other entities in the game.

    Used by:
        - GenerateEntitiesWithinEarshotProcessor

    Examples of JSON definition:
        {"type" : "CanHear", "params": {"distance_px": 1000}}
        {"type" : "CanHear", "params": {"distance_tiles": 10}}

    Tests:
        >>> c = CanHear(**{"distance_tiles": 10})
    '''

    __slots__ = ['distance', 'ent_within_earshot']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the CanHear component.

        Parameters:

            :param distance_px: Audible distance in pixels.
            :type distance_px: int

            :param distance_tiles: Audible distancet in tiles.
            :type distance_tiles: int

            :param ent_within_earshot: Set of audible entities.
            :type ent_within_earshot: set
        '''
        super().__init__()

        # Get the distance in px - mandatory
        self.distance = kwargs.get('distance_px', kwargs.get('distance_tiles', 10) * TILE_RES)

        # Get the list of audible entities - optional
        self.ent_within_earshot = set(kwargs.get('ent_within_earshot', []))

        # Check the validity of input parameters
        try:
            assert isinstance(self.distance, int) and self.distance > 0, f'Incorrect distance value on input.'
            assert isinstance(self.ent_within_earshot, set), f'Incorrect ent_within_earshot value on input.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

if __name__ == '__main__':
    import doctest
    doctest.testmod()
