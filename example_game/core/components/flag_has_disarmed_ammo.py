''' Module "example_game.core.components.flag_has_disarmed_ammo" contains
FlagHasDisarmedAmmo component implemented as a FlagHasDisarmedAmmo class.

Use 'python -m example_game.core.components.flag_has_disarmed_ammo -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagHasDisarmedAmmo(Component):
    ''' Entity (fighter) has disarmed some other entity/ammo.

    Used by:
        -   PerformDisarmAmmoProcessor

    '''

    __slots__ = ['ammo']

    def __init__(self, ammo):
        ''' Initiate value for the new FlagHasDisarmedAmmo component.

        Parameters:
            :param ammo: Entity ID that has been picked
            :type ammo: int

        '''
        super().__init__()

        self.ammo = ammo


if __name__ == '__main__':
    import doctest
    doctest.testmod()
