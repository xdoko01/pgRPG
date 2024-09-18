# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import FILEPATHS
from pathlib import Path

def init() -> None:
    """Prepare the config data.
    """

    # Convert filepaths to Paths
    for path_name, path_rel in FILEPATHS.copy().items():
        FILEPATHS[path_name] = Path(FILEPATHS["GAME_PATH"], path_rel) if path_name not in ("GAME_PATH", "PYRPG_PATH") else Path(path_rel)

    import pprint
    logger.debug(f"Filepaths config initiated. {pprint.pformat(FILEPATHS)}")


def convert_dict_conf_to_vars() -> None:
    """ Add access to FILEPATHS dictionary keys as variables of this module.
    Now it is able to get the configuration as follows:
    
        from pyrpg.core.config.filepaths import GAME_PATH

    Without this, you would always need to use the following way

        from pyrpg.core.config. filepaths import FILEPATHS
        GAME_PATH = FILEPATHS["GAME_PATH"]
    """
    globals().update((k,v) for k, v in FILEPATHS.items())

    logger.debug(f"Filepaths config values initiated as vars.")
