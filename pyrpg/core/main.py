# Init logging config
import logging
logger = logging.getLogger(__name__)

# Init engine
engine = None

def _init_game(scene_file: str, timed: bool) -> None:
    # Create engine instance if not yet created
    global engine

    if engine is None:
        from pyrpg.core.engine import Game
        engine = Game(gui_manager, sound_manager, timed=timed)

    engine.new_game(scene_file)


# Manager of GUI window and related
from pyrpg.core.managers.gui_manager import GUIManager
from pyrpg.core.config.display import DISPLAY 
gui_manager = GUIManager(
    window=DISPLAY["WINDOW"],
    width=DISPLAY["WIDTH"], 
    height=DISPLAY["HEIGHT"], 
    depth=DISPLAY["BITDEPTH"], 
    full=DISPLAY["FULLSCREEN"], 
    ratio=DISPLAY["GUI_WINDOW_RATIO"]
)

# Prepare console
import pyrpg.core.managers.console_manager as console_manager
console=None 

def _init_console() -> None:
    console_manager.init()
    global console
    console = console_manager.console


# Prepare game states
from pyrpg.core.managers.state_manager import StateManager
from pyrpg.core.config.states import STATES_GRAPH, NON_GAME_STATES, START_STATE
state_manager = StateManager(states_graph=STATES_GRAPH, start=START_STATE, non_game_states=NON_GAME_STATES)

# Sound Manager
from pyrpg.core.managers.sound_manager import SoundManager
sound_manager = SoundManager()

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
    if console: 
        _init_console()
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
                if event.key == KEYS["K_CONSOLE_TOGGLE"] and console:
                    if console.toggle():
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
        if console: 
            # Read and process events related to the console
            console.update(key_events)
            # Display the console if enabled or animation is still in progress
            console.show(gui_manager.window)

        # Flip the frame buffers
        #pygame.display.flip()
        gui_manager.flip()

        # Display FPS in window title
        pygame.display.set_caption('FPS: ' + str(int(gui_manager.clock.get_fps())))

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
    global gui_manager
    gui_manager.clear()
    gui_manger = None

    global sound_manager
    sound_manager.clear()
    sound_manager = None

    global state_manager
    state_manager.clear()
    state_manager = None

    logger.info(f'Managers closed')