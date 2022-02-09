'''Sound Manager'''

# Initiate logging
import logging

logger = logging.getLogger(__name__)

class SoundManager:
    '''Manages all sound resources and provides services for sound playback.'''

    def __init__(self):
        logger.info(f'SoundManager initiated')
