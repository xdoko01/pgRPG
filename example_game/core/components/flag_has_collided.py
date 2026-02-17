''' Module "example_game.core.components.flag_has_collided" contains
FlagHasCollided component implemented as a FlagHasCollided class.

Use 'python -m example_game.core.components.flag_has_collided -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagHasCollided(Component):
    ''' Entity has collided with some other entity

    Used by:
        -   NewGenerateCollisionsProcessor

    '''

    __slots__ = ['collisions']

    def __init__(self, collisions={}):
        ''' Initiate values for the new FlagHasCollided component.

        Parameters:
            :param collisions: Set of tuples defining the collision
            :type collisions: set

        '''
        super().__init__()

        # Intit the set of collisions
        self.collisions = collisions


if __name__ == '__main__':
    import doctest
    doctest.testmod()
