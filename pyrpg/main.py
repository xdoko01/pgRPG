''' Main module
'''

# Initiates pygame window and clock
# Initiate fonts
import pyrpg.core.engine

# Initiate keys
import pyrpg.core.config.keys as keys

# Initiate console
import pyrpg.core.config.console



import pygame

from pyrpg.core.config.config import DISPLAY, DEBUG

# Definition of game states
GAME_MODES = ['MAIN_MENU', 'GAME']

global game_mode
global console

console = pyrpg.core.config.console.game_console


def main():
    ''' Starts the game in the MAIN MENU

        game_mode = 'MAIN_MENU'
        run()
    '''

    global game_mode

    # Init the game
    pyrpg.core.engine.init_world()

    # Start game in the GAME MODE
    game_mode = 'GAME'
    pyrpg.core.engine.new_game()

    # run the main loop
    run()

def run():

    global game_mode
    global console

    console_enabled = False

    while True:

        # Get the time of the frame
        dt = pyrpg.core.engine.clock.tick(DISPLAY['max_fps'])

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
            game_mode = pyrpg.core.engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG)

        elif game_mode == 'PAUSE_GAME':
            game_mode = pause_game(key_events=key_events, key_pressed=key_pressed, dt=dt)

        elif game_mode == 'MAIN_MENU':
            game_mode = main_menu(key_events=key_events, key_pressed=key_pressed, dt=dt)

        # Read and process events related to the console in case console is enabled
        console.update(key_events)

        # Display the console if enabled or animation is still in progress
        console.show(pyrpg.core.engine.window)

        # Flip the frame buffers
        #pygame.display.update()
        pygame.display.flip()

        # Display FPS in window title
        pygame.display.set_caption('FPS: ' + str(int(pyrpg.core.engine.clock.get_fps())))


def pause_game(key_events, key_pressed, dt):

    # Here you can draw pause window
    pyrpg.core.engine.pause_game()

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
    pyrpg.core.engine.quit()

main()