''' Module "example_game.core.components.flag_was_disarmed_as_weapon_by" contains
FlagWasDisarmedAsAmmoBy component implemented as a FlagWasDisarmedAsAmmoBy class.

Use 'python -m example_game.core.components.flag_was_disarmed_as_weapon_by -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagWasDisarmedAsAmmoBy(Component):
    ''' Weapon entity was disarmed as ammo by some other entity.

    Used by:
        -   PerformDisarmAmmoProcessor

    '''

    __slots__ = ['fighter']

    def __init__(self, fighter):
        ''' Initiate value for the new FlagWasDisarmedAsAmmoBy component.

        Parameters:
            :param fighter: Entity ID that has disarmed given entity/weapon
            :type fighter: int

        '''
        super().__init__()

        self.fighter = fighter


if __name__ == '__main__':
    import doctest
    doctest.testmod()
