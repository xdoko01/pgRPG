''' Module "pyrpg.core.ecs.components.new_flag_was_armed_as_ammo_by" contains
NewFlagWasArmedAsAmmoBy component implemented as a NewFlagWasArmedAsAmmoBy class.

Use 'python -m pyrpg.core.ecs.components.new_flag_was_armed_as_ammo_by -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewFlagWasArmedAsAmmoBy(Component):
    ''' Weapon entity was armed as ammo by some other entity.

    Used by:
        -   NewPerformArmAmmoProcessor

    '''

    __slots__ = ['fighter']

    def __init__(self, fighter):
        ''' Initiate value for the new NewFlagWasArmedAsAmmoBy component.

        Parameters:
            :param fighter: Entity ID that has armed given entity/ammo
            :type fighter: int

        '''
        super().__init__()

        self.fighter = fighter


if __name__ == '__main__':
    import doctest
    doctest.testmod()
