'''Sound Manager'''

# Initiate logging
import logging

logger = logging.getLogger(__name__)

import pygame.mixer
from pyrpg.core.sounds.sound import get_cache_info, clear_cache

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