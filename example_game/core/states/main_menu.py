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

from pygame_gui.elements import UIButton

_load_scene_button: UIButton = None
_exit_game_button: UIButton = None

from pygame_gui import UI_BUTTON_PRESSED
import pygame

### DO NOT REMOVE - Mandatory registration function
#def initialize(register, module_name):
#    '''State registers itself at StateManager under specific name
#    that will be used to call the command. More then one name can 
#    be used for the same command if needed.
#    '''
#    register(fnc=process, alias=module_name)  # mandatory, register the process under the name of the module
#    register(fnc=init, alias=module_name+'_init')  # mandatory, register the init under module_init name

def init(engine) -> None:
    print(f'Init called in MAIN_MENU module. {engine=}')

    global _engine
    _engine = engine

    global _inited
    _inited = True

    global _load_scene_button
    _load_scene_button = UIButton(relative_rect=pygame.Rect((150, 175), (100, 50)), text='Load Scene', manager=gui_manager.window_manager, container=None)
    
    global _exit_game_button
    _exit_game_button = UIButton(relative_rect=pygame.Rect((150, 275), (100, 50)), text='Exit', manager=gui_manager.window_manager, container=None)
    
    _load_scene_button.hide()
    _exit_game_button.hide()

    logger.info(f'Main menu window initiated')


def _show() -> None:
    _load_scene_button.show()
    _exit_game_button.show()
    logger.info(f'Main menu window showed')

def _hide() -> None:
    _load_scene_button.hide()
    _exit_game_button.hide()
    logger.info(f'Main menu window hidden')

def _clear() -> None:
    pass

def run(key_events, key_pressed, dt) -> state_manager.State:

    #if self.state_manager.changed_game_state:
    if state_manager.changed:
        _show()

    for event in key_events:

        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == _load_scene_button:
                logger.info(f'Accessing load scene window')
                _hide()
                return state_manager.State.LOAD_SCENE_MENU
            if event.ui_element == _exit_game_button:
                logger.info(f'Accessing exit game window')
                return state_manager.State.EXIT_GAME_DIALOG

        gui_manager.process_events(event)

    gui_manager.update(dt/1000)

    gui_manager.blit_background_animation()

    gui_manager.draw_gui()

    return state_manager.State.MAIN_MENU

