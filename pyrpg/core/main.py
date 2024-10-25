# Init logging config
import logging
logger = logging.getLogger(__name__)

# Import configuration so it is available for the console commands - it is ok, because
# it was already initiated in pyrpg.__init__()
from pyrpg.core import config

# Initiate GUI manager - all configuration parameters are loaded in the gui_manager
from pyrpg.core.managers import gui_manager
gui_manager.init()

# Initiate Sound Manager
from pyrpg.core.managers import sound_manager
sound_manager.init()

# Initiate  Console Manager
from pyrpg.core.managers import console_manager

#def _init_console() -> None:
#    console_manager.init()
#    global console
#    console = console_manager.console

# Initiate State Manager
from pyrpg.core.managers import state_manager
state_manager.init()

# Initiate engine
engine = None
def _init_game(scene_file: str, timed: bool) -> None:
    # Create engine instance if not yet created
    global engine

    #if engine is None:
    from pyrpg.core import engine as e
    engine = e
        #e.init(gui_manager, sound_manager, timed=timed)
        #e.init(sound_manager, timed=timed)
    engine.init(timed=timed)
    engine.new_game(scene_file)

# MainMenu
from pyrpg.core.menus.main_menu import MainMenu
main_menu = MainMenu(gui_manager=gui_manager, state_manager=state_manager)

# LoadSceneMenu
from pyrpg.core.menus.load_scene_menu import LoadSceneMenu
load_scene_menu = LoadSceneMenu(gui_manager=gui_manager, state_manager=state_manager, init_game_fnc=_init_game)

# ExitMenu
from pyrpg.core.menus.exit_menu import ExitMenu
exit_menu = ExitMenu(gui_manager=gui_manager, state_manager=state_manager)








def init(console: bool=True, scene_file: str=None, timed: bool=False) -> None:

    # Init Console, if required
    if console: console_manager.init()
        #_init_console()
    logger.info(f"Console initiation done.")

    # Init game state - Start game into main menu or into the game
    if scene_file:
        _init_game(scene_file, timed)
        state_manager.change_state(State.GAME) # TODO: shouldnt this be part of init game??
        logger.info(f"Starting into the game.")
    else:
        state_manager.change_state(State.MAIN_MENU)
        logger.info(f"Starting into the main menu.")



# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config.keys import KEYS # for K_CONSOLE_TOGGLE
from pyrpg.core.config.display import DISPLAY # for MAX_FPS
from pyrpg.core.config.states import State
import pygame

def run():
    ''' Main game and menu loop. Contains references to other
    loop codes depending of current GameState
    '''

    # Fix of the problem with the first frame that has too
    # big dt and as a consequence the first movement with
    # the first frame is too big.
    # Calculate the first dt directly
    gui_manager.clock.tick(DISPLAY["MAX_FPS"])
    dt = 1000 / DISPLAY["MAX_FPS"] # ms

    while True:
        
        # Read the keys pressed, mouse, win resize etc.
        key_events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()

        for event in key_events:

            # Check for closing the main program window
            if event.type == pygame.QUIT:
                state_manager.change_state(State.EXIT_GAME_DIALOG)

            if event.type == pygame.KEYUP:
                if event.key == KEYS["K_CONSOLE_TOGGLE"] and console_manager.console:
                    if console_manager.console.toggle():
                        gui_manager.save_screen()
                        logger.info(f'Entering console')
                        state_manager.change_state(State.CONSOLE)
                    else:
                        logger.info(f'Exiting console')
                        state_manager.revert_state()

        match state_manager.state:
            case State.GAME: 
                state_manager.change_state(engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt))
            case State.MAIN_MENU:
                state_manager.change_state(main_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))
            case State.LOAD_QUEST_MENU:
                state_manager.change_state(load_scene_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))
            case State.EXIT_GAME_DIALOG:
                state_manager.change_state(exit_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))
            case State.CONSOLE:
                # In order to have transparency on console. Can be removed but console will not be transparent
                gui_manager.blit_background()
            case State.END_PROGRAM:
                end()
                break

        # If console is in use
        if console_manager.console: 
            # Read and process events related to the console
            console_manager.console.update(key_events)
            # Display the console if enabled or animation is still in progress
            console_manager.console.show(gui_manager.window)

        # Display FPS if SHOW_FPS is enabled in config
        not DISPLAY["SHOW_FPS"] or gui_manager.blit_text("FPS: " + str(int(gui_manager.clock.get_fps())))

        # Flip the frame buffers
        #pygame.display.flip()
        gui_manager.flip()

        # Display FPS in window title
        #pygame.display.set_caption('FPS: ' + str(int(gui_manager.clock.get_fps())))


        # Get the time of the frame
        dt = gui_manager.clock.tick(DISPLAY["MAX_FPS"])

def end() -> None:

    # Clear Game
    global engine
    if engine: engine.exit_game()
    engine = None
    logger.info(f'Game closed')

    # Clear Menus
    global exit_menu
    exit_menu.clear()
    exit_menu = None

    global load_scene_menu
    load_scene_menu.clear()
    load_scene_menu = None

    global main_menu
    main_menu.clear()
    main_menu = None

    logger.info(f'Menus closed')

    # Clear Managers
    gui_manager.clear()
    sound_manager.clear()
    state_manager.clear()

    logger.info(f'Managers closed')

'''
Functions that feed the console with header and footer data.
'''

# Get process object to determine info about python process (mem usage etc.)
import os, psutil
logger.info(f'pyRPG process running as PID={os.getpid()}.')
python_process = psutil.Process(os.getpid())


def cons_get_info_header():
    '''Returns info that is displayed in the console's header'''

    memory_use = python_process.memory_info()[0]/2.**30  # memory use in GB...I think
    game_state = state_manager.game_state #if main else 'N/A'
    no_of_entities =  len(engine.ecs_manager._world._entities) if engine else 'N/A'

    return f'memory usage: {memory_use} GB | game state: {str(game_state)} | ECS entities: {no_of_entities}'

def cons_get_info_footer():
    '''Returns info that is displayed in the console's footer'''

    loaded_quests = engine._scenes.keys() if engine else 'N/A'

    return f'loaded scenes: {loaded_quests}'