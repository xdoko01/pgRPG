''' Module "pyrpg.core.ecs.components.new_flag_has_picked" contains
NewFlagHasPicked component implemented as a NewFlagHasPicked class.

Use 'python -m pyrpg.core.ecs.components.new_flag_has_picked -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewFlagHasPicked(Component):
    ''' Entity (picker) has picked some other entity.

    Used by:
        -   NewPerformPickupProcessor

    '''

    __slots__ = ['entity']

    def __init__(self, entity=None):
        ''' Initiate value for the new NewFlagHasPicked component.

        Parameters:
            :param entity: Entity ID that has been picked
            :type entity: int

        '''
        super().__init__()

        self.entity = entity


if __name__ == '__main__':
    import doctest
    doctest.testmod()
