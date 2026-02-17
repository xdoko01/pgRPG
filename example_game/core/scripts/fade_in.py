import pygame

from pgrpg import main

def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_fade_in, alias=module_name)

def script_fade_in(event, *args, **kwargs):
    
    speed = kwargs.get("speed", 0.1)

    main.gui_manager.save_screen(flip_before_copy=True)
    
    background = main.gui_manager.screen_copy.copy()
    background.convert_alpha()
    background.set_alpha(0)
    alpha = 0 # The increment-variable.

    while True:

        alpha += speed
        if alpha >= 255: return

        background.set_alpha(alpha)
        main.gui_manager.window.blit(background, (0, 0))

        pygame.display.flip()