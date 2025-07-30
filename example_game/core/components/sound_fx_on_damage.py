''' Module "example_game.core.components.sound_fx_on_damage" contains
SoundFXOnDamage component implemented as a SoundFXOnDamage class.

Use 'python -m example_game.core.components.sound_fx_on_damage -v' to run
module tests.
'''
import pyrpg.core.sounds.sound as sound # For cached sounds

from pyrpg.core.ecs import Component
from pyrpg.core.config import FILEPATHS, Path #SOUND_PATH, Path # for SOUND_PATH, Path

class SoundFXOnDamage(Component):
    ''' Game plays sound effect upon damage of the entity.

    Used by:
        - GenerateSoundFXOnDamageProcessor

    Examples of JSON definition:
        {"type" : "SoundFXOnDamage", "params" : {"sound" : "explosion.wav"}}

    Tests:
        >>> c = SoundFXOnDamage(**{"sound" : "explosion.wav"})
    '''

    __slots__ = ['sound', 'stop_before_playback']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new SoundFXOnDamage component.

        Parameters:
            :param sound: Filename of the sound effect - reference to sound file.
            :type sound: str

            :param stop_before_playback: stop the sound before playing it again (one man cannot shout more sounds at once)
            :type stop_before_playback: bool
        '''
        super().__init__()

        # Get the sound file name
        sound_file = kwargs.get('sound')
        stop_before_playback = kwargs.get('stop_before_playback', False)

        # Check the sound_file name for validity
        try:
            assert isinstance(sound_file, str), f'Sound file name "{sound_file}" is not valid.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        self.stop_before_playback = stop_before_playback

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
