''' Module implementing the behavior wher program is in MAIN_MENU state 

For tests call `python -m pgrpg.core.states.main_menu -v`

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

from pygame_gui.elements import UIButton

_settings_button: UIButton = None
_load_scene_button: UIButton = None
_exit_game_button: UIButton = None

### DO NOT REMOVE - Mandatory init function
def init(*args, **kwargs) -> None:
    '''Pass the parameters necessary for flawless function to the module.
    '''

    global _resume_button
    _resume_button = UIButton(relative_rect=pygame.Rect((150, 25), (100, 50)), text='Resume', manager=gui_manager.window_manager, container=None)

    global _settings_button
    _settings_button = UIButton(relative_rect=pygame.Rect((150, 100), (100, 50)), text='Settings', manager=gui_manager.window_manager, container=None)

    global _load_scene_button
    _load_scene_button = UIButton(relative_rect=pygame.Rect((150, 175), (100, 50)), text='Load Scene', manager=gui_manager.window_manager, container=None)
    
    global _exit_game_button
    _exit_game_button = UIButton(relative_rect=pygame.Rect((150, 275), (100, 50)), text='Exit', manager=gui_manager.window_manager, container=None)

    _resume_button.hide()
    _settings_button.hide()
    _load_scene_button.hide()
    _exit_game_button.hide()

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
from pygame_gui import UI_BUTTON_PRESSED
from pgrpg.core.config import gui as gui_manager

def _show() -> None:
    '''Show the buttons when first time in MAIN_MENU state.
    '''
    if state_manager.game_state is not None: _resume_button.show()
    _settings_button.show()
    _load_scene_button.show()
    _exit_game_button.show()
    logger.info(f'Main menu window showed')

def _hide() -> None:
    '''Hide the buttons when leaving to other state.
    '''
    _resume_button.hide()
    _settings_button.hide()
    _load_scene_button.hide()
    _exit_game_button.hide()
    logger.info(f'Main menu window hidden')

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

        elif event.type == pygame.KEYDOWN:

            # On pushing the ESC button -> show exit dialog
            if event.key == pygame.K_ESCAPE:
                return State.EXIT_GAME_DIALOG

        # On pressing a button -> move to new state
        elif event.type == UI_BUTTON_PRESSED:
            
            # On pressing the Resume button -> switch to GAME state
            if event.ui_element == _resume_button:
                logger.info(f'Resuming to Game')
                _hide()
                return State.GAME

            # On pressing the Settings button -> switch to SETTINGS state
            if event.ui_element == _settings_button:
                logger.info(f'Accessing Settings window')
                _hide()
                return State.SETTINGS

            # On pressing the Load button -> switch to LOAD_STATE state
            if event.ui_element == _load_scene_button:
                logger.info(f'Accessing load scene window')
                #_hide()
                return State.LOAD_SCENE_MENU

            # On pressing the Exit button -> switch to EXIT_GAME_DIALOG state
            if event.ui_element == _exit_game_button:
                logger.info(f'Accessing exit game window')
                #_hide()
                return State.EXIT_GAME_DIALOG

        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()

    return State.MAIN_MENU

