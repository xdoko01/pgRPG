''' Script for loading thescene

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "load_scene"         ... get usage instructions
        "load_scene -h"      ... get usage instructions
        "load_scene --help"  ... get usage instructions
        "load_scene scene_file"  ... loads scene file
'''

instructions = """
Examples of usage:
    "load_scene"         ... get usage instructions
    "load_scene -h"      ... get usage instructions
    "load_scene --help"  ... get usage instructions
    "load_scene scene_file"  ... loads scene file
"""
# Init logging config
import logging
logger = logging.getLogger(__name__)

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_load_scene, alias=module_name)

def cons_cmd_load_scene(game_ctx, params):
    ''' Script that loads the scene
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so or 0 parameters
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params == 0:
        print(instructions)

    # Loads the scene
    else:
        logger.info(f'Starting loading new scene with {game_ctx.engine=}')
        game_ctx.engine.new_game(scene_file=all_params[1])

        logger.info(f'Current State is "{game_ctx.state_manager.state}".')

        # Hide console in order for the camera resolution to take effect
        if game_ctx.state_manager.state == game_ctx.State.CONSOLE:
            logger.info(f'Changing State to GAME')
            game_ctx.state_manager.change_state(game_ctx.State.GAME)
            game_ctx.cons.toggle()
            return 0

        return 0