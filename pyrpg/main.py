''' pyrpg/pyrpg/main.py

    Called from:
    -> pyrpg/pyrpg.py

    Aim:
    -> Implements the main game loop - switching between game, console and the menus

    Usage:
    -> Implements the main game loop - switching between game, console and the menus

    Notes:
    -> Contains `GameState` static class that holds state of the game
    -> Contains `GameConsole` static class that holds reference to console
'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

# Initiates pygame, game window, clock and further
import pyrpg.core.engine

# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config.keys import K_CONSOLE_TOGGLE

# It is needed to import pygame in order to have access to key events in the main game loop
import pygame

# It is needed to have gui elements available in the game menu
import pygame_gui

from pyrpg.core.config.display import DISPLAY_RESOLUTION, DISPLAY_WIDTH, DISPLAY_MAX_FPS
from pyrpg.core.config.config import DEBUG

from pyrpg.core.config.paths import QUEST_PATH

from pathlib import Path # for passing the game filepath after selection via gui

class GameState():
    '''Persists the game state and manages the transitions'''

    AVAILABLE_STATES = ['MAIN_MENU', 'GAME', 'PAUSE_GAME', 'END_PROGRAM', 'CONSOLE']

    state, prev_state = None, None
    changed = False # If the change happened in current loop, set to True else false

    @classmethod
    def change_state(cls, new_state):
        '''Changes the game state and saves the previous state.'''

        if new_state == cls.state: 
            cls.changed = False
            return

        if new_state in cls.AVAILABLE_STATES:
            cls.changed = True
            cls.prev_state, cls.state = cls.state, new_state
            logger.info(f'Game state changed from "{cls.prev_state}" to "{cls.state}".')
        else:
            logger.error(f'Cannot change from "{cls.state}" to unsupported game state "{new_state}".')
            raise ValueError(f'Cannot change to unsupported game state "{new_state}".')

    @classmethod
    def revert_state(cls):
        '''Return to the previous game state.'''
        cls.change_state(cls.prev_state)

class GameConsole():
    '''Manipulates the game console.'''

    console = None
    show_on_sys_msg = None

    @classmethod
    def init(cls, show_on_sys_msg=True):

        # Save if console should pop during loading of the game
        cls.show_on_sys_msg = show_on_sys_msg

        # Run the configuration fixing the paths for console configuration
        from pyrpg.core.config.console import CONSOLE_CONFIG, CONSOLE_CLI_MODULE

        # Imports support for LUA commands
        from pyrpg.core.config.lua import LUA_RUNTIME

        # Get the console class
        from pyrpg.utils import Console

        # Load the console from utils
        cls.console = Console(
            CONSOLE_CLI_MODULE,
            LUA_RUNTIME,
            DISPLAY_WIDTH,
            CONSOLE_CONFIG
        )

        # Send reference to console text display function to engine
        pyrpg.core.engine.init_console_fnc(cls.update_console)

    @classmethod
    def update_console(cls, text):
        ''' Function is used to generate messages on the console
        during startup of the game. Reference to this function is
        passed as an argument in init functions and those functions
        are then adding messages to the console.

        In order to supress console animation, `disable_anim` parameter
        is used - it overrides default settings of the console.
        '''

        cls.console.write(text)

        if cls.show_on_sys_msg:
            cls.console.show(pyrpg.core.engine.window, disable_anim=True)
            pygame.display.flip()

    @classmethod
    def write(cls, text):
        ''' Mandatory function used (not only) by the logger handler to write 
        directly onto the game console.
        '''
        if cls.console: cls.console.write(text)

class GameGUI():
    '''Contains GUI components for the menus'''

    game_window = None
    background = None
    gui_manager = None

    @classmethod
    def init(cls, game_window):
        cls.game_window = game_window
        cls.background = pygame.Surface(cls.game_window.get_size())
        cls.gui_manager = pygame_gui.UIManager(cls.game_window.get_size())

    @classmethod
    def show_file_select(cls, init_path):
        select_file_window = pygame_gui.windows.UIFileDialog(
            rect=pygame.Rect((10,10), (500,500)), 
            manager=cls.gui_manager, 
            window_title='File Dialog', 
            initial_file_path=init_path, 
            allow_existing_files_only=False,
            allow_picking_directories=False)

    @classmethod
    def process_events(cls, event):
        cls.gui_manager.process_events(event)

    @classmethod
    def update(cls, time):
        cls.gui_manager.update(time) # in seconds

    @classmethod
    def draw_gui(cls):
        cls.gui_manager.draw_ui(cls.game_window)

def _init_game(filepath, timed=True):

    # Enable console for startup messages
    GameConsole.console.toggle(enable=GameConsole.show_on_sys_msg)

    # Init world and put the messages to the console
    pyrpg.core.engine.init_world(timed)

    pyrpg.core.engine.new_game(Path(filepath))

    # Hide the console
    GameConsole.console.toggle(enable=False)

def init(console=True, filepath=None):
    '''Inits console, logging and starts the main game loop.

    Parameters:
        :param console: Should in-game console be available. Default True.
        :type console: bool

        :param filepath: Relative path to game definition file. Default None.
        :type filepath: str
    '''

    # Console init
    if console: 
        GameConsole.init()
        logger.info('Console enabled')

    # Init logging config
    import logging.config
    from pyrpg.core.config.config import LOGGING
    logging.config.dictConfig(LOGGING)

    # If game file is specified, run the file immediatelly
    if filepath:
        GameState.change_state('GAME')
        _init_game(filepath)
        logger.info(f'Starting game from file "{filepath}".')
    else:
        GameState.change_state('MAIN_MENU')
        GameGUI.init(pyrpg.core.engine.window)
        logger.info(f'Starting game into the main menu.')
    
    # Start the main loop
    run()

def run():
    ''' Main game and menu loop. Contains references to other
    loop codes depending of current GameState
    '''

    console_toggle = False

    while True:

        # Get the time of the frame
        dt = pyrpg.core.engine.clock.tick(DISPLAY_MAX_FPS)

        # Read the keys pressed, mouse, win resize etc.
        key_events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()

        for event in key_events:

            # Check for closing the main program window
            if event.type == pygame.QUIT:
                GameState.change_state('END_PROGRAM')

            if event.type == pygame.KEYUP:
                if event.key == K_CONSOLE_TOGGLE and GameConsole.console:
                    GameConsole.console.toggle()
                    console_toggle = not console_toggle
                    if console_toggle: 
                        pyrpg.core.engine.save_screen_copy() # Store the game screen
                        GameState.change_state('CONSOLE')
                    else:
                        GameState.revert_state()

        if GameState.state == 'GAME':
            res_state = pyrpg.core.engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG)

        if GameState.state == 'PAUSE_GAME':
            res_state = pyrpg.core.engine.pause_game(key_events=key_events, key_pressed=key_pressed, dt=dt)

        if GameState.state == 'MAIN_MENU':
            res_state = main_menu(key_events=key_events, key_pressed=key_pressed, dt=dt)

        if GameState.state == 'CONSOLE':
            res_state = pyrpg.core.engine.show_console(key_events=key_events, key_pressed=key_pressed, dt=dt)

        if GameState.state == 'END_PROGRAM':
            res_state = end_program()

        # Change the game state as a result of above calls if needed
        GameState.change_state(res_state)

        # Read and process events related to the console in case console is enabled
        GameConsole.console.update(key_events)

        # Display the console if enabled or animation is still in progress
        GameConsole.console.show(pyrpg.core.engine.window)

        # Flip the frame buffers
        #pygame.display.update()
        pygame.display.flip()

        # Display FPS in window title
        pygame.display.set_caption('FPS: ' + str(int(pyrpg.core.engine.clock.get_fps())))

def main_menu(key_events, key_pressed, dt):

    # If first time coming from the game to the loop, generate the gui window again
    if GameState.changed and GameState.prev_state != 'CONSOLE':
        GameGUI.background = pyrpg.core.engine.screen_copy
        GameGUI.show_file_select(QUEST_PATH)

    for event in key_events:
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            logger.info(f'Loading game file "{event.text}".')
            _init_game(event.text)
            return 'GAME'
        elif event.type == pygame_gui.UI_WINDOW_CLOSE and GameState.prev_state: # if MAIN_MENU is accessed from other existing state other than None
            logger.info(f'Closing MAIN_MENU window')
            return GameState.prev_state

        GameGUI.process_events(event)

    GameGUI.update(dt/1000)
    pyrpg.core.engine.window.blit(GameGUI.background, (0, 0))
    GameGUI.draw_gui()

    return 'MAIN_MENU'

def end_program():
    pyrpg.core.engine.quit()