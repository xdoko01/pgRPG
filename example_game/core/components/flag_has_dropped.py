''' Module "example_game.core.components.flag_has_dropped" contains
FlagHasDropped component implemented as a FlagHasDropped class.

Use 'python -m example_game.core.components.flag_has_dropped -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagHasDropped(Component):
    ''' Entity (dropper) has dropped some other entity.

    Used by:
        -   PerformDropProcessor

    '''

    __slots__ = ['entity']

    def __init__(self, entity=None):
        ''' Initiate value for the new FlagHasDropped component.

        Parameters:
            :param entity: Entity ID that has been dropped
            :type entity: int

        '''
        super().__init__()

        self.entity = entity


if __name__ == '__main__':
    import doctest
    doctest.testmod()
