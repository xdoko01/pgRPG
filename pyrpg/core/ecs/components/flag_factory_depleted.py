''' Module "pyrpg.core.ecs.components.flag_factory_depleted" contains
FlagFactoryDepleted component implemented as a FlagFactoryDepleted class.

Use 'python -m pyrpg.core.ecs.components.flag_factory_depleted -v' to run
module tests.
'''

from .component import Component

class FlagFactoryDepleted(Component):
    ''' Flag/tag to mark entity(generator) which has no more
    units left to be produced.

    Used by:
        - CreateEntityOnPositionProcessor

    Examples of JSON definition:
        {"type" : "FlagFactoryDepleted", "params" : {}}

    Tests:
        >>> c = FlagFactoryDepleted()
    '''

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new FlagFactoryDepleted component.
        '''

        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()