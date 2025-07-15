''' Module "pyrpg.core.ecs.components.flag_is_about_to_arm_ammo" contains
FlagIsAboutToArmAmmo component implemented as a FlagIsAboutToArmAmmo class.

Use 'python -m pyrpg.core.ecs.components.flag_is_about_to_arm_ammo -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagIsAboutToArmAmmo(Component):
    ''' Entity (fighter) is about to arm some other picked entity (ammo), if capable
    of wearing a weapon.

    Used by:
        -   GenerateArmAmmoProcessor

    '''

    __slots__ = ['ammo', 'weapon', 'type', 'total_units', 'used_units']

    def __init__(self, ammo, weapon, type, total_units, used_units):
        ''' Initiate value for the new FlagIsAboutToArmAmmo component.

        Parameters:
            :param ammo: Entity ID of ammo entity
            :type ammo: int

            :param weapon: Type of the weapon suitable for ammo (bow, sword, etc)
            :type weapon: str

            :param type: Type of the ammo so that same ammo types can be merged together
            :type type: str

            :param total_units: Number of pieces of ammo available in the ammo pack
            :type total_units: int

            :param used_units: Number of pieces of ammo already depleted from the ammo pack
            :type used_units: int
        '''
        super().__init__()

        self.ammo = ammo
        self.weapon = weapon
        self.type = type
        self.total_units = total_units
        self.used_units = used_units


if __name__ == '__main__':
    import doctest
    doctest.testmod()
