''' Module "pyrpg.core.ecs.components.flag_has_armed_ammo" contains
FlagHasArmedAmmo component implemented as a FlagHasArmedAmmo class.

Use 'python -m pyrpg.core.ecs.components.flag_has_armed_ammo -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagHasArmedAmmo(Component):
    ''' Entity (fighter) has armed some other entity/ammo.

    Used by:
        -   PerformArmAmmoProcessor

    '''

    __slots__ = ['ammo']

    def __init__(self, ammo):
        ''' Initiate value for the new FlagHasArmedAmmo component.

        Parameters:
            :param ammo: Entity ID that has been picked
            :type ammo: int

        '''
        super().__init__()

        self.weapon = ammo


if __name__ == '__main__':
    import doctest
    doctest.testmod()
