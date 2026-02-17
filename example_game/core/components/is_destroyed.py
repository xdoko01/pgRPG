''' Module "example_game.core.components.is_destroyed" contains
IsDestroyed component implemented as a IsDestroyed class.

Use 'python -m example_game.core.components.is_destroyed -v' to run
module tests.
'''

from pgrpg.core.ecs import Component
from pygame.time import get_ticks

class IsDestroyed(Component):
    ''' Component tagging entity as destroyed

    Used by:
        - PerformDestroyEntitiesProcessor
        - PerformExpireAnimationProcessor

    Examples of JSON definition:
        {"type" : "IsDestroyed", "params" : {}}

    Tests:
        >>> c = IsDestroyed()
    '''

    __slots__ = ['ttl', 'destroyed_time', 'action']

    def __init__(self, *args, **kwargs):
        ''' Initiate IsDestroyed tag.

        Parameters:

        :param ttl: Number of mili-seconds before the entity is destroyed.
        :type ttl: int

        :param action: Animation action when entity is in destroyed status, default 'expire'
        :type action: str
        '''
        super().__init__()
        self.ttl = kwargs.get('ttl', 0)

        # When was the component created - in order to determine
        # destruction time
        self.destroyed_time = get_ticks()

        # Animation action for destroyed entity
        self.action = kwargs.get('action', 'expire')

if __name__ == '__main__':
    import doctest
    doctest.testmod()