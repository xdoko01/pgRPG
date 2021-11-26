''' Module "pyrpg.core.ecs.components.flag_add_damage" contains
FlagAddDamage component implemented as a FlagAddDamage class.

Use 'python -m pyrpg.core.ecs.components.flag_add_damage -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagAddDamage(Component):
    ''' Flag/tag to mark entity  which has beer damaged.

    Used by:
        - CollisionDamageProcessor
        - CalculateDamageProcessor


    Examples of JSON definition:
        {"type" : "FlagAddDamage", "params" : {"damage" : 5}}
        {"type" : "FlagAddDamage", "params" : {"damage" : 5, "src_entity" : 2}}


    Tests:
        >>> c = FlagAddDamage(**{"damage" : 5})
        >>> c.damage
        5
        >>> c = FlagAddDamage(**{"damage" : 10, "src_entity" : 2})
        >>> c.src_entity
        2
    '''

    __slots__ = ['damage', 'src_entity']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new FlagAddDamage component.

        Parameters:
            :param damage: Count of Damage points to be added
            :type damage: int

            :param src_entity: Originator of the damage (optional)
            :type src_entity: entity_id
        '''
        super().__init__()

        # Get the damage and originator
        self.damage = kwargs.get('damage')
        self.src_entity = kwargs.get('src_entity', None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
