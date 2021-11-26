''' Module "pyrpg.core.ecs.components.new_flag_is_about_to_arm_weapon" contains
NewFlagIsAboutToArmWeapon component implemented as a NewFlagIsAboutToArmWeapon class.

Use 'python -m pyrpg.core.ecs.components.new_flag_is_about_to_arm_weapon -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewFlagIsAboutToArmWeapon(Component):
    ''' Entity (fighter) is about to arm some other picked entity (weapon), if capable
    of wearing a weapon.

    Used by:
        -   NewGenerateArmWeaponProcessor

    '''

    __slots__ = ['weapon', 'type']

    def __init__(self, weapon, type):
        ''' Initiate value for the new NewFlagIsAboutToArmWeapon component.

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
