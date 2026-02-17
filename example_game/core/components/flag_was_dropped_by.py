''' Module "example_game.core.components.flag_was_dropped_by" contains
FlagWasDroppedBy component implemented as a FlagWasDroppedBy class.

Use 'python -m example_game.core.components.flag_was_dropped_by -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagWasDroppedBy(Component):
    ''' Entity was dropped by some other entity.

    Used by:
        -   PerformDropProcessor

    '''

    __slots__ = ['dropper']

    def __init__(self, dropper):
        ''' Initiate value for the new FlagWasDroppedBy component.

        Parameters:
            :param dropper: Entity ID that has dropped given entity
            :type dropper: int

        '''
        super().__init__()

        self.dropper = dropper


if __name__ == '__main__':
    import doctest
    doctest.testmod()
