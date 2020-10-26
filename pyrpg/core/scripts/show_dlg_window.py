import pyrpg.core.engine as engine
from pyrpg.functions import wait # import wait function
import pyrpg.utils.dialog as dialog # import display_dialog function

import pygame
from pyrpg.core.config.keys import K_SUBMIT

def script_show_dlg_window(event, *args, **kwargs):
    ''' Script that displays dialog window and freezes the game.
    Dialog can have several frames that are switched by pressing
    the submit button.
    '''

    # Take a copy of the screen and store it in engine
    # Before taking the screen, everything is blittet (screen is updated)
    engine.save_screen_copy(True)

    # Load dialog object based on the dialog_id
    dlg_id = kwargs.get('dialog_id', None)
    dlg_obj = engine.dialogs.get(dlg_id, {})

    # Load the position of the dialog
    dlg_pos = kwargs.get('position', [0, 0])

    # Load the frames of the dialog that should be displayed in form of the list
    # If not indicated, all frames should be shown
    # If dialog has no frames, the list of frames is [None]
    dlg_frames = kwargs.get('frames', None)
    no_of_frames = dialog.get_no_of_frames(dlg_obj)
    dlg_frames = dlg_frames if dlg_frames else (list(range(no_of_frames)) if no_of_frames else [None])

    print(dlg_obj)

    # Iterate and display dialog with all required frames
    for frame_id in dlg_frames:

        # Paste window copy
        engine.window.blit(engine.screen_copy, (0, 0))

        # Show dialog
        dialog.display_dlg(engine.window, dlg_pos, dlg_obj, frame_id)

        # Update screen
        pygame.display.update()

        # Until key is pressed - switch to the next frame when pressed
        wait(K_SUBMIT, pygame.K_ESCAPE)

    # Return success
    return 0
