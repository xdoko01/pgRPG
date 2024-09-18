# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import MESSAGES

import pprint
logger.debug(f"Messages config initiated. {pprint.pformat(MESSAGES)}")
