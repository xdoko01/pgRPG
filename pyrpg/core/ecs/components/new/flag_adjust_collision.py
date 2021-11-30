''' Module "pyrpg.core.ecs.components.flag_adjust_collision" contains
FlagAdjustCollision component implemented as a FlagAdjustCollision class.

Use 'python -m pyrpg.core.ecs.components.flag_adjust_collision -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagAdjustCollision(Component):
    ''' Entity should adjust its collision component by given inputs

    Used by:
        -   PerformAdjustCollisionProcessor
        -   RemoveFlagAdjustCollisionProcessor
    '''

    __slots__ = ['x_fnc', 'y_fnc', 'ignore_collision_with']

    def __init__(self, x_fnc=[lambda x:x], y_fnc=[lambda y:y], ignore_collision_with=[]):
        ''' Initiate value for the new FlagAdjustCollision component.

        Parameters:
            :param x_fnc: Functions for modification of x-dimension of collidable component
            :type x_fnc: list of function

            :param y_fnc: Functions for modification of y-dimension of collidable component
            :type y_fnc: list of function

        '''
        super().__init__()

        self.x_fnc = x_fnc
        self.y_fnc = y_fnc
        self.ignore_collision_with = set(ignore_collision_with)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
