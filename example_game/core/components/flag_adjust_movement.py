''' Module "pyrpg.core.ecs.components.flag_adjust_movement" contains
FlagAdjustMovement component implemented as a FlagAdjustMovement class.

Use 'python -m pyrpg.core.ecs.components.flag_adjust_movement -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagAdjustMovement(Component):
    ''' Entity should adjust its movement component by given inputs

    Used by:
        -   PerformAdjustMovementProcessor
        -   RemoveFlagAdjustMovementProcessor
    '''

    __slots__ = ['velocity_fnc', 'accelerate_fnc']

    def __init__(self, velocity_fnc=[lambda x:x], accelerate_fnc=[lambda y:y]):
        ''' Initiate value for the new FlagAdjustCollision component.

        Parameters:
            :param velocity_fnc: Functions for modification of velocity of movable component
            :type velocity_fnc: list of function

            :param accelerate_fnc: Functions for modification of acceleration movable component
            :type accelerate_fnc: list of function

        '''
        super().__init__()

        self.velocity_fnc = velocity_fnc
        self.accelerate_fnc = accelerate_fnc

if __name__ == '__main__':
    import doctest
    doctest.testmod()
