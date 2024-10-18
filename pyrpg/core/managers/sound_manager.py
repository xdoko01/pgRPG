'''Sound Manager'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

import pygame.mixer
from pyrpg.core.sounds.sound import get_cache_info, clear_cache

logger.info(f'Sound Manager module initiated')

def init():
    pass

def play_sound(sound_obj: pygame.mixer.Sound, stop_before_playback: bool=False) -> None:
    """
    Parameters:
        :stop_before_playback: if the same instance of the sound is already playing, 
                               stop it before playing again.
    """
    if stop_before_playback: sound_obj.stop()

    pygame.mixer.Sound.play(sound_obj)
    logger.debug(f'Sound "{sound_obj}" played.')

def get_sound_cache_info():
    return get_cache_info()

def clear():
    clear_cache()

"""
class SoundManager:
    '''Manages all sound resources and provides services for sound playback.'''

    def __init__(self):
        logger.info(f'SoundManager initiated')

    def play_sound(self, sound_obj: pygame.mixer.Sound) -> None:
        pygame.mixer.Sound.play(sound_obj)
        logger.debug(f'Sound "{sound_obj}" played.')

    def get_sound_cache_info(self):
        return get_cache_info()

    def clear(self):
        clear_cache()
"""