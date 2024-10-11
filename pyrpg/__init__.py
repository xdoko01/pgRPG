# Init logging config
import logging
logger = logging.getLogger(__name__)

# Get process object to determine info about python process (mem usage etc.)
import os, psutil
logger.info(f'pyRPG process running as PID={os.getpid()}.')
python_process = psutil.Process(os.getpid())


# Via this global variable, console can access all game properties
main = None

def init(config_file: str, console: bool=True, scene_file: str=None, timed: bool=False) -> None:
    '''Create instance of main game class and remember it in 
    form of global variable so that console can use it'''
    
    # Load config
    from pyrpg.core.config import load
    load(config_file=config_file)
    logger.info(f"Config successfully loaded.")

    # Start the engine
    global main
    from pyrpg.core.main import Main
    main = Main(console=console, filepath=scene_file, timed=timed)
    logger.info(f'Instance of Main class created as "{main}".')

    # Main loop
    logger.info(f'Starting the main loop.')
    main.run()

def exit() -> None:
    '''Clears the references and exits'''
    global main

    main.end()
    main = None
    logger.info(f'PyRPG quits.')


'''
Functions that feed the console with header and footer data.
'''

def cons_get_info_header():
    '''Returns info that is displayed in the console's header'''

    memory_use = python_process.memory_info()[0]/2.**30  # memory use in GB...I think
    game_state = main.state_manager.game_state if main else 'N/A'
    no_of_entities =  len(main.engine.ecs_manager._world._entities) if main and main.engine else 'N/A'

    return f'memory usage: {memory_use} GB | game state: {str(game_state)} | ECS entities: {no_of_entities}'

def cons_get_info_footer():
    '''Returns info that is displayed in the console's footer'''

    loaded_quests = main.engine._scenes.keys() if main and main.engine else 'N/A'

    return f'loaded scenes: {loaded_quests}'
