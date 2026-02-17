''' Module "example_game.core.components.flag_was_picked_by" contains
FlagWasPickedBy component implemented as a FlagWasPickedBy class.

Use 'python -m example_game.core.components.flag_was_picked_by -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagWasPickedBy(Component):
    ''' Entity was picked by some other entity.

    Used by:
        -   PerformPickupProcessor

    '''

    __slots__ = ['picker']

    def __init__(self, picker=None):
        ''' Initiate value for the new FlagWasPickedBy component.

        Parameters:
            :param picker: Entity ID that has picked given entity
            :type picker: int

        '''
        super().__init__()

        self.picker = picker


if __name__ == '__main__':
    import doctest
    doctest.testmod()
