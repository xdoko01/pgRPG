''' Module "pyrpg.core.ecs.components.collidable" contains
Collidable component implemented as a Collidable class.

Use 'python -m pyrpg.core.ecs.components.collidable -v' to run
module tests.
'''

from .component import Component

class Collidable(Component):
    ''' Entity collides with other collidable entities.

    Used by:
        - RenderDebugProcessor
        - CollisionMapProcessor
        - CollisionEntityGeneratorProcessor
        - CollisionDamageProcessor
        - CollisionWeaponProcessor
        - CollisionWearableProcessor
        - CollisionTeleportProcessor
        - CollisionItemProcessor
        - CollisionEntityProcessor
        - CollisionDeletionProcessor
        - OBSOLETE: CollisionCorrectorProcessor

    Examples of JSON definition:
        {"type" : "Collidable", "params" : {"x" : 20, "y" : 20}}

    Tests:
        >>> c = Collidable()
        >>> c.x
        0
        >>> c = Collidable(**{"x" : 20, "y" : 20})
        >>> c.x
        20
    '''

    __slots__ = ['x', 'y', 'has_collided', 'collision_events']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Collidable component.

        Parameters:
            :param x: X-axis collision zone +- from the x-centre of the entity in pixel coordinates
            :type x: int

            :param y: Y-axis collision zone +- from the y-centre of the entity in pixel coordinates
            :type y: int

            :raise: ValueError - in case of incorrect collision borders
        '''

        super().__init__()

        # With and height of the collision zone - from the center +/-x and +/-y
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)

        try:
            assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as positive int.'
            assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as positive int.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Indicate if entity has collided with anything
        self.has_collided = False

        # Keep track with whom the entity collided
        self.collision_events = set()


if __name__ == '__main__':
    import doctest
    doctest.testmod()

