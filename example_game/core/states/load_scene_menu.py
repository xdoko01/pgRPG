''' Module implementing the behavior wher program is in LOAD_SCENE_MENU state 

For tests call `python -m pgrpg.core.states.load_scene_menu -v`

State module represents one state only. The name of the module must be the same as the name of the
state in lower case.

State module must consists of following functions:

    - initialize() ... Function that registers the state with the state manager.
    - init() ... Function that passes all the necessary parameters to the state module so it can operate.
'''

######## INIT PART

### DO NOT REMOVE
import logging
logger = logging.getLogger(__name__)

import sys
import pgrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.
from pgrpg.core.config.states import State

# Globals
_initialized: bool = False
_init: bool = False

### DO NOT REMOVE - Mandatory registration function
def initialize(state: State, register_fnc) -> None:
    '''State registers itself at state manager.
    Called from state_manager.
    
    Parameters:
        :param register_fnc: Function of state manager to register state module.
        :type register_fnc: func ref
    '''
    register_fnc(state=state, module=sys.modules[__name__])  # mandatory, register the module by state manager
    
    global _initialized
    _initialized = True # mark as initialized

### DO NOT REMOVE - Mandatory init function
def init(*args, **kwargs) -> None:
    '''Pass the parameters necessary for flawless function to the module.
    '''

    # Put any assignments here
    # ...

    global _init
    _init = True

    logger.info(f'State module {sys.modules[__name__]} init done.')

### DO NOT REMOVE - Mandatory clear function
def clear() -> None:
    '''Called when ending the program.
    '''
    # Put anything what needs to be derefferenced here
    # ...

    global _init
    _init = False

    logger.info(f'State module {sys.modules[__name__]} cleared.')

### PUT ALL YOUR OPTIONAL IMPORTS HERE
from pgrpg.core.config import FILEPATHS #SCENE_PATH # for SCENE_PATH
from pgrpg.core.config import GUI # for the dimensions of the window
from pgrpg.core.config import gui as gui_manager
from pgrpg.core import engine

from pygame import Rect
from pygame_gui import UI_FILE_DIALOG_PATH_PICKED, UI_WINDOW_CLOSE
from pygame_gui.windows import UIFileDialog

### GLOBALS
_last_scene_path = FILEPATHS["SCENE_PATH"]
_load_scene_window = None

def _show() -> None:
    '''Show the load dialog.'''
    global _load_scene_window
    _load_scene_window = UIFileDialog(
            #rect=Rect(self.gui_manager._gui_dlg_start, self.gui_manager._gui_dlg_dim),
            rect=Rect(GUI["DLG_START_PX"], GUI["DLG_DIM_PX"]),
            manager=gui_manager.window_manager,
            window_title="Load Scene",
            initial_file_path=_last_scene_path,
            allow_existing_files_only=False,
            allow_picking_directories=False
        )

    logger.info(f"Load Scenes Menu dialog created.")

### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt) -> State:
    '''The main loop for the given state.
    '''

    # If load scene menu accessed from other game state, create new dialog
    if state_manager.changed: _show()

    # Process the events
    for event in key_events:

        # On selecting a scene -> run a scene
        if event.type == UI_FILE_DIALOG_PATH_PICKED:
            logger.info(f"Loading scene file '{event.text}''.")
            engine.load_scene(event.text)
            global _last_scene_path
            _last_scene_path = event.text
            return State.GAME

        # On closing the window -> revert to the previous state
        elif event.type == UI_WINDOW_CLOSE and state_manager.prev_state:
            logger.info(f"Closing Load Scenes Menu Dialog.")
            state_manager.revert_state()
            return state_manager.state

        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()

    return State.LOAD_SCENE_MENU

