''' Module implementing WAIT command 

For tests call python -m pyrpg.core.commands.commands.new.wait -v

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
    - cmd_ctx: CommandContext,  # Contains information from other commands and statistics
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
from pyrpg.core.managers.ecs_manager import ECSManager, ECSManagerMock
from pyrpg.core.commands import CommandContext, CommandContextMock, CommandStatus

def init(
        # Mandatory attributes that must be always present
        # 'Public' attributes specific to this command and used while calling the command
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:

        :returns: None

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), duration_ms=2000)
    '''
    pass

def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        duration_ms,
        # 'Private' attributes that have been prepared by init function
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Wait for some specific duration.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param duration_ms: How long to wait in ms.
        :type duration_ms: int

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        -> Test No Context
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=None, duration_ms=2000)
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Time is Still Running
            >>> cmd_ctx_mock = CommandContextMock(duration=500)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=cmd_ctx_mock, duration_ms=2000)
            <CommandStatus.RUNNING: 'RUNNING'>

        -> Test Time is Up
            >>> cmd_ctx_mock = CommandContextMock(duration=2500)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=cmd_ctx_mock, duration_ms=2000)
            <CommandStatus.SUCCESS: 'SUCCESS'>
        '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{cmd_ctx=}')

    # Command must run with context, else does not make sense
    assert cmd_ctx is not None, f'Command cannot run without context.'

    # Did I wait enough?
    if (cmd_ctx.duration < duration_ms) :

        # There is still some time to wait
        return CommandStatus.RUNNING
    else:
        # Time is up, end waiting
        return CommandStatus.SUCCESS

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()