''' Module "example_game.core.components.flag_was_damaged_by" contains
FlagWasDamagedBy component implemented as a FlagWasDamagedBy class.

Use 'python -m example_game.core.components.flag_was_damaged_by -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagWasDamagedBy(Component):
    ''' Entity was damaged by some other entities.

    Used by:
        -   GenerateDamageProcessor
        -   CalculateDamageProcessor

    '''

    __slots__ = ['entities']

    def __init__(self, entities={}):
        ''' Initiate value for the new FlagWasDamagedBy component.

        Parameters:
            :param entities: Set of entity ids that has damaged entity in this cycle.
            :type entities: set

        '''
        super().__init__()

        self.entities = entities


if __name__ == '__main__':
    import doctest
    doctest.testmod()
