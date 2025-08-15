''' Module "example_game.core.components.flag_is_about_to_drop_entity" contains
FlagIsAboutToDropEntity component implemented as a FlagIsAboutToDropEntity class.

Use 'python -m example_game.core.components.flag_is_about_to_drop_entity -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagIsAboutToDropEntity(Component):
    ''' Entity (dropper) is about to drop some other entity.

    Used by:
        -   PerformDropProcessor

    '''

    __slots__ = ['entity_for_drop']

    def __init__(self, entity_for_drop=None):
        ''' Initiate value for the new FlagIsAboutToDropEntity component.

        Parameters:
            :param entity_for_drop: Entity ID to be dropped
            :type entity_for_drop: int

            :param category: Category of pickable entity, used for storage in the proper inventory category
            :type category: str

        '''
        super().__init__()

        self.entity_for_drop = entity_for_drop


if __name__ == '__main__':
    import doctest
    doctest.testmod()
