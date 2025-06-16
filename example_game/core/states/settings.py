''' Module implementing the behavior wher program is in SETTINGS state 

For tests call `python -m pyrpg.core.states.settings -v`

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
import pyrpg.core.config.states as state_manager # for switching between game states - game <> console <> menu etc.
from pyrpg.core.config.states import State

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

import pyrpg.core.main as main # for re-init after change of display configuration
from pygame_gui.elements import UIDropDownMenu
_resolution_dropdown: UIDropDownMenu = None

from pyrpg.core.config import DISPLAY

### DO NOT REMOVE - Mandatory init function
def init(*args, **kwargs) -> None:
    '''Pass the parameters necessary for flawless function to the module.
    '''
    print(f'{DISPLAY["SUPPORTED_RESOLUTIONS"]=}')

    global _resolution_dropdown
    _resolution_dropdown = UIDropDownMenu(
        #options_list=[str(res)[10:] for res in DISPLAY["SUPPORTED_RESOLUTIONS"]],
        #starting_option= str(DISPLAY["RESOLUTION"])[10:],

        options_list=[f"{res[0]}x{res[1]}" for res in DISPLAY["SUPPORTED_RESOLUTIONS"]],
        starting_option= f"{DISPLAY["RESOLUTION"][0]}x{DISPLAY["RESOLUTION"][1]}",
        relative_rect=pygame.Rect((200, 200), (250, 30)),
        manager=gui_manager.window_manager,
        container=None
        )
    
    _resolution_dropdown.hide()

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


import pygame
from pygame_gui import UI_DROP_DOWN_MENU_CHANGED
from pyrpg.core.config import gui as gui_manager

def _show() -> None:
    '''Show the buttons when first time in MAIN_MENU state.
    '''
    _resolution_dropdown.show()
    logger.info(f'Settings window showed')

def _hide() -> None:
    '''Hide the buttons when leaving to other state.
    '''
    _resolution_dropdown.hide()
    logger.info(f'Settings window hidden')

### DO NOT REMOVE - Mandatory execution function called every cycle when engine in the State
def run(key_events, key_pressed, dt) -> State:
    '''The main loop for the given state.
    '''

    #if self.state_manager.changed_game_state:
    if state_manager.changed: 
        _show()

    # Process the events
    for event in key_events:

        # On closing of the game window -> show the exit confirmation dialog
        if event.type == pygame.QUIT:
            return State.EXIT_GAME_DIALOG

        # On changing the dropdown menu -> change configuration
        elif event.type == UI_DROP_DOWN_MENU_CHANGED:


            sep = event.text.find('x')
            width = event.text[0:sep]
            height = event.text[sep+1:]

            print(f"Changed to {width=}, {height=}")

            # Call change of resolution
            DISPLAY["RESOLUTION"] = (int(width), int(height))

            # Reinit after change of configuration
            main.reinit()
            
            # Show again the Settings
            _show()
            
            return State.SETTINGS

        elif event.type == pygame.KEYDOWN:

            # On pressing the ESC button -> go back to main menu
            if event.key == pygame.K_ESCAPE:
                _hide()
                return State.MAIN_MENU


        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()

    return State.SETTINGS

