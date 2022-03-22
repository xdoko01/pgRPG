''' pyrpg/pyrpg/main_5ex.py

Prerequisites
  - console enabled as config parameter not from the command line


'''

# Init logging config
import logging
import logging.config
from pyrpg.core.config.config import LOGGING
logging.config.dictConfig(LOGGING)

# Initiate logging of module
logger = logging.getLogger(__name__)

# Get process object to determine info about python process (mem usage etc.)
import os, psutil
logger.info(f'pyRPG process running as PID={os.getpid()}.')
python_process = psutil.Process(os.getpid())

# LOADS DURING IMPORT Manager of GUI window and related
from pyrpg.core.managers.gui_manager import GUIManager
from pyrpg.core.config.display import DISPLAY_BITDEPTH, DISPLAY_FULLSCREEN, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_GUI_WINDOW_RATIO
gui_manager = GUIManager(DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_BITDEPTH, DISPLAY_FULLSCREEN, DISPLAY_GUI_WINDOW_RATIO)

# LOADS DURING IMPORT - Manager of game states
from pyrpg.core.managers.state_manager import StateManager
from pyrpg.core.config.states import STATES_GRAPH, NON_GAME_STATES, START_STATE
state_manager = StateManager(states_graph=STATES_GRAPH, start=START_STATE, non_game_states=NON_GAME_STATES)

# LOADS DURING IMPORT - Sound Manager
from pyrpg.core.managers.sound_manager import SoundManager
sound_manager = SoundManager()

# LOADS DURING IMPORT - Class representing the main menu
from pyrpg.core.menus.main_menu import MainMenu
main_menu = MainMenu(gui_manager=gui_manager, state_manager=state_manager)

#  LOADS DURING IMPORT - Class representing the load quest menu
from pyrpg.core.menus.load_quest_menu import LoadQuestMenu
load_quest_menu = LoadQuestMenu(gui_manager=gui_manager, state_manager=state_manager, init_game_fnc=init_game)

#  LOADS DURING IMPORT - Class representing the exit dialog
from pyrpg.core.menus.exit_menu import ExitMenu
exit_menu = ExitMenu(gui_manager=gui_manager, state_manager=state_manager)

# LOADS DURING IMPORT - Load console or not based on config in the config file
import pyrpg.core.managers.console_manager as console_manager
from pyrpg.core.config import ENABLE_CONSOLE
if ENABLE_CONSOLE: console_manager.init()
console = console_manager.console

# LOADS DURING IMPORT - engine
import pyrpg.core.engine_5ex as engine

from pyrpg.core.config.states import State


def init(filepath: str=None, timed: bool=False) -> None:
    '''Create instance of main game class and remember it in 
    form of global variable so that console can use it'''


    # Start game into main menu or into the game
    if filepath:
        state_manager.change_state(State.GAME)
        init_game(filepath, timed=timed)
        logger.info(f'Starting game into the game.')

    else:
        state_manager.change_state(State.MAIN_MENU)
        logger.info(f'Starting game into the main menu.')

    run()

def init_game(filepath: str, timed: bool = False):

    engine.initialize(timed=timed)

    from pathlib import Path
    engine.new_game(Path(filepath))


# It is needed to import pygame in order to have access to key events in the main game loop
import pygame
# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config.keys import K_CONSOLE_TOGGLE
from pyrpg.core.config.config import DEBUG
from pyrpg.core.config.display import DISPLAY_MAX_FPS

def run() -> None:
    ''' Main game and menu loop. Contains references to other
    loop codes depending of current GameState
    '''

    while True:

        # Get the time of the frame
        dt = gui_manager.clock.tick(DISPLAY_MAX_FPS)
        
        # Read the keys pressed, mouse, win resize etc.
        key_events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()

        for event in key_events:

            # Check for closing the main program window
            if event.type == pygame.QUIT:
                state_manager.change_state(State.EXIT_GAME_DIALOG)

            if event.type == pygame.KEYUP:
                if event.key == K_CONSOLE_TOGGLE and console:
                    if console.toggle():
                        gui_manager.save_screen()
                        logger.info(f'Entering console')
                        state_manager.change_state(State.CONSOLE)
                    else:
                        logger.info(f'Exiting console')
                        state_manager.revert_state()

        if state_manager.state == State.GAME:
            state_manager.change_state(engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG))

        elif state_manager.state == State.MAIN_MENU:
            state_manager.change_state(main_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

        elif state_manager.state == State.LOAD_QUEST_MENU:
            state_manager.change_state(load_quest_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

        elif state_manager.state == State.EXIT_GAME_DIALOG:
            state_manager.change_state(exit_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

        elif state_manager.state == State.CONSOLE:
            #In order to have transparency on console. Cna be removed but console will not be transparent
            gui_manager.blit_background()

        elif state_manager.state == State.END_PROGRAM:
            exit()
            break

        # Change the game state as a result of above calls if needed
        #self.state_manager.change_state(res_state)

        if console: 
            # Read and process events related to the console
            console.update(key_events)
            # Display the console if enabled or animation is still in progress
            console.show(gui_manager.window)

        # Flip the frame buffers
        #pygame.display.update()
        pygame.display.flip()

        # Display FPS in window title
        pygame.display.set_caption('FPS: ' + str(int(gui_manager.clock.get_fps())))



def exit() -> None:
    '''Clears the references and exits'''
    engine.exit_game()
    logger.info(f'Game closed')

    # Clear Menus
    exit_menu.clear()
    load_quest_menu.clear()
    main_menu.clear()
    exit_menu, load_quest_menu, main_menu = None, None, None
    logger.info(f'Menus closed')

    # Clear Managers
    gui_manager.clear()
    sound_manager.clear()
    state_manager.clear()
    gui_manager, sound_manager, state_manager = None, None, None
    logger.info(f'Managers closed')

    pygame.quit()

    logger.info(f'Program quits.')


'''
Functions that feed the console with header and footer data.
'''

def cons_get_info_header():
    '''Returns info that is displayed in the console's header'''

    memory_use = python_process.memory_info()[0]/2.**30  # memory use in GB...I think
    game_state = state_manager.game_state
    no_of_entities =  len(engine.ecs_manager._world._entities) if engine.ecs_manager._world else 'N/A'

    return f'memory usage: {memory_use} GB | game state: {str(game_state)} | ECS entities: {no_of_entities}'

def cons_get_info_footer():
    '''Returns info that is displayed in the console's footer'''

    loaded_quests = engine.quest_manager._quests.keys()

    return f'loaded quests: {loaded_quests}'
