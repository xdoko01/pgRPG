''' Module "example_game.core.components.flag_is_about_to_drop_entity" contains
FlagIsAboutToDropEntity component implemented as a FlagIsAboutToDropEntity class.

Use 'python -m example_game.core.components.flag_is_about_to_drop_entity -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagIsAboutToDropEntity(Component):
    ''' Entity (dropper) is about to drop some other entity.

    Used by:
        -   PerformDropProcessor

    '''

    __slots__ = ['entity_for_drop', 'categories']

    def __init__(self, entity_for_drop, categories):
        ''' Initiate value for the new FlagIsAboutToDropEntity component.

        Parameters:
            :param entity_for_drop: Entity ID to be dropped
            :type entity_for_drop: int

            :param categories: List of categories where entity id was assigned and is being removed from
            :type categories: list

        '''
        super().__init__()

        self.entity_for_drop = entity_for_drop
        self.categories = categories



if __name__ == '__main__':
    import doctest
    doctest.testmod()
