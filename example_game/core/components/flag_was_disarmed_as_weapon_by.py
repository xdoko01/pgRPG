''' Module "example_game.core.components.flag_was_disarmed_as_weapon_by" contains
FlagWasDisarmedAsWeaponBy component implemented as a FlagWasDisarmedAsWeaponBy class.

Use 'python -m example_game.core.components.flag_was_disarmed_as_weapon_by -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagWasDisarmedAsWeaponBy(Component):
    ''' Weapon entity was disarmed as weapon by some other entity.

    Used by:
        -   PerformDisarmWeaponProcessor

    '''

    __slots__ = ['fighter']

    def __init__(self, fighter):
        ''' Initiate value for the new FlagWasDisarmedAsWeaponBy component.

        Parameters:
            :param fighter: Entity ID that has disarmed given entity/weapon
            :type fighter: int

        '''
        super().__init__()

        self.fighter = fighter


if __name__ == '__main__':
    import doctest
    doctest.testmod()
