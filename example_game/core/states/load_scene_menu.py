''' Module implementing the behavior wher program is in START_PROGRAM state 

For tests call `python -m pyrpg.core.states.start_program -v`

State module represents one state only. The name of the module must be the same as the name of the
state in lower case.

State module must consists of following functions:

    - initialize() ... Function that registers the state with the StateManager.
    - init() ... Function that passes all the necessary parameters to the state module so
                it can operate.
'''

######## INIT PART

### DO NOT REMOVE - Support of command logging
import logging
logger = logging.getLogger(__name__)

import pyrpg.core.config.gui as gui_manager # for manipulation with game screen
import pyrpg.core.config.sound as sound_manager # for menu sounds
import pyrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.

from pyrpg.core.config import FILEPATHS #SCENE_PATH # for SCENE_PATH

_initialized = False
_inited = False
_engine = None

_last_scene_path = FILEPATHS["SCENE_PATH"]
_load_scene_window = None

### DO NOT REMOVE - Mandatory registration function
#def initialize(register, module_name):
#    '''State registers itself at StateManager under specific name
#    that will be used to call the command. More then one name can 
#    be used for the same command if needed.
#    '''
#    register(fnc=process, alias=module_name)  # mandatory, register the process under the name of the module
#    register(fnc=init, alias=module_name+'_init')  # mandatory, register the init under module_init name

def init(engine) -> None:
    print(f'Init called in START_PROGRAM module. {engine=}')

    global _engine
    _engine = engine

    global _inited
    _inited = True

    logger.info(f"Load Scenes Menu dialog initiated.")



#from pyrpg.core.config.paths import QUEST_PATH
from pyrpg.core.config import FILEPATHS #SCENE_PATH # for SCENE_PATH
from pyrpg.core.config import GUI
from pygame_gui import UI_FILE_DIALOG_PATH_PICKED, UI_WINDOW_CLOSE
from pyrpg.core.config.states import State
from pygame_gui.windows import UIFileDialog
from pygame import Rect


def _show() -> None:
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

def _hide():
    raise NotImplementedError

def run(key_events, key_pressed, dt) -> State:
        
    # If load scene menu accessed from other game state, create new dialog
    #if state_manager.changed_game_state:
    if state_manager.changed:
        _show()

    for event in key_events:
        if event.type == UI_FILE_DIALOG_PATH_PICKED:
            logger.info(f"Loading scene file '{event.text}''.")
            _engine.new_game(event.text)
            global _last_scene_path
            _last_scene_path = event.text
            return State.GAME
        elif event.type == UI_WINDOW_CLOSE and state_manager.prev_game_state:
            logger.info(f"Closing Load Scenes Menu Dialog.")
            return state_manager.prev_game_state

        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()
    

    return State.LOAD_SCENE_MENU

def _clear() -> None:
    pass