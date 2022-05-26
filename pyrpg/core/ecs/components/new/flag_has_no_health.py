''' Module "pyrpg.core.ecs.components.flag_has_no_health" contains
FlagHasNoHealth component implemented as a FlagHasNoHealth class.

Use 'python -m pyrpg.core.ecs.components.flag_has_no_health -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagHasNoHealth(Component):
    ''' Component tagging entity as destroyed

    Used by:
        - PerformDamageProcessor

    Examples of JSON definition:
        {"type" : "FlagHasNoHealth", "params" : {}}

    Tests:
        >>> c = FlagHasNoHealth()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiate FlagHasNoHealth tag.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
