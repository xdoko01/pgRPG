''' Module "example_game.core.components.flag_has_disarmed_weapon" contains
FlagHasDisarmedWeapon component implemented as a FlagHasDisarmedWeapon class.

Use 'python -m example_game.core.components.flag_has_disarmed_weapon -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagHasDisarmedWeapon(Component):
    ''' Entity (fighter) has disarmed some other entity/weapon.

    Used by:
        -   PerformDisarmWeaponProcessor

    '''

    __slots__ = ['weapon']

    def __init__(self, weapon):
        ''' Initiate value for the new FlagHasDisarmedWeapon component.

        Parameters:
            :param weapon: Entity ID that has been picked
            :type weapon: int

        '''
        super().__init__()

        self.weapon = weapon


if __name__ == '__main__':
    import doctest
    doctest.testmod()
