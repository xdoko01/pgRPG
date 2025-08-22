''' Module "example_game.core.components.flag_is_about_to_disarm_ammo" contains
FlagIsAboutToDisarmAmmo component implemented as a FlagIsAboutToDisarmAmmo class.

Use 'python -m example_game.core.components.flag_is_about_to_disarm_ammo -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagIsAboutToDisarmAmmo(Component):
    ''' Entity (fighter) is about to disarm some other picked entity (ammo), if capable
    of wearing a weapon.

    Used by:
        -   GenerateDisarmAmmoProcessor
        -   PerformDisarmAmmoProcessor

    '''

    __slots__ = ['ammo', 'type']

    def __init__(self, ammo, type):
        ''' Initiate value for the new FlagIsAboutToDisarmAmmo component.

        Parameters:
            :param ammo: Entity ID of ammo entity
            :type ammo: int

            :param type: Type of the ammo weapon (bow, sword, etc)
            :type type: str

        '''
        super().__init__()

        self.ammo = ammo
        self.type = type


if __name__ == '__main__':
    import doctest
    doctest.testmod()
