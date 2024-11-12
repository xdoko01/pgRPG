''' Script for change of the resolution

    Parameters passed from console:
        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "c_change_res"           ... get usage instructions
        "c_change_res -h"        ... get usage instructions
        "c_change_res --help"    ... get usage instructions
        "c_change_res 640 480"   ... change the resolution to 640x480
        "c_change_res 640 480 1" ... change the resolution to 640x480 + fullscreen
        "c_change_res 800 600 0" ... change the resolution to 800x600 + windowed
'''

instructions = """
Examples of usage:
    "c_change_res"           ... get usage instructions
    "c_change_res -h"        ... get usage instructions
    "c_change_res --help"    ... get usage instructions
    "c_change_res 640 480"   ... change the resolution to 640x480
    "c_change_res 640 480 1" ... change the resolution to 640x480 + fullscreen
    "c_change_res 800 600 0" ... change the resolution to 800x600 + windowed
"""

from core.components.camera import Camera

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
        game.config.DISPLAY["RESOLUTION"] = res
        print(f'Resolution changed to {res}')

    except ValueError:
        print("Integer values required.")

    if no_of_params > 2:
        try:
            # Set the fullscreen
            game.config.DISPLAY["FULLSCREEN"] = bool(int(all_params[3]))
        except ValueError:
            print("Integer value 0/1 required for fullscreen settings")

    # Init everything except State of the game
    game.config.init(False)
    print(f'Reinit done')

    # Adjust all Camera components for the new resolution
    for ent, (camera) in game.engine.ecs_manager._world.get_component(Camera):
        camera.on_display_change()
        print(f'Camera comp resolution changed on entity {ent}')
    