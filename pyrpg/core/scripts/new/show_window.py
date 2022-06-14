'''
Can be run from the console by putting following command

py game.main.game.script_manager._scripts['show_window'](None, html_text='Hello')

'''
import pygame
from pygame_gui.windows import UIMessageWindow
from pygame_gui import UI_WINDOW_CLOSE
from pygame import Rect
from pyrpg.main import main
from pyrpg.core.config.display import DISPLAY_MAX_FPS


def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_show_window, alias=module_name)
    # Optional names for the script
    register(fnc=script_show_window, alias='show_window')

def script_show_window(event, *args, **kwargs):
    ''' Script that displays pygame_gui dialog window and freezes the game.
    '''

    html_text = kwargs.get('html_text', '')

    # Must be with parameter True because the flip is done at the end of main loop
    main.gui_manager.save_screen(flip_before_copy=True)

    # Prepare the window
    message_window = UIMessageWindow(
        rect=Rect(main.gui_manager._gui_dlg_start, main.gui_manager._gui_dlg_dim), 
        html_message = html_text,
        manager=main.gui_manager.window_manager)

    is_running = True

    while is_running:
        dt = main.gui_manager.clock.tick(DISPLAY_MAX_FPS)

        for event in pygame.event.get():

            if event.type == UI_WINDOW_CLOSE:
                is_running = False

            main.gui_manager.process_events(event)

        main.gui_manager.update(dt/1000)
        main.gui_manager.blit_background()
        main.gui_manager.draw_gui()
        pygame.display.update()

    # Return success
    return 0
