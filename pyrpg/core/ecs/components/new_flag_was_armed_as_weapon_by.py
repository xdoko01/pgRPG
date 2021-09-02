''' Module "pyrpg.core.ecs.components.new_flag_was_armed_as_weapon_by" contains
NewFlagWasArmedAsWeaponBy component implemented as a NewFlagWasArmedAsWeaponBy class.

Use 'python -m pyrpg.core.ecs.components.new_flag_was_armed_as_weapon_by -v' to run
module tests.
'''

from .component import Component

class NewFlagWasArmedAsWeaponBy(Component):
    ''' Weapon entity was armed as weapon by some other entity.

    Used by:
        -   NewPerformArmWeaponProcessor

    '''

    __slots__ = ['fighter']

    def __init__(self, fighter):
        ''' Initiate value for the new NewFlagWasArmedAsWeaponBy component.

        Parameters:
            :param fighter: Entity ID that has armed given entity/weapon
            :type fighter: int

        '''
        super().__init__()

        self.fighter = fighter


if __name__ == '__main__':
    import doctest
    doctest.testmod()
