''' Module "pyrpg.core.ecs.components.flag_adjust_damaging" contains
FlagAdjustDamaging component implemented as a FlagAdjustDamaging class.

Use 'python -m pyrpg.core.ecs.components.flag_adjust_damaging -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class FlagAdjustDamaging(Component):
    ''' Entity should adjust its damaging component by given inputs

    Used by:
        -   PerformAdjustDamagingProcessor
        -   RemoveFlagAdjustDamagingProcessor
    '''

    __slots__ = ['parent', 'damage_fnc']

    def __init__(self, parent, damage_fnc=[lambda y:y]):
        ''' Initiate value for the new FlagAdjustDamaging component.

        Parameters:
            :param parent: Parent as source of the damage
            :type parent: integer

            :param damage_fnc: Functions for modification of damage of component
            :type damage_fnc: list of functions

        '''
        super().__init__()

        self.parent = parent
        self.damage_fnc = damage_fnc

if __name__ == '__main__':
    import doctest
    doctest.testmod()
