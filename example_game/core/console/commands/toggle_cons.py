''' Script for toggle to/from fullscreen 

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "toggle_fullscreen"         ... toggle to/from fullscreen from/to window
        "toggle_fullscreen -h"      ... get usage instructions
        "toggle_fullscreen --help"  ... get usage instructions
        "toggle_fullscreen 1"       ... switch to fullscreen
        "toggle_fullscreen 0"       ... switch to windowed mode
'''

instructions = """
Examples of usage:
    "toggle_fullscreen"         ... toggle to/from fullscreen from/to window
    "toggle_fullscreen -h"      ... get usage instructions
    "toggle_fullscreen --help"  ... get usage instructions
    "toggle_fullscreen 1"       ... switch to fullscreen
    "toggle_fullscreen 0"       ... switch to windowed mode
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_toggle_cons, alias=module_name)

def cons_cmd_toggle_cons(game_ctx, params):
    ''' Script that switches to fullscreen
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params > 0:
        print(instructions)

    # Try to toggle fullscreen
    else:

        if game_ctx.state_manager.state == game_ctx.State.CONSOLE:
            game_ctx.state_manager.change_state(game_ctx.State.GAME)
            game_ctx.cons.toggle()
            return 0
