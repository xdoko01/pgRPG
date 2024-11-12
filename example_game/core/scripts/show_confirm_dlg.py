'''
Can be run from the console by putting following command

py game.main.game.script_manager._scripts['show_confirm_dlg'](None, html_text='Hello')

'''
import pygame
from pygame_gui.windows import UIConfirmationDialog
from pygame_gui import UI_WINDOW_CLOSE, UI_CONFIRMATION_DIALOG_CONFIRMED
from pygame import Rect
from pyrpg.core import main
from pyrpg.core.config import DISPLAY # for MAX_FPS
from pyrpg.core.config import GUI
from pyrpg.functions.str_utils import translate_str

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_show_confirm_dlg, alias=module_name)
    # Optional names for the script
    register(fnc=script_show_confirm_dlg, alias='show_confirm_dlg_window')

def script_show_confirm_dlg(event, *args, **kwargs):
    ''' Script that displays pygame_gui confirm dialog and freezes the game.
    '''

    long_desc = kwargs.get('long_desc', '')
    title = kwargs.get('title', 'Confirm')
    confirm_text = kwargs.get('confirm_text', 'OK')
    event_type = kwargs.get('event_type', None)
    event_params = kwargs.get('event_params', {})

    # Substitute words starting by % with values from event.params dict
    long_desc = translate_str(for_trans=long_desc, trans_dict=event.params, prefix='%')

    # Must be with parameter True because the flip is done at the end of main loop
    main.gui_manager.save_screen(flip_before_copy=True)

    # Prepare the window
    message_window = UIConfirmationDialog(
        #rect=Rect(main.gui_manager.gui_dlg_start, main.gui_manager.gui_dlg_dim),
        rect=Rect(GUI["DLG_START_PX"], GUI["DLG_DIM_PX"]), 
        action_long_desc=long_desc,
        window_title=title,
        action_short_name=confirm_text,
        manager=main.gui_manager.window_manager)

    is_running = True

    while is_running:
        dt = main.gui_manager.clock.tick(DISPLAY["MAX_FPS"])

        for event in pygame.event.get():

            if event.type == UI_WINDOW_CLOSE:
                is_running = False
            
            if event.type == UI_CONFIRMATION_DIALOG_CONFIRMED: # Clicked on ok
                is_running = False

                # Generate a new custom event if wanted
                if event_type:
                    new_event = main.engine.event_manager.create_event(type=event_type, params=event_params)
                    main.engine.event_manager.add_event(new_event)

            main.gui_manager.process_events(event)

        main.gui_manager.update(dt/1000)
        main.gui_manager.blit_background()
        main.gui_manager.draw_gui()
        pygame.display.update()

    # Return success
    return 0
