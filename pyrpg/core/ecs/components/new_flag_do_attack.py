''' Module "pyrpg.core.ecs.components.new_flag_do_attack" contains
NewFlagDoAttack component implemented as a NewFlagDoAttack class.

Use 'python -m pyrpg.core.ecs.components.new_flag_do_attack -v' to run
module tests.
'''

from .component import Component

class NewFlagDoAttack(Component):
    ''' Flag that the entity has performed an attack.
    '''

    __slots__ = []

    def __init__(self):
        ''' Initiate values for the new NewFlagDoAttack component.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
