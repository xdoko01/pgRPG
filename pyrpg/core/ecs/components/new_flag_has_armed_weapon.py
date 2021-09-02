''' Module "pyrpg.core.ecs.components.new_flag_has_armed_weapon" contains
NewFlagHasArmedWeapon component implemented as a NewFlagHasArmedWeapon class.

Use 'python -m pyrpg.core.ecs.components.new_flag_has_armed_weapon -v' to run
module tests.
'''

from .component import Component

class NewFlagHasArmedWeapon(Component):
    ''' Entity (fighter) has armed some other entity/weapon.

    Used by:
        -   NewPerformArmWeaponProcessor

    '''

    __slots__ = ['weapon']

    def __init__(self, weapon):
        ''' Initiate value for the new NewFlagHasArmedWeapon component.

        Parameters:
            :param weapon: Entity ID that has been picked
            :type weapon: int

        '''
        super().__init__()

        self.weapon = weapon


if __name__ == '__main__':
    import doctest
    doctest.testmod()
