''' Main module 
'''

# Init clock and pygame
import core.engine

# Init console
import core.config.console 


# Initiate keys
import core.config.keys as keys

import pygame

from core.config.config import DISPLAY, DEBUG

# Definition of game states
GAME_MODES = ['MAIN_MENU', 'GAME']

global game_mode
global console

def main():

    ######################
    # Init Window
    ######################

    ######################
    # Init Console
    ######################
    global console
    console = core.config.console.game_console

    # Force displaying console for game init messages
    console.toggle(enable=True)

    ######################
    # Init Game
    ######################

    # Init the game
    core.engine.init_world(update_console) # passing console update function so that can write some info to the console

    ######################
    # Start game in the desired game mode
    ######################
    global game_mode
    game_mode = 'GAME'

    core.engine.new_game(update_console)

    # run the main loop
    run(update_console)

def run(cns_fnc):

    global game_mode
    global console

    console_enabled = False

    while True:

        # Get the time of the frame
        dt = core.engine.clock.tick(DISPLAY['max_fps'])

        # Read the keys pressed, mouse, win resize etc.
        key_events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()

        # Check for End Game
        for event in key_events:
            if event.type == pygame.QUIT:
                end()
                break
            elif event.type == pygame.KEYUP:
                if event.key == keys.K_CONSOLE_TOGGLE:
                    console.toggle()
                    console_enabled = not console_enabled


        if game_mode == 'GAME':
            game_mode = core.engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG)

        elif game_mode == 'PAUSE_GAME':
            game_mode = pause_game(key_events=key_events, key_pressed=key_pressed, dt=dt)

        elif game_mode == 'MAIN_MENU':
            game_mode = main_menu(key_events=key_events, key_pressed=key_pressed, dt=dt)

        # Read and process events related to the console in case console is enabled
        console.update(key_events)

        # Display the console if enabled or animation is still in progress
        console.show(core.engine.window)

        # Flip the frame buffers
        #pygame.display.update()
        pygame.display.flip()

        # Display FPS in window title
        pygame.display.set_caption('FPS: ' + str(int(core.engine.clock.get_fps())))


def update_console(text):
    ''' Function is used to generate messages on the console
    during startup of the game. Reference to this function is
    passed as an argument in init functions and those functions
    are then adding messages to the console.

    In order to supress console animation, `disable_anim` parameter
    is used - it overrides default settings of the console.
    '''

    global console

    console.write(text)
    console.show(pyrpg.core.engine.window, disable_anim=True)
    pygame.display.flip()

def pause_game(key_events, key_pressed, dt):

    # Here you can draw pause window
    core.engine.pause_game()

    for event in key_events:
        if event.type == pygame.QUIT:
            return 'QUIT_GAME'
        elif event.type == pygame.KEYDOWN:
            if event.key == keys.K_PAUSE_GAME:
                return 'GAME'

    return 'PAUSE_GAME'

def main_menu(key_events, key_pressed, dt):
    print('In MAIN MENU')
    return 'MAIN_MENU'

def end():
    core.engine.quit()

main()