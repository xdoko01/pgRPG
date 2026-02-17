''' Module "example_game.core.components.destroy_on_no_movement" contains
DestroyOnNoMovement component implemented as a DestroyOnNoMovement class.

Use 'python -m example_game.core.components.destroy_on_no_movement -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class DestroyOnNoMovement(Component):
    ''' Entity is marked as IsDestroyed after it has stopped moving

    Used by:
        - PerformDestroyOnStoppedMovementProcessor

    Examples of JSON definition:
        {"type" : "DestroyOnNoMovement", "params" : {"ttl" : 1000}}

    Tests:
        >>> c = DestroyOnNoMovement(ttl=1000)
    '''

    __slots__ = ['ttl']

    def __init__(self, *args, **kwargs):
        ''' Initiate the new DestroyOnCollision component.

        Parameters:

        :param ttl: How many miliseconds should the entity persist before deletion.
        :type ttl: int
        '''
        super().__init__()
        self.ttl = kwargs.get('ttl', 0)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
