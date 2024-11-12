''' Script for toggle to/from fullscreen 

    Parameters passed from console:
        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "c_toggle_fullscreen"         ... toggle to/from fullscreen from/to window
        "c_toggle_fullscreen -h"      ... get usage instructions
        "c_toggle_fullscreen --help"  ... get usage instructions
        "c_toggle_fullscreen 1"       ... switch to fullscreen
        "c_toggle_fullscreen 0"       ... switch to windowed mode
'''

instructions = """
Examples of usage:
    "c_toggle_fullscreen"         ... toggle to/from fullscreen from/to window
    "c_toggle_fullscreen -h"      ... get usage instructions
    "c_toggle_fullscreen --help"  ... get usage instructions
    "c_toggle_fullscreen 1"       ... switch to fullscreen
    "c_toggle_fullscreen 0"       ... switch to windowed mode
"""

params: str

# Save all parameters passed from the Console in the list
all_params = params.split()
no_of_params = len(all_params) - 1 # exclude the script name

# Show instructions if the last parametr indicates so
if all_params[-1] in ('-h','--help', '?', 'help') or no_of_params > 1:
    print(instructions)

# Try to toggle fullscreen
else:

    # If no parameters, toggle
    if no_of_params == 0:
        game.config.DISPLAY["FULLSCREEN"] = not game.config.DISPLAY["FULLSCREEN"]
    
    elif no_of_params == 1:
        try:
            game.config.DISPLAY["FULLSCREEN"] = bool(int(all_params[1]))
        except ValueError:
            print("Expecting integer value 0/1")

    # Init everything except State of the game
    game.config.init(False)
    print(f'Reinit done')
