# Init logging config
import logging
logger = logging.getLogger(__name__)


# It is needed to import pygame in order to have access to key events in the main game loop
import pygame

# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config.keys import KEYS # for K_CONSOLE_TOGGLE

from pyrpg.core.config.display import DISPLAY # for MAX_FPS

from pyrpg.core.config.states import State


class Main:

    def __init__(self, console: bool=True, filepath: str=None, timed: bool=False) -> None:

        self.timed = timed

        # Manager of GUI window and related
        from pyrpg.core.managers.gui_manager import GUIManager
        from pyrpg.core.config.display import DISPLAY 
        self.gui_manager = GUIManager(
            window=DISPLAY["WINDOW"],
            width=DISPLAY["WIDTH"], 
            height=DISPLAY["HEIGHT"], 
            depth=DISPLAY["BITDEPTH"], 
            full=DISPLAY["FULLSCREEN"], 
            ratio=DISPLAY["GUI_WINDOW_RATIO"]
        )

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
        #from pyrpg.core.menus.progress_bar import ProgressBar
        #self.progress_bar = ProgressBar(gui_manager=self.gui_manager)

        # Class representing the load scene menu
        from pyrpg.core.menus.load_scene_menu import LoadSceneMenu
        self.load_scene_menu = LoadSceneMenu(gui_manager=self.gui_manager, state_manager=self.state_manager, init_game_fnc=self.init_game)

        # Class representing the exit dialog
        from pyrpg.core.menus.exit_menu import ExitMenu
        self.exit_menu = ExitMenu(gui_manager=self.gui_manager, state_manager=self.state_manager)
        
        # Start game into main menu or into the game
        if filepath:

            # Init the game
            self.init_game(filepath)

            # Everything is loaded, game can start
            self.state_manager.change_state(State.GAME)

            logger.info(f'Starting into the game.')

        else:
            self.state_manager.change_state(State.MAIN_MENU)
            logger.info(f'Starting into the main menu.')

        # Reference to game to itself
        global main
        main = self

    def init_game(self, filepath):
        # Show loading screen here

        if self.engine is None:
            from pyrpg.core.engine import Game
            self.engine = Game(self.gui_manager, self.sound_manager, timed=self.timed)

        self.engine.new_game(filepath)


    def run(self):
        ''' Main game and menu loop. Contains references to other
        loop codes depending of current GameState
        '''

        # Fix of the problem with the first frame that has too
        # big dt and as a consequence the first movement with
        # the first frame is too big.
        # Calculate the first dt directly
        self.gui_manager.clock.tick(DISPLAY["MAX_FPS"])
        dt = 1000 / DISPLAY["MAX_FPS"] # ms

        while True:
            
            # Read the keys pressed, mouse, win resize etc.
            key_events = pygame.event.get()
            key_pressed = pygame.key.get_pressed()

            for event in key_events:

                # Check for closing the main program window
                if event.type == pygame.QUIT:
                    self.state_manager.change_state(State.EXIT_GAME_DIALOG)

                if event.type == pygame.KEYUP:
                    if event.key == KEYS["K_CONSOLE_TOGGLE"] and self.console:
                        if self.console.toggle():
                            self.gui_manager.save_screen()
                            logger.info(f'Entering console')
                            self.state_manager.change_state(State.CONSOLE)
                        else:
                            logger.info(f'Exiting console')
                            self.state_manager.revert_state()

            if self.state_manager.state == State.GAME:
                #res_state = self.game.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG)
                self.state_manager.change_state(self.engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

            elif self.state_manager.state == State.MAIN_MENU:
                #res_state = self.main_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt)
                self.state_manager.change_state(self.main_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

            elif self.state_manager.state == State.LOAD_QUEST_MENU:
                #res_state = self.load_scene_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt)
                self.state_manager.change_state(self.load_scene_menu.run(key_events=key_events, key_pressed=key_pressed, dt=dt))

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

            # Get the time of the frame
            dt = self.gui_manager.clock.tick(DISPLAY["MAX_FPS"])


    def end_program(self) -> None:

        # Clear Game
        if self.engine:
            self.engine.exit_game()
        logger.info(f'Game closed')

        # Clear Menus
        self.exit_menu.clear()
        self.load_scene_menu.clear()
        self.main_menu.clear()
        self.exit_menu, self.load_scene_menu, self.main_menu = None, None, None
        logger.info(f'Menus closed')

        # Clear Managers
        self.gui_manager.clear()
        self.sound_manager.clear()
        self.state_manager.clear()
        self.gui_manager, self.sound_manager, self.state_manager = None, None, None
        logger.info(f'Managers closed')
