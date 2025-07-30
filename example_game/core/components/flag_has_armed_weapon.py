''' Module "example_game.core.components.flag_has_armed_weapon" contains
FlagHasArmedWeapon component implemented as a FlagHasArmedWeapon class.

Use 'python -m example_game.core.components.flag_has_armed_weapon -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagHasArmedWeapon(Component):
    ''' Entity (fighter) has armed some other entity/weapon.

    Used by:
        -   PerformArmWeaponProcessor

    '''

    __slots__ = ['weapon']

    def __init__(self, weapon):
        ''' Initiate value for the new FlagHasArmedWeapon component.

        Parameters:
            :param weapon: Entity ID that has been picked
            :type weapon: int

        '''
        super().__init__()

        self.weapon = weapon


if __name__ == '__main__':
    import doctest
    doctest.testmod()
