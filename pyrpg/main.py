''' pyrpg/pyrpg/main.py

    Called from:
    -> pyrpg/pyrpg.py

    Aim:
    -> Implements the main game loop - switching between game, console and the menus

    Usage:
    -> Implements the main game loop - switching between game, console and the menus
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

# It is needed to import pygame in order to have access to key events in the main game loop
import pygame

# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config.keys import K_CONSOLE_TOGGLE

from pyrpg.core.config.config import DEBUG

from pyrpg.core.config.display import DISPLAY_MAX_FPS

from pyrpg.core.config.states import State

# Via this global variable, console can access all game properties
main = None

def init(console: bool=True, filepath: str=None, timed: bool=False) -> None:
    '''Create instance of main game class and remember it in 
    form of global variable so that console can use it'''

    global main

    main = Main(console=console, filepath=filepath, timed=timed)
    logger.info(f'Instance of Main class created as "{main}".')

    logger.info(f'Starting the main loop.')
    main.run()

def exit() -> None:
    '''Clears the references and exits'''
    global main

    main.end_program()
    main = None
    pygame.quit()

    logger.info(f'Program quits.')

class Main:

    def __init__(self, console: bool=True, filepath: str=None, timed: bool=False) -> None:

        self.timed = timed

        # Manager of GUI window and related
        from pyrpg.core.managers.gui_manager import GUIManager
        from pyrpg.core.config.display import DISPLAY_BITDEPTH, DISPLAY_FULLSCREEN, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_GUI_WINDOW_RATIO
        self.gui_manager = GUIManager(DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_BITDEPTH, DISPLAY_FULLSCREEN, DISPLAY_GUI_WINDOW_RATIO)

        # Prepare console
        import pyrpg.core.managers.console_manager as console_manager
        if console:
            console_manager.init()
        self.console = console_manager.console

        # Manager of game states
        from pyrpg.core.managers.state_manager import StateManager
        from pyrpg.core.config.states import STATES_GRAPH, NON_GAME_STATES, START_STATE
        self.state_manager = StateManager(states_graph=STATES_GRAPH, start=START_STATE, non_game_states=NON_GAME_STATES)

        # Sound Manager
        from pyrpg.core.managers.sound_manager import SoundManager
        self.sound_manager = SoundManager()

        # Class representing the game
        self.engine = None

        # Class representing the main menu
        from pyrpg.core.menus.main_menu import MainMenu
        self.main_menu = MainMenu(gui_manager=self.gui_manager, state_manager=self.state_manager)

        # Class representing progress bar
        from pyrpg.core.menus.progress_bar import ProgressBar
        self.progress_bar = ProgressBar(gui_manager=self.gui_manager)

        # Class representing the load quest menu
        from pyrpg.core.menus.load_quest_menu import LoadQuestMenu
        self.load_quest_menu = LoadQuestMenu(gui_manager=self.gui_manager, state_manager=self.state_manager, init_game_fnc=self.init_game)

        # Class representing the exit dialog
        from pyrpg.core.menus.exit_menu import ExitMenu
        self.exit_menu = ExitMenu(gui_manager=self.gui_manager, state_manager=self.state_manager)
        
        # Start game into main menu or into the game
        if filepath:

            # Init the game
            self.init_game(filepath)

            # Everything is loaded, game can start
            self.state_manager.change_state(State.GAME)

            logger.info(f'Starting game into the game.')

        else:
            self.state_manager.change_state(State.MAIN_MENU)
            logger.info(f'Starting game into the main menu.')

    def init_game(self, filepath):
        # Show loading screen here

        if self.engine is None:
            from pyrpg.core.engine import Game
            self.engine = Game(self.gui_manager, self.sound_manager, progress_bar=self.progress_bar, timed=self.timed)

        self.engine.new_game(filepath)


    def run(self):
        ''' Main game and menu loop. Contains references to other
        loop codes depending of current GameState
        '''

        while True:


            # Get the time of the frame
            dt = self.gui_manager.clock.tick(DISPLAY_MAX_FPS)
            
            # Read the keys pressed, mouse, win resize etc.
            key_events = pygame.event.get()
            key_pressed = pygame.key.get_pressed()

            for event in key_events:

                # Check for closing the main program window
                if event.type == pygame.QUIT:
                    self.state_manager.change_state(State.EXIT_GAME_DIALOG)

                if event.type == pygame.KEYUP:
                    if event.key == K_CONSOLE_TOGGLE and self.console:
                        if self.console.toggle():
                            self.gui_manager.save_screen()
                            logger.info(f'Entering console')
                            self.state_manager.change_state(State.CONSOLE)
                        else:
                            logger.info(f'Exiting console')
                            self.state_manager.revert_state()

            if self.state_manager.state == State.GAME:
                #res_state = self.game.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG)
                self.state_manager.change_state(self.engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG))

            elif self.state_manager.state == State.MAIN_MENU:
                #res_state = self.main_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt)
                self.state_manager.change_state(self.main_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

            elif self.state_manager.state == State.LOAD_QUEST_MENU:
                #res_state = self.load_quest_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt)
                self.state_manager.change_state(self.load_quest_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

            elif self.state_manager.state == State.EXIT_GAME_DIALOG:
                #res_state = self.exit_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt)
                self.state_manager.change_state(self.exit_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

            elif self.state_manager.state == State.CONSOLE:
                #In order to have transparency on console. Cna be removed but console will not be transparent
                self.gui_manager.blit_background()

            elif self.state_manager.state == State.END_PROGRAM:
                exit()
                break

            # Change the game state as a result of above calls if needed
            #self.state_manager.change_state(res_state)

            if self.console: 
                # Read and process events related to the console
                self.console.update(key_events)
                # Display the console if enabled or animation is still in progress
                self.console.show(self.gui_manager.window)

            # Flip the frame buffers
            #pygame.display.update()
            pygame.display.flip()

            # Display FPS in window title
            pygame.display.set_caption('FPS: ' + str(int(self.gui_manager.clock.get_fps())))


    def end_program(self) -> None:

        # Clear Game
        if self.engine:
            self.engine.exit_game()
        logger.info(f'Game closed')

        # Clear Menus
        self.exit_menu.clear()
        self.load_quest_menu.clear()
        self.main_menu.clear()
        self.exit_menu, self.load_quest_menu, self.main_menu = None, None, None
        logger.info(f'Menus closed')

        # Clear Managers
        self.gui_manager.clear()
        self.sound_manager.clear()
        self.state_manager.clear()
        self.gui_manager, self.sound_manager, self.state_manager = None, None, None
        logger.info(f'Managers closed')


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

    loaded_quests = main.engine.quest_manager._quests.keys() if main and main.engine else 'N/A'

    return f'loaded quests: {loaded_quests}'
