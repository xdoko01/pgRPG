''' Module "pyrpg.core.ecs.components.new_flag_has_armed_ammo" contains
NewFlagHasArmedAmmo component implemented as a NewFlagHasArmedAmmo class.

Use 'python -m pyrpg.core.ecs.components.new_flag_has_armed_ammo -v' to run
module tests.
'''

from .component import Component

class NewFlagHasArmedAmmo(Component):
    ''' Entity (fighter) has armed some other entity/ammo.

    Used by:
        -   NewPerformArmAmmoProcessor

    '''

    __slots__ = ['ammo']

    def __init__(self, ammo):
        ''' Initiate value for the new NewFlagHasArmedAmmo component.

        Parameters:
            :param ammo: Entity ID that has been picked
            :type ammo: int

        '''
        super().__init__()

        self.weapon = ammo


if __name__ == '__main__':
    import doctest
    doctest.testmod()
