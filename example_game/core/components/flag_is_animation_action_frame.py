''' Module "example_game.core.components.flag_is_animation_action_frame" contains
FlagIsAnimationActionFrame component implemented as a FlagIsAnimationActionFrame class.

Use 'python -m example_game.core.components.flag_is_animation_action_frame -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class FlagIsAnimationActionFrame(Component):
    ''' Flag that the entity animation frame is marked as action frame
    '''

    __slots__ = []

    def __init__(self):
        ''' Initiate values for the new FlagIsAnimationActionFrame component.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
