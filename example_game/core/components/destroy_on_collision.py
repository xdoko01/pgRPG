''' Module "pyrpg.core.ecs.components.destroy_on_collision" contains
DestroyOnCollision component implemented as a DestroyOnCollision class.

Use 'python -m pyrpg.core.ecs.components.destroy_on_collision -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class DestroyOnCollision(Component):
    ''' Entity is marked as IsDestroyed after collision with other entity

    Used by:
        - PerformDestroyOnCollisionProcessor

    Examples of JSON definition:
        {"type" : "DestroyOnCollision", "params" : {"ttl" : 1000}}

    Tests:
        >>> c = DestroyOnCollision(ttl=1000)
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
