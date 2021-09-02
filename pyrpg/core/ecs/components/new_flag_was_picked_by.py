''' Module "pyrpg.core.ecs.components.new_flag_was_picked_by" contains
NewFlagWasPickedBy component implemented as a NewFlagWasPickedBy class.

Use 'python -m pyrpg.core.ecs.components.new_flag_was_picked_by -v' to run
module tests.
'''

from .component import Component

class NewFlagWasPickedBy(Component):
    ''' Entity was picked by some other entity.

    Used by:
        -   NewPerformPickupProcessor

    '''

    __slots__ = ['picker']

    def __init__(self, picker=None):
        ''' Initiate value for the new NewFlagWasPickedBy component.

        Parameters:
            :param picker: Entity ID that has picked given entity
            :type picker: int

        '''
        super().__init__()

        self.picker = picker


if __name__ == '__main__':
    import doctest
    doctest.testmod()
