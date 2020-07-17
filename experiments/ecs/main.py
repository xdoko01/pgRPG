''' Experiments with ECS
'''

import core.engine
import pygame

# Definition of game states
GAME_MODES = ['MAIN_MENU', 'GAME']

global game_mode

def main():
    ''' Starts the game in the MAIN MENU

        game_mode = 'MAIN_MENU'
        run()
    '''

    global game_mode

    # Init the game
    core.engine.init_world()

    # Start game in the GAME MODE
    game_mode = 'GAME'
    core.engine.new_game()

    # run the main loop
    run()

def run():

    while True:

        global game_mode

        # Read the keys pressed, mouse, win resize etc.
        key_events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()

        # Check for End Game
        for event in key_events:
            if event.type == pygame.QUIT:
                end()
                break

        if game_mode == 'MAIN_MENU':
            game_mode = main_menu(key_events=key_events, key_pressed=key_pressed)

        elif game_mode == 'GAME':
            game_mode = core.engine.run(key_events=key_events, key_pressed=key_pressed)


def main_menu(key_events, key_pressed):
    print('In MAIN MENU')
    return 'MAIN_MENU'

def end():
    core.engine.quit()

main()