from pyrpg.core.config import MODULEPATHS

# Init logging config
import logging
logger = logging.getLogger(__name__)

import pprint
logger.debug(f"Modulepaths config initiated. {pprint.pformat(MODULEPATHS)}")
