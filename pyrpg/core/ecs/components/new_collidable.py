''' Module "pyrpg.core.ecs.components.new_collidable" contains
NewCollidable component implemented as a NewCollidable class.

Use 'python -m pyrpg.core.ecs.components.new_collidable -v' to run
module tests.
'''

from .component import Component

class NewCollidable(Component):
    ''' Entity collides with other collidable entities.

    Used by:
        - GenerateCollisionsProcessor

    Examples of JSON definition:
        {"type" : "Collidable", "params" : {"x" : 20, "y" : 20, "dx" : 0, "dy" : 0}}

    Tests:
        >>> c = NewCollidable()
        >>> c.x
        0
        >>> c = NewCollidable(**{"x" : 20, "y" : 20})
        >>> c.x
        20
    '''

    __slots__ = ['x', 'y', 'dx', 'dy', 'ignore_position_fix']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the NewCollidable component.

        Parameters:
            :param x: X-axis collision zone +- from the x-centre of the entity in pixel coordinates
            :type x: int

            :param y: Y-axis collision zone +- from the y-centre of the entity in pixel coordinates
            :type y: int

            :param dx: X-axis set offset +- from the x-centre of the entity in pixel coordinates
            :type dx: int

            :param dy: Y-axis set offset +- from the y-centre of the entity in pixel coordinates
            :type dy: int

            :param ignore_position_fix: Do not fix position upon hitting this entity - damage zones 
              need to be collidable in order to cause damage but at the same time can be stepped on by the player.
            :type ignore_position_fix: boolean

            :raise: ValueError - in case of incorrect collision borders
        '''

        super().__init__()

        # With and height of the collision zone - from the center +/-x and +/-y
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)

        # Correction of the centre from which the collision zone is calculated
        self.dx = kwargs.get('dx', 0)
        self.dy = kwargs.get('dy', 0)

        # Ignore fixing of position uppon collision with the entity - default False
        self.ignore_position_fix = kwargs.get('ignore_position_fix', False)

        try:
            assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as a positive int.'
            assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as a positive int.'
            assert isinstance(self.dx, int), f'Offset centre x-axis must be passed as an int.'
            assert isinstance(self.dy, int), f'Offset centre y-axis must be passed as an int.'
            assert isinstance(self.ignore_position_fix, bool), f'Parameter "ignore_position_fix" must be a boolean.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()

