''' Module "example_game.core.components.gui_button" contains
GUIButton component implemented as a GUIButton class.

Use 'python -m example_game.core.components.gui_button -v' to run
module tests.
'''
import pygame
from pgrpg.core.ecs import Component
from pgrpg.core.engine import gui_manager

class GUIButton(Component):
    ''' Game plays sound effect upon collision with other entity.

    Used by:
        - GenerateSoundFXOnCollisionProcessor

    Examples of JSON definition:
        {"type" : "SoundFXOnCollision", "params" : {"sound" : "explosion.wav"}}

    Tests:
        >>> c = SoundFXOnCollision(**{"sound" : "explosion.wav"})
    '''

    __slots__ = ['button','text','name']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new GUIButton component.

        Parameters:
            :param relative_rect: 
            :type relative_rect: pygame.Rect

            :param text: 
            :type text: str
        '''
        super().__init__()

        self.name = kwargs['name']
        self.text = kwargs.get('text', self)

        self.button = gui_manager.pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((kwargs.get('x', 0), kwargs.get('y',0)), (kwargs.get('width', 100), kwargs.get('height', 100))), 
            text=str(self.text),
            manager=gui_manager.window_manager, 
            container=None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
