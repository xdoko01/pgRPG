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
from pyrpg.core.config.states import State

import pygame
from pyrpg.core.config import DISPLAY # for MAX_FPS

from pyrpg.core.config import cons # handler for manipulation with the game console

# Remember reference to engine module to be used by the console commands
engine = None

def _init_engine() -> None:
    # Create engine instance if not yet created
    from pyrpg.core import engine as e

    global engine
    engine = e

    if engine.get_init(): logger.warning(f'Engine already initiated.')
    engine.init() # Init can be removed as timed parameter is no longer passed

def _init_game(scene_file: str) -> None:
    # Create engine instance if not yet created
    #global engine
    #from pyrpg.core import engine as e
    #engine = e
    #engine.init() # Init can be removed as timed parameter is no longer passed
    global engine
    _init_engine()
    engine.load_scene(scene_file)

def _init_state_modules() -> None:
    """Pass information about the managers to the state modules that
    are representing different menus in the game - main menu, configuration, end dialog, etc.
    """
    for state, state_module in state_manager.state_modules.items():
        state_module.init()
        logger.info(f"State module '{state_module}' initiated.")

# Start the program
def init(scene_file: str=None) -> None:
    """ Start either into the game scene or in the main menu.
    """
    _init_engine()
    _init_state_modules()

    # Init game state - Start game into main menu or into the game
    if scene_file:
        _init_game(scene_file)
        state_manager.change_state(State.GAME)
        logger.info(f"Starting into the game.")
    else:
        # to allow load driven by the console script

        # Show and Switch to the console
        state_manager.change_state(State.CONSOLE)

        # Start the default script - and show the results
        cons.cli.do_script("default.scr")
        cons.console_output.prepare_surface() # Show the output buffer - as normally it is not shown
 
def reinit() -> None:
    """Reinit everything needed upon change of display configuration."""
    
    # Init what is needed
    config.init(
            log_init=False,
            font_init=False,
            frame_init=False,
            sound_init=False,
            state_init=False 
            )
    logger.info(f'Config reinit done')

    # Reinit all processors by calling their reinit function
    engine.ecs_manager.reinit_processors()

    # Reinit all components by calling their reinit funftion
    engine.ecs_manager.reinit_components()

    # Call init also on the State modules - should pe part of the state_init
    _init_state_modules()
    
    logger.info(f'Reinit done')

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

        # Run the appropriate State module loop based on the current state
        state_manager.change_state(
            state_manager.state_modules[state_manager.state].run(
                key_events=key_events, # Keyboard, mouse and other events
                key_pressed=pygame.key.get_pressed(),  # Pressed Keys
                dt=dt
            )
        )

        # Notify console - regardless of the State - to support animation of the console during the toggle
        cons.update(key_events)
        cons.show(gui_manager.window)

        # Display FPS if SHOW_FPS is enabled in config
        not DISPLAY["SHOW_FPS"] or gui_manager.blit_text("FPS: " + str(int(gui_manager.clock.get_fps())))

        # Flip the frame buffers
        gui_manager.flip()

        # Get the time of the frame
        dt = gui_manager.clock.tick(DISPLAY["MAX_FPS"])
