# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import GAME

import pprint
logger.debug(f"Game config initiated. {pprint.pformat(GAME)}")
