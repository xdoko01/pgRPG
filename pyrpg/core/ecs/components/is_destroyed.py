''' Module "pyrpg.core.ecs.components.is_destroyed" contains
IsDestroyed component implemented as a IsDestroyed class.

Use 'python -m pyrpg.core.ecs.components.is_destroyed -v' to run
module tests.
'''

from .component import Component

class IsDestroyed(Component):
    ''' Component tagging entity as destroyed

    Used by:
        - HandleDestroyedEntitiesProcessor
        - RenderableModelAnimationActionProcessor

    Examples of JSON definition:
        {"type" : "IsDestroyed", "params" : {}}

    Tests:
        >>> c = IsDestroyed()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiate FlagIsDestroyed tag.

            :param src_entity: The destroyer (optional)
            :type src_entity: entity_id
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()