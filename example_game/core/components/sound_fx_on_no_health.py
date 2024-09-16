''' Module "pyrpg.core.ecs.components.sound_fx_on_no_health" contains
SoundFXOnNoHealth component implemented as a SoundFXOnNoHealth class.

Use 'python -m pyrpg.core.ecs.components.sound_fx_on_no_health -v' to run
module tests.
'''
import pyrpg.core.sounds.sound as sound # For cached sounds

from pyrpg.core.ecs.components.component import Component
from pyrpg.core.config.filepaths import FILEPATHS, Path # for SOUND_PATH, Path

class SoundFXOnNoHealth(Component):
    ''' Game plays sound effect upon destroy of the entity.

    Used by:
        - GenerateSoundFXOnNoHealthProcessor

    Examples of JSON definition:
        {"type" : "SoundFXOnNoHealth", "params" : {"sound" : "explosion.wav"}}

    Tests:
        >>> c = SoundFXOnNoHealth(**{"sound" : "explosion.wav"})
    '''

    __slots__ = ['sound']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new SoundFXOnNoHealth component.

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
