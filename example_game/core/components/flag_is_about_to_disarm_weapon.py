''' Module "example_game.core.components.flag_is_about_to_disarm_weapon" contains
FlagIsAboutToDisarmWeapon component implemented as a FlagIsAboutToDisarmWeapon class.

Use 'python -m example_game.core.components.flag_is_about_to_disarm_weapon -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagIsAboutToDisarmWeapon(Component):
    ''' Entity (fighter) is about to disarm some other picked entity (weapon), if capable
    of wearing a weapon.

    Used by:
        -   GenerateDisarmWeaponProcessor
        -   PerformDisarmWeaponProcessor

    '''

    __slots__ = ['weapon', 'type']

    def __init__(self, weapon, type):
        ''' Initiate value for the new FlagIsAboutToDisarmWeapon component.

        Parameters:
            :param weapon: Entity ID of weapon entity
            :type weapon: int

            :param type: Type of the weapon (bow, sword, etc)
            :type type: str

        '''
        super().__init__()

        self.weapon = weapon
        self.type = type


if __name__ == '__main__':
    import doctest
    doctest.testmod()
