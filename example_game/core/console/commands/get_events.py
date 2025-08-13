''' Script for listing invformation about events in the event queue.

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "get_events"         ... get events info
        "get_events -h"      ... get usage instructions
        "get_events --help"  ... get usage instructions
'''

instructions = """
Examples of usage:
    "get_events"         ... get events info
    "get_events -h"      ... get usage instructions
    "get_events --help"  ... get usage instructions
"""

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_get_events, alias=module_name)

def cons_cmd_get_events(game_ctx, params):
    ''' Script that shows entities in the game
    '''
    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help'):
        print(instructions)

    # Show entites
    else:
        # Print the head of the queue
        print(f'First 10 Events in the Queue: {game_ctx.engine.event_manager._event_queue[:10]}')

        # Separator
        print('...')

        # Print the tail of the queue
        print(f'Last 10 Events in the Queue: {game_ctx.engine.event_manager._event_queue[-10:]}')

        # Print the length of the queue
        print(f'No. of Events in the Queue: {len(game_ctx.engine.event_manager._event_queue)}')
