''' Module "pyrpg.core.ecs.components.destroy_on_no_health" contains
DestroyOnNoHealth component implemented as a DestroyOnNoHealth class.

Use 'python -m pyrpg.core.ecs.components.destroy_on_no_health -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class DestroyOnNoHealth(Component):
    ''' Entity is marked as IsDestroyed after having no health

    Used by:
        - GenerateDestroyOnNoHealthProcessor

    Examples of JSON definition:
        {"type" : "DestroyOnNoHealth", "params" : {"ttl" : 1000}}

    Tests:
        >>> c = DestroyOnNoHealth(ttl=1000)
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
