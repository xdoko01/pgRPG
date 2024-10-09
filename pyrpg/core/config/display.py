# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import DISPLAY

def init() -> None:
    """Prepare the config data.
    """
    import pygame

    DISPLAY["WINDOW"] = pygame.display.set_mode(
        size=tuple(DISPLAY["RESOLUTION"]),
        flags=pygame.FULLSCREEN if DISPLAY["FULLSCREEN"] else 0,
        depth=DISPLAY["BITDEPTH"]
    )
    import pprint
    logger.debug(f"Display config initiated. {pprint.pformat(DISPLAY)}")

def convert_dict_conf_to_vars() -> None:
    """ Add access to DISPLAY dictionary keys as variables of this module.
    Now it is able to get the configuration as follows:
    
        from pyrpg.core.config.display import RESOLUTION

    Without this, you would always need to use the following way

        from pyrpg.core.config.display import DISPLAY
        RESOLUTION = DISPLAY["RESOLUTION"]
    """
    globals().update((k,v) for k, v in DISPLAY.items())
    
    logger.debug(f"Display config values initiated as vars.")
