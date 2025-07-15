''' Module "pyrpg.core.ecs.components.damageable" contains
Damageable component implemented as a Damageable class.

Use 'python -m pyrpg.core.ecs.components.damageable -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class Damageable(Component):
    ''' Entity has some health, i.e. is damageable

    Used by:
        - CollisionDamageProcessor
        - RenderDebugProcessor

    Examples of JSON definition:
        {"type" : "Damageable", "params" : {}}
        {"type" : "Damageable", "params" : {"health" : 50}}

   Tests:
        >>> c = Damageable(**{"health" : 50})
        >>> c.health
        50
    '''

    __slots__ = ['health', 'damages']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the  Health component.
        '''
        super().__init__()

        self.health = kwargs.get("health", 100)
        self.damages = []


if __name__ == '__main__':
    import doctest
    doctest.testmod()
