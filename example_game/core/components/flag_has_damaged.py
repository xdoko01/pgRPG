''' Module "pyrpg.core.ecs.components.flag_has_damaged" contains
FlagHasDamaged component implemented as a FlagHasDamaged class.

Use 'python -m pyrpg.core.ecs.components.flag_has_damaged -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagHasDamaged(Component):
    ''' Entity has damaged some other entity.

    Used by:
        -   GenerateDamageProcessor

    '''

    __slots__ = ['entities']

    def __init__(self, entities={}):
        ''' Initiate value for the new FlagHasDamaged component.

        Parameters:
            :param entities: ID of entities that has been damaged by this entity
            :type entity: set

        '''
        super().__init__()

        self.entities = entities


if __name__ == '__main__':
    import doctest
    doctest.testmod()
