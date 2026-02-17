''' Script for listing of all commands implemented as a script

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "list"         ... list all the available commands
        "list -h"      ... get usage instructions
        "list --help"  ... get usage instructions
'''

instructions = """
    Examples of usage:
        "list"         ... list all the available commands
        "list -h"      ... get usage instructions
        "list --help"  ... get usage instructions
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_list, alias=module_name)

def cons_cmd_list(game_ctx, params):
    ''' Script that lists all the commands
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params > 0:
        print(instructions)

    # List commands and scripts
    else:
        
        import os
        from pgrpg.core.config import MODULEPATHS, FILEPATHS

        print("Available Console Commands:")
        commands = [cmd[:-3] for cmd in os.listdir(f"{FILEPATHS['GAME_PATH']}/{MODULEPATHS['CONSOLE_COMMAND_MODULE_PATH'].replace('.', '/')}") if cmd[0:2] != '__' and cmd[-3:].lower() == '.py']
        print(commands)

        print("Registered Console Commands:")
        print(game_ctx.cons.cli._cmd_scripts)

        print("Available Console Scripts:")
        print(os.listdir(f"{FILEPATHS['CONSOLE_SCRIPT_PATH']}"))
