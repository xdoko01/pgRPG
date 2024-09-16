''' Module "pyrpg.core.ecs.components.new.has_target_position" contains
HasTargetPosition component implemented as a HasTargetPosition class.

Use 'python -m pyrpg.core.ecs.components.new.has_target_position -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

from pyrpg.core.config.game import GAME # for TILE_RES # in order to specify the position in pixel coords

from collections import namedtuple

Target = namedtuple('Target', ['map', 'tile_x', 'tile_y', 'x', 'y', 'radius'])

class HasTargetPosition(Component):
    ''' Entity should move/ be moved to the target
    position.

    Used by:
        - PerformCheckOnTargetPositionProcessor

    Examples of JSON definition:
        {
            "type" : "HasTargetPosition",
            "params" : {
                "targets" : [
                    ["test_map", 20, 10, 5],
                    ["test_map", 10, 20, 5]
                ]
            }
        }

    Tests:
        >>> c = HasTargetPosition(**{"targets" : [["test_map", 20, 10, 5], ["test_map", 10, 20, 5]]})
    '''

    __slots__ = ['targets']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the HasTargetPosition component.

        Parameters:
            :param targets: List containing targets as a list of values map, tile_x, tile_y, radius (in px)
            :type targets: list
        '''
        super().__init__()

        self.targets = []

        try:
            assert isinstance(kwargs.get('targets'), list), f'"Targets" must be specified as a list of tarkets.'
            for target in kwargs.get('targets'):
                assert isinstance(target, list) and len(target) == 4, f'Individual targets must be specified in a form of list containing 3 values.'
                new_target = Target(
                    map=target[0],
                    tile_x=target[1],
                    tile_y=target[2],
                    x=target[1] * GAME["TILE_RES_PX"] + GAME["TILE_RES_PX"] // 2,
                    y=target[2] * GAME["TILE_RES_PX"] + GAME["TILE_RES_PX"] // 2,
                    radius=target[3]
                )
                self.targets.append(new_target)
        except AssertionError:
            raise ValueError

if __name__ == '__main__':
    import doctest
    doctest.testmod()
