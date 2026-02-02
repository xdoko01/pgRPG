''' Module "example_game.core.components.sound_fx_on_movement" contains
SoundFXOnMovement component implemented as a SoundFXOnMovement class.

Use 'python -m example_game.core.components.sound_fx_on_movement -v' to run
module tests.
'''
import pyrpg.core.sounds.sound as sound # For cached sounds

from pyrpg.core.ecs import Component
from pyrpg.core.config import FILEPATHS, Path # SOUND_PATH, Path # for SOUND_PATH, Path

class SoundFXOnMovement(Component):
    ''' Game plays sound effect upon movement of the entity.

    Used by:
        - GenerateSoundFXOnMovementProcessor

    Examples of JSON definition:
        {"type" : "SoundFXOnMovement", "params" : {"sound" : "explosion.wav"}}

    Tests:
        >>> c = SoundFXOnMovement(**{"sound" : "explosion.wav"})
    '''

    __slots__ = ['sound', 'volume']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new SoundFXOnMovement component.

        Parameters:
            :param sound: Filename of the sound effect - reference to sound file.
            :type sound: str

            :param volume: Volume of the effect. (optional, default = 1.0)
            :type sound: str

        '''
        super().__init__()

        # Get the sound file name
        sound_file = kwargs.get('sound')

        # Get the volume or set the default value if not set
        self.volume = kwargs.get('volume', 1.0)

        # Check the sound_file name for validity
        try:
            assert isinstance(sound_file, str), f'Sound file name "{sound_file}" is not valid.'
            assert isinstance(self.volume, float) and 0.0 <= self.volume <= 1, f'Volume must be between 0.0 and 1.0. Current value "{self.volume}" is not valid.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Initiate new sound
        try:
            self.sound = sound.load_sound(FILEPATHS["SOUND_PATH"] / Path(sound_file))
        except:
            print(f'Something went wrong during initiation of the sound "{FILEPATHS["SOUND_PATH"]  / Path(sound_file)}".')
            # Notify component factory that initiation has failed
            raise ValueError

if __name__ == '__main__':
    import doctest
    doctest.testmod()
