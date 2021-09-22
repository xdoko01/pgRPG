''' Module "pyrpg.core.ecs.components.new_flag_is_animation_action_frame" contains
NewFlagIsAnimationActionFrame component implemented as a NewFlagIsAnimationActionFrame class.

Use 'python -m pyrpg.core.ecs.components.new_flag_is_animation_action_frame -v' to run
module tests.
'''

from .component import Component

class NewFlagIsAnimationActionFrame(Component):
    ''' Flag that the entity animation frame is marked as action frame
    '''

    __slots__ = []

    def __init__(self):
        ''' Initiate values for the new NewFlagIsAnimationActionFrame component.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
