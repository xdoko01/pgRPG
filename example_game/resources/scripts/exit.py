''' Script for exiting the game

    Parameters passed from console:
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

# Save all parameters passed from the Console in the list
all_params = params.split()
no_of_params = len(all_params) - 1 # exclude the script name

# Show instructions if the last parametr indicates so
if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params > 0:
    print(instructions)

# Exit the game
else:
    game.end()