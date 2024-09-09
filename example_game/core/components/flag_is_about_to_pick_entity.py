''' Module "pyrpg.core.ecs.components.flag_is_about_to_pick_entity" contains
FlagIsAboutToPickEntity component implemented as a FlagIsAboutToPickEntity class.

Use 'python -m pyrpg.core.ecs.components.flag_is_about_to_pick_entity -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagIsAboutToPickEntity(Component):
    ''' Entity (potential picker) is about to pick some other entity (pickable), if capable
    of picking.

    Used by:
        -   GeneratePickupProcessor

    '''

    __slots__ = ['entity_for_pickup', 'category']

    def __init__(self, entity_for_pickup=None, category=None):
        ''' Initiate value for the new FlagIsAboutToPickEntity component.

        Parameters:
            :param entity_for_pickup: Entity ID of pickable entity
            :type entity_for_pickup: int

            :param category: Category of pickable entity, used for storage in the proper inventory category
            :type category: str

        '''
        super().__init__()

        self.entity_for_pickup = entity_for_pickup
        self.category = category


if __name__ == '__main__':
    import doctest
    doctest.testmod()
