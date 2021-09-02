''' pyrpg/pyrpg/main.py

    Called from:
    -> pyrpg/pyrpg.py

    Aim:
    -> Implements the main game loop - switching between game and the menus

    Usage:
    -> Implements the main game loop - switching between game and the menus

    Notes:
    -> Contains `main.game_mode` variable that holds state of the game
    -> Contains `main.console` variable that holds reference to console

    Examples:
'''

# Initiate logging
import logging
import logging.config
logger = logging.getLogger(__name__)

# Initiates pygame window
# Initiates pygame clock
import pyrpg.core.engine

# Initiates console
import pyrpg.core.config.console


# Initiate keys used for the console toggle anywhere in the game
from pyrpg.core.config.keys import K_CONSOLE_TOGGLE

# It is needed to import pygame in order to have access to key events in the main game loop
import pygame

from pyrpg.core.config.config import DISPLAY, DEBUG, LOGGING

# Definition of game states
GAME_STATE = ['MAIN_MENU', 'GAME']

global _game_state
global _prev_game_state # Introduced to remember from which game status I come to Console
global console
global show_cons_on_sys_msg

def init(state='MAIN_MENU', cons_enabled=True):

    ##################
    # Init logging
    ##################

    logging.config.dictConfig(LOGGING)
    logger.info('Logging configured ...')

    ##################
    # Init the console
    ##################
    global console
    global show_cons_on_sys_msg # remember if system messages should force displaying of the console

    show_cons_on_sys_msg = cons_enabled

    from pyrpg.core.config.console import game_console as console
    # console = pyrpg.core.config.console.game_console

    # Enable console for startup messages
    console.toggle(enable=show_cons_on_sys_msg)

    # Send reference to console text display function to engine
    pyrpg.core.engine.init_console_fnc(update_console)


    ##################
    # Init the game
    ##################

    # Init world and put the messages to the console
    pyrpg.core.engine.init_world()

    #####################################
    # Start game in the given GAME STATE
    #####################################

    global _game_state
    _game_state = state

    # Load the definitions contained in the init quest - old processors
    #pyrpg.core.engine.new_game('init')
    #pyrpg.core.engine.new_game('test04_weapons')
    #pyrpg.core.engine.new_game('otik_lvl1')

    # Load the example test quest
    # TODO - in the future this will be triggered from the menu

    ##################
    ### Command Tests
    ##################
    #pyrpg.core.engine.new_game('tests/02_commands/new_test_commands_01')
    #pyrpg.core.engine.new_game('tests/02_commands/new_test_commands_02')


    ##################
    ### Movement Tests
    ##################
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_01')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_02')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_03') # Support for diagonal moves
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_04')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_05')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_06')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_07')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_08')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_09')
    #pyrpg.core.engine.new_game('tests/01_movements/new_test_movement_10')

    ##################
    ### Animation Tests
    ##################
    #pyrpg.core.engine.new_game('tests/03_animations/new_test_animations_01')

    ##################
    ### Collision Tests
    ##################
    #pyrpg.core.engine.new_game('tests/04_collisions/new_test_collisions_01')
    #pyrpg.core.engine.new_game('tests/04_collisions/new_test_collisions_02')
    #pyrpg.core.engine.new_game('tests/04_collisions/new_test_collisions_03')
    #pyrpg.core.engine.new_game('tests/04_collisions/map_collision_test_01')

    ##################
    ### Pickup Tests
    ##################
    #pyrpg.core.engine.new_game('tests/05_pickup/new_test_pickup_01')

    ##################
    ### Teleportation Tests
    ##################
    #pyrpg.core.engine.new_game('tests/06_teleportation/new_test_teleportation_01')
    #pyrpg.core.engine.new_game('tests/06_teleportation/new_test_teleportation_02')

    ##################
    ### Arm Weapon Tests
    ##################
    pyrpg.core.engine.new_game('tests/07_arm_weapon/new_test_arm_weapon_01')



    ##################
    # Hide the console
    ##################

    # Enable console for startup messages
    console.toggle(enable=False)

    # run the main loop
    run()

def run():

    global _game_state
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
                if event.key == K_CONSOLE_TOGGLE and console:
                    console.toggle()
                    console_enabled = not console_enabled
                    if console_enabled: 
                        pyrpg.core.engine.save_screen_copy() # Store the game screen
                        _prev_game_state = _game_state
                        _game_state = 'CONSOLE'
                    else:
                        _game_state = _prev_game_state
                        _prev_game_state = 'CONSOLE'


        if _game_state == 'GAME':
            _game_state = pyrpg.core.engine.run(key_events=key_events, key_pressed=key_pressed, dt=dt, debug=DEBUG)

        elif _game_state == 'PAUSE_GAME':
            _game_state = pyrpg.core.engine.pause_game(key_events=key_events, key_pressed=key_pressed, dt=dt)

        elif _game_state == 'MAIN_MENU':
            _game_state = main_menu(key_events=key_events, key_pressed=key_pressed, dt=dt)

        elif _game_state == 'CONSOLE':
            _game_state = pyrpg.core.engine.show_console(key_events=key_events, key_pressed=key_pressed, dt=dt)


        # Read and process events related to the console in case console is enabled
        console.update(key_events)

        # Display the console if enabled or animation is still in progress
        console.show(pyrpg.core.engine.window)

        # Flip the frame buffers
        #pygame.display.update()
        pygame.display.flip()

        # Display FPS in window title
        pygame.display.set_caption('FPS: ' + str(int(pyrpg.core.engine.clock.get_fps())))


def update_console(text):
    ''' Function is used to generate messages on the console
    during startup of the game. Reference to this function is
    passed as an argument in init functions and those functions
    are then adding messages to the console.

    In order to supress console animation, `disable_anim` parameter
    is used - it overrides default settings of the console.
    '''

    global console
    global show_cons_on_sys_msg # remember if system messages should force displaying of the console

    console.write(text)
    
    if show_cons_on_sys_msg:
        console.show(pyrpg.core.engine.window, disable_anim=True)
        pygame.display.flip()

def main_menu(key_events, key_pressed, dt):
    print('In MAIN MENU')
    return 'MAIN_MENU'

def end():
    pyrpg.core.engine.quit()