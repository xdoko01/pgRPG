''' Script for exiting the game

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "exit"         ... exits the game
        "exit -h"      ... get usage instructions
        "exit --help"  ... get usage instructions
'''

instructions = """
Examples of usage:
        "exit"         ... exits the game
        "exit -h"      ... get usage instructions
        "exit --help"  ... get usage instructions
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_exit, alias=module_name)

def cons_cmd_exit(game_ctx, params):
    ''' Script that exits the game
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params > 0:
        print(instructions)

    # Exit the game
    else:
        game_ctx.state_manager.change_state(game_ctx.State.END_PROGRAM)
        return 0