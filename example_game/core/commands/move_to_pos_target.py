''' Module implementing MOVE_TO_POS_TARGET command 

For tests call python -m pyrpg.core.commands.commands.new.move_to_pos_target -v

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
    - ctx: CommandContext,  # Contains information from other commands and statistics
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
from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from core.components.position import Position # To work with components in commands (remove search add ...)
from .move_to_pos_px import process as cmd_move_to_pos_px # import other existing command
from .move_to_pos_px import init as cmd_move_to_pos_px_init

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        target,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:
        :param target: Entity_id of the target
        :type target: int

        :returns: None

    Tests:

        Prepare mocs:
        -------------
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(), target=2)
    ''' 

    # Reuse existing init from more general move to px function
    cmd_move_to_pos_px_init(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        **cmd_kwargs
    )

    # Add new local - position component of the target
    ctx.locals.add('_tar_pos', ecs_mng.try_component(target, Position))


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        target,
        proximity_px=10,
        max_time_s=None,
        change_dir_ms=1000,
        dt_comp=True,
        absolute=False,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move to the position of certain entity on the current map.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param target: Entity_id that should be reached.
        :type target: int
        
        :param proximity_px: How far from the target to stop
        :type proximity_px: int
        
        :param max_time_s: Maximum time before ending with failure. If None, never fails.
        :type max_time_s: int

        :param change_dir_ms: How long keep direction before changing it
        :type change_dir_ms: int

        :param dt_comp: Should delta time (dt) correction be taken into account.
        :type dt_comp: bool

        :param absolute: Should velocity be ignored (only move by vector, not multipy by velocity).
        :type absolute: bool

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock
        >>> from core.components.position import PositionMock
        >>> ctx_mock = CommandContextMock()

        Run tests:
        ----------
        -> Test No Context
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=None, target=2)
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Target Ceased to Exist
            >>> ctx_mock.locals.add("_tar_pos", None)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, target=2)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Entity Ceased to Exist
            >>> ctx_mock.locals.add("_ent_pos", None)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, target=2)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position Not Reached in Time
            >>> ctx_mock.duration = 20000
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, target=2, max_time_s=5)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position has been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=91, y=105))
            >>> ctx_mock.locals.add("_tar_pos", PositionMock(x=85, y=105))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, target=2)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Target Position has not been Reached Yet
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=91, y=120))
            >>> ctx_mock.locals.add("_tar_pos", PositionMock(x=20, y=10))
            >>> ctx_mock.locals.add("_last_dir_change", 50)
            >>> ctx_mock.locals.add("_move_axis", "X")
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, target=2)
            <CommandStatus.RUNNING: 'RUNNING'>
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{ctx=}')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'

    # Check if target have still position component, if not finish. Entity position
    # component existence is checked in move_to_pos_px command.
    if ctx.locals._tar_pos is None: return CommandStatus.FAILURE

    return cmd_move_to_pos_px(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        # 'Public' attributes specific to this command and used while calling the command
        pos=(ctx.locals._tar_pos.x, ctx.locals._tar_pos.y),
        proximity_px=proximity_px,
        max_time_s=max_time_s,
        change_dir_ms=change_dir_ms,
        dt_comp=dt_comp,
        absolute=absolute,
        # The rest of parameters, if needed
        **cmd_kwargs
    )

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
