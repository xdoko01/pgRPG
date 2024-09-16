''' Script for listing of all processors in ordered manner.

    Parameters passed from console:
        :params: The whole command passed from console containing the script name and parameters

    Examples:
        "! get_processors"
'''
# Save all parameters passed from the Console in the list
all_params = params.split()

for processor in game.main.engine.ecs_manager.get_game_world()._processors:
	print(processor)

