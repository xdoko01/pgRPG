''' Module "pyrpg.core.ecs.components.flag_no_health" contains
FlagNoHealth component implemented as a FlagNoHealth class.

Use 'python -m pyrpg.core.ecs.components.flag_no_health -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagNoHealth(Component):
    ''' Component tagging entity as destroyed

    Used by:
        - CalculateDamageProcessor
        - RenderableModelAnimationActionProcessor

    Examples of JSON definition:
        {"type" : "FlagNoHealth", "params" : {}}

    Tests:
        >>> c = FlagNoHealth()
    '''

    __slots__ = ['src_entity']

    def __init__(self, *args, **kwargs):
        ''' Initiate FlagNoHealth tag.

            :param src_entity: The destroyer (optional)
            :type src_entity: entity_id
        '''
        super().__init__()

        self.src_entity = kwargs.get('src_entity', None)



if __name__ == '__main__':
    import doctest
    doctest.testmod()
