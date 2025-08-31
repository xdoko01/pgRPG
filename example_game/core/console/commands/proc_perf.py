''' Script for getting the cumulative time spent in processors - tracking of performance.

    Parameters passed from console:
        :param game_ctx: Reference to the console entry point to the game (main module). 
                         Depends on the console configuration.
        :type game_ctx: ref

        :param params: The whole command passed from console containing the script name and parameters
        :type params: str

    Examples of usage:
        "proc_perf"            ... show cumulative time spent in processors
        "proc_perf -h"         ... get usage instructions
        "proc_perf --help"     ... get usage instructions
        "proc_perf -s"         ... show ordered by process time
        "proc_perf --sort"     ... show ordered by process time
'''

instructions = """
In the config, section "PYRPG",  "TIMED" must be set to true in order for this stats to work.

Examples of usage:
    "proc_perf"            ... show cumulative time spent in processors
    "proc_perf -h"         ... get usage instructions
    "proc_perf --help"     ... get usage instructions
    "proc_perf -s"         ... show ordered by process time
    "proc_perf --sort"     ... show ordered by process time
    "proc_perf -t"         ... show top 10 slowest processes
    "proc_perf --top"      ... show top 10 slowest processes

"""
# Support of command logging
import logging
logger = logging.getLogger(__name__)

from pprint import pprint, pformat

def initialize(register, module_name):
    '''Script registers itself at Console'''
    # Mandatory line
    register(fnc=cons_cmd_change_res, alias=module_name)

def cons_cmd_change_res(game_ctx, params):
    ''' Script that changes game resolution
    '''

    # Save all parameters passed from the Console in the list
    all_params = params.split()
    no_of_params = len(all_params) - 1 # exclude the script name

    # Show instructions if the last parametr indicates so
    if all_params[-1] in ('-h','--help', '?', 'help'):
        print(instructions)

    # Show the performance information
    elif all_params[-1] in ('-s','--sort'):
        pprint(game_ctx.engine.ecs_manager.get_proc_perf(sort=True), sort_dicts=False)
    elif all_params[-1] in ('-t','--top'):
        pprint({k: v for k, v in list(game_ctx.engine.ecs_manager.get_proc_perf(sort=True).items())[:10]}, sort_dicts=False)
    else:
        pprint(game_ctx.engine.ecs_manager.get_proc_perf(), sort_dicts=False)
