''' Script for engine initiation

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "init_engine"         ... initiate the engine
        "init_engine -h"      ... get usage instructions
        "init_engine --help"  ... get usage instructions
'''

instructions = """
Examples of usage:
    "init_engine"         ... initiate the engine
    "init_engine -h"      ... get usage instructions
    "init_engine --help"  ... get usage instructions
"""
# Init logging config
import logging
logger = logging.getLogger(__name__)

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_init_engine, alias=module_name)

def cons_cmd_init_engine(game_ctx, params):
    ''' Script that loads the scene
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so or 0 parameters
    if all_params[-1] in ('-h','--help', '?', 'help'):
        print(instructions)

    # Loads the scene
    else:
        logger.info(f'Initiating engine {game_ctx=}')
        game_ctx._init_engine()
        return 0