''' Script for listing of all processors in ordered manner.

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "get_processors -h  ... get usage instructions"
        "get_processors --help  ... get usage instructions"
        "get_processors     ... shows processors"
'''

instructions = """
Examples of usage:
    "get_processors -h  ... get usage instructions"
    "get_processors --help  ... get usage instructions"
    "get_processors     ... shows processors"
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_get_processors, alias=module_name)

def cons_cmd_get_processors(game_ctx, params):
    ''' Script that shows processors used in the game
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params > 0:
        print(instructions)

    # Show processors
    else:
        for processor in game_ctx.engine.ecs_manager._world._processors:
            print(processor)

