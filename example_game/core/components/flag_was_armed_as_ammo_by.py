''' Module "pyrpg.core.ecs.components.flag_was_armed_as_ammo_by" contains
FlagWasArmedAsAmmoBy component implemented as a FlagWasArmedAsAmmoBy class.

Use 'python -m pyrpg.core.ecs.components.flag_was_armed_as_ammo_by -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagWasArmedAsAmmoBy(Component):
    ''' Weapon entity was armed as ammo by some other entity.

    Used by:
        -   PerformArmAmmoProcessor

    '''

    __slots__ = ['fighter']

    def __init__(self, fighter):
        ''' Initiate value for the new FlagWasArmedAsAmmoBy component.

        Parameters:
            :param fighter: Entity ID that has armed given entity/ammo
            :type fighter: int

        '''
        super().__init__()

        self.fighter = fighter


if __name__ == '__main__':
    import doctest
    doctest.testmod()
