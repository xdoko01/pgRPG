''' Module "pyrpg.core.ecs.components.is_dead" contains
IsDead component implemented as a IsDead class.

Use 'python -m pyrpg.core.ecs.components.is_dead -v' to run
module tests.
'''

from .component import Component

class IsDead(Component):
    ''' Component taging entity as dead

    Used by:
        - CollisionDamageProcessor
        - RenderableModelAnimationActionProcessor

    Examples of JSON definition:
        {"type" : "IsDead", "params" : {}}

    Tests:
        >>> c = IsDead()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiate IsDead tag.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
