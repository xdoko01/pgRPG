# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import FILEPATHS # FONT_PATH # for font path
from pyrpg.core.config import FONTS # for fonts modification

_INIT: bool = False

def get_init() -> bool:
    """Return True, if console config is already initiated.
    """
    return _INIT

def init() -> None:
    """Prepare the config data.
    """
    import pyrpg.utils as utils# for BitmapFont class
    import pygame # for pygame.Color

    # Font for in-game dialog bubbles
    FONTS["GAME_DEBUG_FONT"] = utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["GAME_DEBUG_FONT"], color=pygame.Color('#000001'))
    FONTS["PLAYER_TALK_FONT"] = utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["PLAYER_TALK_FONT"])

    # Font for in-game messages such as 'item picked'
    FONTS["GAME_MSG_FONT"]= utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["GAME_MSG_FONT"])

    # Font or GUI manager
    FONTS["GUI_MANAGER_FONT"]= utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["GUI_MANAGER_FONT"])

    import pprint
    logger.debug(f"Fonts config initiated. {pprint.pformat(FONTS)}")

    global _INIT
    _INIT = True


def convert_dict_conf_to_vars() -> None:
    """ Add access to FONTS dictionary keys as variables of this module.
    Now it is able to get the configuration as follows:
    
        from pyrpg.core.config.fonts import GAME_MSG_FONT

    Without this, you would always need to use the following way

        from pyrpg.core.config.fonts import FONTS
        GAME_MSG_FONT = FONTS["GAME_MSG_FONT"]
    """
    globals().update((k,v) for k, v in FONTS.items())

    logger.debug(f"Fonts config values initiated as vars.")
