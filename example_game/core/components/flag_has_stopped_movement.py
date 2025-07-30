''' Module "example_game.core.components.flag_has_stopped_movement" contains
FlagHasStoppedMovement component implemented as a FlagHasStoppedMovement class.

Use 'python -m example_game.core.components.flag_has_stopped_movement -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagHasStoppedMovement(Component):
    ''' Entity (picker) has stopped movement.

    Used by:
        -   PerformMovementProcessor
        -   PerformDestroyOnStoppedMovementProcessor
    '''

    __slots__ = []

    def __init__(self):
        ''' Initiate value for the new FlagHasStoppedMovement component.
        '''
        super().__init__()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
