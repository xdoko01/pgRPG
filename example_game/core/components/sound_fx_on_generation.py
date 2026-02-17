''' Module "example_game.core.components.sound_fx_on_generation" contains
SoundFXOnGeneration component implemented as a SoundFXOnGeneration class.

Use 'python -m example_game.core.components.sound_fx_on_generation -v' to run
module tests.
'''
import pgrpg.core.sounds.sound as sound # For cached sounds

from pgrpg.core.ecs import Component
from pgrpg.core.config import FILEPATHS, Path #SOUND_PATH, Path # for SOUND_PATH, Path

class SoundFXOnGeneration(Component):
    ''' Game plays sound effect upon generation of the entity
    from Factory generator.

    Used by:
        - GenerateSoundFXOnGenerationProcessor

    Examples of JSON definition:
        {"type" : "SoundFXOnGeneration", "params" : {"sound" : "explosion.wav"}}

    Tests:
        >>> c = SoundFXOnGeneration(**{"sound" : "explosion.wav"})
    '''

    __slots__ = ['sound']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new SoundFXOnGeneration component.

        Parameters:
            :param sound: Filename of the sound effect - reference to sound file.
            :type sound: str
        '''
        super().__init__()

        # Get the sound file name
        sound_file = kwargs.get('sound')

        # Check the sound_file name for validity
        try:
            assert isinstance(sound_file, str), f'Sound file name "{sound_file}" is not valid.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Initiate new sound
        try:
            self.sound = sound.load_sound(FILEPATHS["SOUND_PATH"] / Path(sound_file))
        except:
            print(f'Something went wrong during initiation of the sound "{FILEPATHS["SOUND_PATH"] / Path(sound_file)}".')
            # Notify component factory that initiation has failed
            raise ValueError

if __name__ == '__main__':
    import doctest
    doctest.testmod()
