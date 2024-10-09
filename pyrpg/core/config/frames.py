# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import FILEPATHS #FRAME_PATH # for frame path
from pyrpg.core.config import FRAMES

def init() -> None:
    """Prepare the config data.
    """
    import pyrpg.utils as utils # for BitmapFrame class
    import pygame # for pygame.Color

    FRAMES["PLAYER_TALK_FRAME"] = utils.BitmapFrame(FILEPATHS["FRAME_PATH"] / FRAMES["PLAYER_TALK_FRAME"], color=pygame.Color('blue'))
    FRAMES["GAME_DEBUG_FRAME"] = utils.BitmapFrame(FILEPATHS["FRAME_PATH"] / FRAMES["GAME_DEBUG_FRAME"], color=pygame.Color('blue'))

    import pprint
    logger.debug(f"Frames config initiated. {pprint.pformat(FRAMES)}")

def convert_dict_conf_to_vars() -> None:
    """ Add access to FRAMES dictionary keys as variables of this module.
    Now it is able to get the configuration as follows:
    
        from pyrpg.core.config.frames import GAME_DEBUG_FRAME

    Without this, you would always need to use the following way

        from pyrpg.core.config.frames import FRAMES
        GAME_DEBUG_FRAME = FRAMES["GAME_DEBUG_FRAME"]
    """
    globals().update((k,v) for k, v in FRAMES.items())

    logger.debug(f"Frames config values initiated as vars.")
