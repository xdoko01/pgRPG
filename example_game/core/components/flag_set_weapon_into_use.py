''' Module "example_game.core.components.flag_set_weapon_into_use" contains
FlagSetWeaponIntoUse component implemented as a FlagSetWeaponIntoUse class.

Use 'python -m example_game.core.components.flag_set_weapon_into_use -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

from core.components.weapon import Weapon

class FlagSetWeaponIntoUse(Component):
    ''' Set the wepon type for usage.

    Used by:
        -   PerformSetWeaponIntoUseProcessor

    '''

    __slots__ = ['type', 'prev_ent_ids']

    def __init__(self, type, prev_ent_ids):
        ''' Initiate value for the new FlagSetWeaponIntoUse component.

        Parameters:
            :param type: Type of weapon to be used for usage
            :type type: str

            :param prev_ent_ids: Entity IDs where RenderDataFromParent needs to be removed
            :type prev_ent_ids: set

        '''
        super().__init__()

        self.type = type
        self.prev_ent_ids = prev_ent_ids

        assert self.type in Weapon.WEAPONS.keys(), f'Invalid weapon type: {self.type}'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
