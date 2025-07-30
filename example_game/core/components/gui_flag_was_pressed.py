''' Module "example_game.core.components.gui_flag_was_pressed" contains
GUIFlagWasPressed component implemented as a GUIFlagWasPressed class.

Use 'python -m example_game.core.components.gui_flag_was_pressed -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class GUIFlagWasPressed(Component):
    ''' Flag that the entity animation frame is marked as action frame
    '''

    __slots__ = []

    def __init__(self):
        ''' Initiate values for the new GUIFlagWasPressed component.
        '''
        super().__init__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
