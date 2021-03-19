''' Module "pyrpg.core.ecs.components.temporary" contains
Temporary component implemented as a Temporary class.

Use 'python -m pyrpg.core.ecs.components.temporary -v' to run
module tests.
'''

import pygame
from .component import Component

class Temporary(Component):
    ''' Component that can be assigned to the entity that has
    limited timespan. After that entity disappears. For example
    projectile is temporary (arrow).

    Used by:
        - HasWeapon component
        - ClearTemporaryEntityProcessor
        - CollisionDamageProcessor

    Examples of JSON definition:
        {"type" : "Temporary", "params" : {"ttl" : 1000}}

    Tests:
        >>> c = Temporary()
        >>> c = Temporary(**{"ttl" : 1000})
    '''

    __slots__ = ['ttl', 'creation_time']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Temporary component.

            Parameters:
                :param ttl: How long the entity with this components should live (optional, default 5s)
                :type ttl: int
        '''

        super().__init__()

        # How long the entity with this components should live
        # default is 5 seconds.
        self.ttl = kwargs.get("ttl", 5000)

        # When was the component created - in order to determine
        # destruction time
        self.creation_time = pygame.time.get_ticks()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
