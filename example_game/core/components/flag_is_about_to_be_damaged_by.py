''' Module "pyrpg.core.ecs.components.flag_is_about_to_be_damaged_by" contains
FlagIsAboutToBeDamagedBy component implemented as a FlagIsAboutToBeDamagedBy class.

Use 'python -m pyrpg.core.ecs.components.flag_is_about_to_be_damaged_by -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagIsAboutToBeDamagedBy(Component):
    ''' Entity (potential damagee) is about to be damaged by damaging item, 
    if damageable.

    Used by:
        -   GenerateDamageProcessor
    '''

    __slots__ = ['damages']

    def __init__(self, damages=[]):
        ''' Initiate value for the new FlagIsAboutToBeDamagedBy component.

        Parameters:
            :param damages: List of damage objects defining the damage
            :type damages: list
        '''
        super().__init__()

        self.damages = damages


if __name__ == '__main__':
    import doctest
    doctest.testmod()
