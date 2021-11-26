''' Module "pyrpg.core.ecs.components.new_flag_is_about_to_pick_entity" contains
NewFlagIsAboutToPickEntity component implemented as a NewFlagIsAboutToPickEntity class.

Use 'python -m pyrpg.core.ecs.components.new_flag_is_about_to_pick_entity -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewFlagIsAboutToPickEntity(Component):
    ''' Entity (potential picker) is about to pick some other entity (pickable), if capable
    of picking.

    Used by:
        -   NewGeneratePickUpProcessor

    '''

    __slots__ = ['entity_for_pickup']

    def __init__(self, entity_for_pickup=None):
        ''' Initiate value for the new NewFlagIsAboutToPickEntity component.

        Parameters:
            :param entity_for_pickup: Entity ID of pickable entity
            :type entity_for_pickup: int

        '''
        super().__init__()

        self.entity_for_pickup = entity_for_pickup


if __name__ == '__main__':
    import doctest
    doctest.testmod()
