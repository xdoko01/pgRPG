""" Module for loading, handling and caching Sounds.
"""

import functools        # for cache decorator
from pygame import mixer
from pathlib import Path

def load_sound(filepath: Path):
    """ Loads sound and returns the new sound instance.

    Parameters:
        :param filepath: Path to Sound file
        :type filepath: Path

        :return: Returns Sound instance, if success

        :raises: ValueException, if Sound cannot be created
    """

    try:
        new_sound = Sound(filepath)
    except ValueError:
        print(f"Error during init of the model '{filepath}'")
        raise ValueError

    return new_sound

def get_cache_info():
    print(Sound.cache_info())

def clear_cache():
    Sound.cache_clear()

# Cached sound class
@functools.lru_cache(maxsize=32)
class Sound(mixer.Sound):
    """ Object representing the sound.
    """

    def __init__(self, sound_file: Path):

        try:
            super().__init__(str(sound_file))
        except FileNotFoundError:
            print(f"File '{str(sound_file)}' not found.")
            raise

    def __str__(self):

        from pprint import pformat
        import ctypes           # to show number of references to an instance

        return f"\n*Instance of {self.__class__.__name__} ({hex(id(self))}) [{ctypes.c_long.from_address(id(self)).value}]"
