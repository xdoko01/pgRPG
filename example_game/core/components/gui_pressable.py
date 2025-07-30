''' Module "example_game.core.components.gui_button" contains
GUIButton component implemented as a GUIButton class.

Use 'python -m example_game.core.components.gui_button -v' to run
module tests.
'''
from pyrpg.core.ecs import Component
from pyrpg.core.commands import cmd_factory

class Pressable(Component):
    ''' Game plays sound effect upon collision with other entity.

    Used by:
        - GenerateSoundFXOnCollisionProcessor

    Examples of JSON definition:
        {"type" : "SoundFXOnCollision", "params" : {"sound" : "explosion.wav"}}

    Tests:
        >>> c = SoundFXOnCollision(**{"sound" : "explosion.wav"})
    '''

    __slots__ = ['cmds']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new GUIButton component.

        Parameters:
            :param cmds: List of commands to be added to the command queue
            :type cmds: list

        '''
        super().__init__()

        # Transform the commands in the form of list to the form of Commands
        self.cmds = [cmd_factory(cmd) for cmd in kwargs.get('cmds', [])]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
