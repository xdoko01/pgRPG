''' Module implementing DO_PARALLEL command 

For tests call python -m example_game.core.commands.do_parallel -v

Command module represents one command only. The name of the module must be the same as the name of the
command.

Command module must consists of 3 functions:

    - initialize() ... Function that registers the command with the CommandManager.
    - init() ... Function that is executed when the command is called for the first time. Used
                 to setup local parameters for the process function to use.
    - process() ... Function implementing the command. Must return CommandStatus.

Every init() and process() functions must always have at least the following parameters:
    - ecs_mng: ECSManager,      # Provides all necessary tools for manipulating the game world
    - entity_id: int,           # Game world entity to which the command should be applied
    - ctx: CommandContext,      # Contains information from other commands and statistics
'''

######## INIT PART

### DO NOT REMOVE - Support of command logging
import logging
logger = logging.getLogger(__name__)

### DO NOT REMOVE - Mandatory registration function
def initialize(register, module_name):
    '''Command registers itself at CommandManager under specific name
    that will be used to call the command. More then one name can 
    be used for the same command if needed.
    '''
    register(fnc=process, alias=module_name)  # mandatory, register the process under the name of the module
    register(fnc=init, alias=module_name+'_init')  # mandatory, register the init under module_init name

######## COMMAND PART

### DO NOT REMOVE - Mandatory imports
from types import ModuleType # for type hint on importing the ecs_manager module
from pgrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from functools import reduce

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        commands,
        returns,
        ticks=None,
        defaults=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:

        :param commands: list of commands that should be executed in one click
        :type commands: list

        :param returns: mapping of results of individual commands to the overall result of parallel command
        :type returns: dict

        :param ticks: specifies if the command should run every tick or every x-tick only
        :type ticks: list

        :param defaults: specifies the default return value if the command is not called during this tick
        :type defaults: str ("SUCCESS", "FAILURE", "RUNNING")
    '''

    logger.debug(f'{entity_id=}. Starting init')

    # Store functions for calling the commands
    ctx.locals.add('exec_cmd_fnc', ecs_mng._game_functions['FNC_EXEC_CMD'])
    ctx.locals.add('exec_cmd_init_fnc', ecs_mng._game_functions['FNC_EXEC_CMD_INIT'])

    # Call init on all the commands that we want to execute in parallel
    for command in commands:
        cmd_name, cmd_params = command
        ctx.locals.exec_cmd_init_fnc(ecs_mng=ecs_mng, entity_id=entity_id, cmd_ctx=ctx, cmd_name=cmd_name, cmd_params=cmd_params)

    logger.debug(f'{entity_id=}. Locals initiated: {ctx.locals=}')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        commands,
        returns,
        ticks=None,
        defaults=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move to the target entity position using the path.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param commands: list of commands that should be executed in one click
        :type commands: list

        :param returns: mapping of results of individual commands to the overall result of parallel command
        :type returns: dict

        :param ticks: specifies if the command should run every tick or every x-tick only
        :type ticks: list

        :param defaults: specifies the default return value if the command is not called during this tick
        :type defaults: str ("SUCCESS", "FAILURE", "RUNNING")

        :returns: CommandStatus
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{ctx=}')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'
    
    # Execute every command and store the result in the list
    cmd_results = []
    for cmd_ord, command in enumerate(commands):

        # Run every x tick
        if ctx.tick_count % (ticks[cmd_ord] if (ticks and ticks[cmd_ord]) else 1) == 0:
            cmd_name, cmd_params = command
            res = ctx.locals.exec_cmd_fnc(ecs_mng=ecs_mng, entity_id=entity_id, cmd_name=cmd_name, cmd_params=cmd_params, cmd_ctx=ctx)
            cmd_results.append(res)
        else:
            # if its not time right tick, return the default
            cmd_results.append(CommandStatus[defaults[cmd_ord]])
    
    logger.debug(f'{entity_id=}. Result of commands is {cmd_results=}. ')

    # Return the final do_parallel result based on results parameter
    
    # 1. Only evaluate the results if any of commands returns something else than RUNNING
    if all(cmd_results) == CommandStatus.RUNNING:
        logger.debug(f'{entity_id=}. All commands are still RUNNING. Returning Running') 
        return CommandStatus.RUNNING

    # 2.Re-cast the results to the string representation -> e.g. CommandsStatus.FAILURE, CommandStatus.SUCCESS to 'FS'
    cmd_results = reduce(lambda x, y: x+y, map(lambda cs: cs.value[0], cmd_results))
    
    # 3. find the exact result in the returns dict
    res = returns.get(cmd_results)

    # 4. if no exact result found, try to match with the substituting X character
    logger.debug(f'{entity_id=}. FOund the record in results {res=}. Returning {CommandStatus[res]}')
    return CommandStatus[res]

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
