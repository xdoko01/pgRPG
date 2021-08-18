''' Module "pyrpg.core.ecs.components.new_flag_has_collided" contains
NewFlagHasCollided component implemented as a NewFlagHasCollided class.

Use 'python -m pyrpg.core.ecs.components.new_flag_has_collided -v' to run
module tests.
'''

from .component import Component

class NewFlagHasCollided(Component):
    ''' Entity has collided with some other entity

    Used by:
        -   NewGenerateCollisionsProcessor

    '''

    __slots__ = ['collisions']

    def __init__(self, collisions={}):
        ''' Initiate values for the new NewFlagHasCollided component.

        Parameters:
            :param collisions: Set of tuples defininf the collision
            :type collisions: set

        '''
        super().__init__()

        # Intit the set of collisions
        self.collisions = collisions


if __name__ == '__main__':
    import doctest
    doctest.testmod()
