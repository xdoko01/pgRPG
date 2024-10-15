"""
    - Load the configuration
    - Initiate the program and start into the main program loop
"""
# Init logging config
import logging
logger = logging.getLogger(__name__)

def init(config_file: str, console: bool=True, scene_file: str=None, timed: bool=False) -> None:
    """Create instance of main game class and remember it in 
    form of global variable so that console can use it."""
    
    # Load config
    from pyrpg.core.config import load
    load(config_file=config_file)
    logger.info(f"Config successfully loaded.")

    # Initiate the core funcionalities / managers
    from pyrpg.core import main
    main.init(console=console, scene_file=scene_file, timed=timed)
    logger.info(f"Main module initiation done.")

    # Main program loop
    logger.info(f'Starting the main loop.')
    main.run()


