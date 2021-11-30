''' Module "pyrpg.core.ecs.components.flag_has_picked" contains
FlagHasPicked component implemented as a FlagHasPicked class.

Use 'python -m pyrpg.core.ecs.components.flag_has_picked -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagHasPicked(Component):
    ''' Entity (picker) has picked some other entity.

    Used by:
        -   PerformPickupProcessor

    '''

    __slots__ = ['entity']

    def __init__(self, entity=None):
        ''' Initiate value for the new FlagHasPicked component.

        Parameters:
            :param entity: Entity ID that has been picked
            :type entity: int

        '''
        super().__init__()

        self.entity = entity


if __name__ == '__main__':
    import doctest
    doctest.testmod()
