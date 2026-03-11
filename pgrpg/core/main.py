"""Entry point for the pgrpg game loop.

Provides ``init()`` to bootstrap the engine, state modules, and an optional
starting scene or state, and ``run()`` for the main pygame event loop.
"""

import logging
logger = logging.getLogger(__name__)

# Init the configuration — merge default.jsonc + game config.jsonc and bring
# all subsystems (display, console, logging, …) to life.
import pgrpg.core.config as config
import sys
from pprint import pprint, pformat # for pretty printing in the console

config.init(main_module=sys.modules[__name__]) # return the reference to the main module to the config module in order to use it for console functions getting info about the game

# Load selected configuration objects to the main module so that it can be used
import pgrpg.core.config.gui as gui_manager # for manipulation with game screen
import pgrpg.core.config.sound as sound_manager # for menu sounds
import pgrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.
from pgrpg.core.config.states import State

import pygame
from pgrpg.core.config import DISPLAY # for MAX_FPS

from pgrpg.core.config import cons # handler for manipulation with the game console

# Remember reference to engine module to be used by the console commands
engine = None

def _init_engine() -> None:
    """Import and initialize the engine module (idempotent)."""
    from pgrpg.core import engine as e

    global engine
    engine = e

    if engine.get_init(): logger.warning(f'Engine already initiated.')
    engine.init() # Init can be removed as timed parameter is no longer passed

def _init_game(scene_file: str) -> None:
    """Initialize the engine and load the given scene file."""
    _init_engine()
    engine.load_scene(scene_file, show_progress=True)

def _init_state_modules() -> None:
    """Pass information about the managers to the state modules that
    are representing different menus in the game - main menu, configuration, end dialog, etc.
    """
    for state, state_module in state_manager.state_modules.items():
        state_module.init()
        logger.info(f"State module '{state_module}' initiated.")

def init(scene_file: str=None, state: str=None) -> None:
    """Bootstrap the engine and enter the initial game state.

    Args:
        scene_file: Optional scene file path to load immediately.
        state: Optional state name (e.g. ``'MAIN_MENU'``) to start in.
            If neither is given, starts into the dev console.
    """
    _init_engine()
    _init_state_modules()

    # Init game state - Start game into main menu or into the game
    if scene_file:
        _init_game(scene_file)
        state_manager.change_state(State.GAME)
        logger.info(f"Starting into the scene.")
    elif state:
        # If you want to enter MAIN_MENU then run with State.MAIN_MENU
        state_manager.change_state(State[state])
        logger.info(f"Starting into the '{state}' state.")
    else:
        # By default start into console with defaut.scr script executed
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
    """Run the main game loop until the process exits.

    Each iteration reads pygame events, delegates to the active state
    module, updates the console overlay, displays FPS if enabled, and
    flips the display buffer.
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
                key_pressed=key_pressed,  # Pressed Keys
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
