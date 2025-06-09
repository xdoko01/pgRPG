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

_initialized = False
_inited = False
_engine = None

_exit_dialog = None

### DO NOT REMOVE - Mandatory registration function
#def initialize(register, module_name):
#    '''State registers itself at StateManager under specific name
#    that will be used to call the command. More then one name can 
#    be used for the same command if needed.
#    '''
#    register(fnc=process, alias=module_name)  # mandatory, register the process under the name of the module
#    register(fnc=init, alias=module_name+'_init')  # mandatory, register the init under module_init name

def init(engine) -> None:
    print(f'Init called in EXIT_GAME_DIALOG module. {engine=}')

    global _engine
    _engine = engine

    global _inited
    _inited = True

def run(*args, **kwargs) -> state_manager.State:
    print(f'RUn called in EXIT_GAME_DIALOG module.')

    return state_manager.State.EXIT_GAME_DIALOG


from pygame_gui import UI_WINDOW_CLOSE, UI_CONFIRMATION_DIALOG_CONFIRMED
from pyrpg.core.config import GUI
from pyrpg.core.config.states import State
from pygame_gui.windows import UIConfirmationDialog
from pygame import Rect


def _show() -> None:
    '''Each time the exit dialog must be created. When closed it is destroyed automatically. '''
    global _exit_dialog
    _exit_dialog = UIConfirmationDialog(
            #rect=Rect(self.gui_manager.gui_dlg_start, self.gui_manager.gui_dlg_dim),
            rect=Rect(GUI["DLG_START_PX"], GUI["DLG_DIM_PX"]),
            manager=gui_manager.window_manager,
            action_long_desc='Do you want to exit the game?',
            action_short_name='Exit')

    logger.info(f'Exit dialog created')

def _hide():
    '''Hiding is not needed as dialog is destroyed upon closing'''
    raise NotImplementedError

def run(key_events, key_pressed, dt) -> State:

    # If exit menu accessed from other game state, create new exit dialog
    #if self.state_manager.changed_game_state:
    if state_manager.changed:
        _show()

    for event in key_events:
        if event.type == UI_CONFIRMATION_DIALOG_CONFIRMED:
            logger.info(f'Exiting the game')
            return State.END_PROGRAM
        elif event.type == UI_WINDOW_CLOSE and state_manager.prev_game_state:
            logger.info(f'Closing the exit window')
            return state_manager.prev_game_state

        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()

    return State.EXIT_GAME_DIALOG

def _clear() -> None:
    pass