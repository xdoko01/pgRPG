''' Module implementing ATTACK command 

For tests call `python -m example_game.core.commands.attack -v`

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

######## COMMAND(S) PART

### DO NOT REMOVE - Mandatory imports
from types import ModuleType # for type hint on importing the ecs_manager module
from pgrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from core.components.flag_do_attack import FlagDoAttack # To work with components in commands (remove search add ...)

# DO NOT REMOVE - Mandatory function
def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        attack_time_ms: int=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:
        :param attack_time_ms: How long attack commands should be generated, default None (do not repeat)
        :type attack_time_ms: int

        :returns: None

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock
        >>> ctx_mock = CommandContextMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, attack_time_ms=1000)
        >>> print(ctx_mock.locals)
        {}
    '''
    pass

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        attack_time_ms: int=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param attack_time_ms: How long attack commands should be generated, default None (do not repeat)
        :type attack_time_ms: int

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock
        >>> ctx_mock = CommandContextMock()

        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, attack_time_ms=1000)
        >>> print(ctx_mock.locals)
        {}

        Run tests:
        ----------
        -> Test Attack Should Stop 1
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(duration=1200), attack_time_ms=1000)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Attack Should Continue 1
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(duration=500), attack_time_ms=1000)
            <CommandStatus.RUNNING: 'RUNNING'>

        -> Test Attack Should Stop 2
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(duration=500))
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Attack Should Stop 3
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=None, attack_time_ms=1000)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Attack Should Stop 
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock())
            <CommandStatus.SUCCESS: 'SUCCESS'>
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{ctx=}')

    # Mark the attack
    ecs_mng.add_component(entity_id, FlagDoAttack())

    if ctx is None or attack_time_ms is None or ctx.duration > attack_time_ms:
        return CommandStatus.SUCCESS

    return CommandStatus.RUNNING


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception


    # Run the tests
    import doctest
    doctest.testmod()

