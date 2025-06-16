''' Script for change of the resolution

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "change_res"           ... get usage instructions
        "change_res -h"        ... get usage instructions
        "change_res --help"    ... get usage instructions
        "change_res 640 480"   ... change the resolution to 640x480
        "change_res 640 480 1" ... change the resolution to 640x480 + fullscreen
        "change_res 800 600 0" ... change the resolution to 800x600 + windowed
'''

instructions = """
Examples of usage:
    "change_res"           ... get usage instructions
    "change_res -h"        ... get usage instructions
    "change_res --help"    ... get usage instructions
    "change_res 640 480"   ... change the resolution to 640x480
    "change_res 640 480 1" ... change the resolution to 640x480 + fullscreen
    "change_res 800 600 0" ... change the resolution to 800x600 + windowed
"""
# Support of command logging
import logging
logger = logging.getLogger(__name__)

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_change_res, alias=module_name)

def cons_cmd_change_res(game_ctx, params):
    ''' Script that changes game resolution
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params < 2:
        print(instructions)

    # Try to set new resolution
    else:

        try:
            res = (int(all_params[1]), int(all_params[2]))

            # Set the resolution
            game_ctx.config.DISPLAY["RESOLUTION"] = res
            print(f'Resolution changed to {res}')

        except ValueError:
            print("Integer values required.")

        if no_of_params > 2:
            try:
                # Set the fullscreen
                game_ctx.config.DISPLAY["FULLSCREEN"] = bool(int(all_params[3]))
            except ValueError:
                print("Integer value 0/1 required for fullscreen settings")

        # Reinit the whole program after change of display configuration
        game_ctx.reinit()

        '''
        # Init what is needed
        game_ctx.config.init(
             log_init=False,
             font_init=False,
             frame_init=False,
             sound_init=False,
             state_init=False 
             )
        print(f'Config reinit done')

        # Reinit all processors by calling their reinit function
        game_ctx.engine.ecs_manager.reinit_processors()

        # Reinit all components by calling their reinit funftion
        game_ctx.engine.ecs_manager.reinit_components()

        # Call init also on the State modules - should pe part of the state_init
        game_ctx._init_state_modules()
        '''

        # Hide console in order for the camera resolution to take effect
        if game_ctx.state_manager.state == game_ctx.State.CONSOLE:
            game_ctx.state_manager.change_state(game_ctx.State.GAME)
            game_ctx.cons.toggle()
            return 0
