''' Module "example_game.core.components.flag_was_armed_as_weapon_by" contains
FlagWasArmedAsWeaponBy component implemented as a FlagWasArmedAsWeaponBy class.

Use 'python -m example_game.core.components.flag_was_armed_as_weapon_by -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagWasArmedAsWeaponBy(Component):
    ''' Weapon entity was armed as weapon by some other entity.

    Used by:
        -   PerformArmWeaponProcessor

    '''

    __slots__ = ['fighter']

    def __init__(self, fighter):
        ''' Initiate value for the new FlagWasArmedAsWeaponBy component.

        Parameters:
            :param fighter: Entity ID that has armed given entity/weapon
            :type fighter: int

        '''
        super().__init__()

        self.fighter = fighter


if __name__ == '__main__':
    import doctest
    doctest.testmod()
