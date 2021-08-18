import logging

logger = logging.getLogger(__name__)

logger.info(f'This is info log from the module 3.')
logger.debug(f'This is debug log from the module 3.')
logger.warning(f'This is warning log from the module 3.')
logger.critical(f'This is critical log from the module 3.')

def test():
	logger.info(f'This is info log from the module 3 -> test fnc.')
	logger.debug(f'This is debug log from the module 3 -> test fnc.')
	logger.warning(f'This is warning log from the module 3 -> test fnc.')
	logger.critical(f'This is critical log from the module 3 -> test fnc.')