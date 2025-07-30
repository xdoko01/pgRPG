''' Module "example_game.core.components.flag_do_attack" contains
FlagDoAttack component implemented as a FlagDoAttack class.

Use 'python -m example_game.core.components.flag_do_attack -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class FlagDoAttack(Component):
    ''' Flag that the entity has performed an attack.
    '''

    __slots__ = []

    def __init__(self):
        ''' Initiate values for the new FlagDoAttack component.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
