''' Module "pyrpg.core.ecs.components.debug" contains
Debug component implemented as a Debug class.

Use 'python -m pyrpg.core.ecs.components.debug -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class Debug(Component):
    ''' Display debug information on entities that are tagged by this component.

    Used by:
        - RenderDebugProcessor

    Examples of JSON definition:
        {"type" : "Debug", "params" : {}}

    Tests:
        >>> c = Debug()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new component
        '''

        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
