# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import GUI

import pprint
logger.debug(f"Gui config initiated. {pprint.pformat(GUI)}")
