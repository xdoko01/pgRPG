# Init logging config
import logging
logger = logging.getLogger(__name__)

# Init the configuration
# Config variables were merged from default.jsonc and config.jsonc. Now we need to init
# all the necessary configurations, bring them to life (init display, console, logging, ...)
import pyrpg.core.config as config
import sys
config.init(main_module=sys.modules[__name__]) # return the reference to the main module to the config module in order to use it for console functions getting info about the game

# Load selected configuration objects to the main module so that it can be used
import pyrpg.core.config.gui as gui_manager # for manipulation with game screen
import pyrpg.core.config.sound as sound_manager # for menu sounds
import pyrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.

from pyrpg.core.config import cons # handler for manipulation with the game console

# Remember reference to engine module to be used by the console commands
engine = None

def _init_game(scene_file: str) -> None:

    # Create engine instance if not yet created
    global engine
    from pyrpg.core import engine as e
    engine = e
    engine.init() # Init can be removed as timed parameter is no longer passed
    engine.new_game(scene_file)

# Start the program
#def init(scene_file: str=None, timed: bool=False) -> None:
def init(scene_file: str=None) -> None:
    """ Start either into the game scene or in the main menu.
    """
    # Init game state - Start game into main menu or into the game
    if scene_file:
       # _init_game(scene_file, timed)
        _init_game(scene_file)
        state_manager.change_state(State.GAME) # TODO: shouldnt this be part of init game??
        logger.info(f"Starting into the game.")
    else:
        state_manager.change_state(State.MAIN_MENU)
        logger.info(f"Starting into the main menu.")



# Load the menus that can be accessed from the main program loop
from pyrpg.core.menus.main_menu import MainMenu
from pyrpg.core.menus.load_scene_menu import LoadSceneMenu
from pyrpg.core.menus.exit_menu import ExitMenu

main_menu = MainMenu(gui_manager=gui_manager, sound_manager=sound_manager, state_manager=state_manager)
load_scene_menu = LoadSceneMenu(gui_manager=gui_manager, sound_manager=sound_manager, state_manager=state_manager, init_game_fnc=_init_game)
exit_menu = ExitMenu(gui_manager=gui_manager, sound_manager=sound_manager, state_manager=state_manager)


import pygame
# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config import KEYS # for K_CONSOLE_TOGGLE
from pyrpg.core.config import DISPLAY # for MAX_FPS
from pyrpg.core.config.states import State

def run():
    """ Main game and menu loop. Contains references to other
    loop codes depending of current GameState.
    """

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
                if event.key == KEYS["K_CONSOLE_TOGGLE"]: 
                    if cons.toggle():
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

        # Notify console
        cons.update(key_events)
        cons.show(gui_manager.window)

        # Display FPS if SHOW_FPS is enabled in config
        not DISPLAY["SHOW_FPS"] or gui_manager.blit_text("FPS: " + str(int(gui_manager.clock.get_fps())))

        # Flip the frame buffers
        gui_manager.flip()

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
    state_manager.clear()

    logger.info(f'Managers closed')
