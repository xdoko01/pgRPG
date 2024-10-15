''' Module implementing MOVE_TO_CHECKPOINTS command 

For tests call python -m pyrpg.core.commands.commands.new.move_to_checkpoints -v

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
from pyrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from core.components.position import Position # To work with components in commands (remove search add ...)
from .move_to import process as cmd_move_to # import other existing command
from .move_to import init as cmd_move_to_init # import other existing command

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        checkpoints,
        #upd_path_ms=5000, # after how many ms to check for update of the checkpoints
        repeat=False,
        max_time_s=None, # how long to move along the checkpoints
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:

        :param target: Target entity id.
        :type target: int

        :returns: None

    Tests:

        Prepare mocs:
        -------------
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock
        >>> ctx_mock = CommandContextMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
        >>> print((ctx_mock.locals._px_pos, ctx_mock.locals._path[0], ctx_mock.locals._path_idx))
        ((96, 96), (1, 1), 0)
    '''

    logger.debug(f'{entity_id=}. Start move_to_checkpoints init')

    # Add new local - position component of the target
    #ctx.locals.add('_tar_pos', ecs_mng.try_component(target, Position))
    #ctx.locals.add('_last_tar_pos', ctx.locals._tar_pos.get_tile())
    #ctx.locals.add('_last_path_change', ctx.current_time)
    ctx.locals.add('_checkpoints', checkpoints)
    ctx.locals.add('_checkpoint_idx', 0)
    ctx.locals.add('_next_checkpoint', checkpoints[0])

    cmd_move_to_init(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        # 'Public' attributes specific to this command and used while calling the command
        pos=ctx.locals._next_checkpoint,
        # The rest of parameters, if needed
        **cmd_kwargs
    )

    logger.debug(f'{entity_id=}. Locals initiated: {ctx.locals=}')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        checkpoints,
        #upd_path_ms=5000, # after how many ms to update the path
        repeat=False,
        max_time_s=None, # how long to chase
        #proximity_tl=0, # how close to get to finish successfully
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
        :param target: Target entity id
        :type target: int
        
        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock
        >>> from core.components.position import PositionMock

        >>> ctx_mock = CommandContextMock()
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
        >>> print((ctx_mock.locals._px_pos, ctx_mock.locals._path[0], ctx_mock.locals._path_idx))
        ((96, 96), (1, 1), 0)

        Run tests:
        ----------
        -> Test No Context
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=None, pos=[10,10])
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Entity Ceased to Exist
            >>> ctx_mock.locals.add("_ent_pos", None)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position has not been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=91, y=120))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
            <CommandStatus.RUNNING: 'RUNNING'>

        -> Test Target Position has been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=672, y=672))
            >>> ctx_mock.locals.add("_path", ((1,1),(2,2),(10,10)))
            >>> ctx_mock.locals.add("_path_idx", 2)
            >>> ctx_mock.locals.add("_px_pos", (672,672))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
            <CommandStatus.SUCCESS: 'SUCCESS'>
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{ctx=}')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'

    # Move to _next_checkpoint
    res = cmd_move_to(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            # 'Public' attributes specific to this command and used while calling the command
            pos=ctx.locals._next_checkpoint,
            # The rest of parameters, if needed
            **cmd_kwargs
        )

    # Check if the checkpoint is near. If not, continue moving towards it
    if res == CommandStatus.SUCCESS:

        # Log that checkpoint has bean reached
        logger.debug(f'{entity_id=}. Standing on the checkpoint {ctx.locals._next_checkpoint}. ')

        # If standing on the last checkpoint finish with success or repeat the checkpoints
        if (ctx.locals._checkpoint_idx == len(ctx.locals._checkpoints) - 1):
            if not repeat:
                logger.debug(f'Standing on the last checkpoint. Returning SUCCESS.')
                return CommandStatus.SUCCESS
            else:
                ctx.locals._checkpoint_idx = -1   # Continue from the start

        # Otherwise, move to the next checkpoint
        ctx.locals._checkpoint_idx += 1
        ctx.locals._next_checkpoint = ctx.locals._checkpoints[ctx.locals._checkpoint_idx]
        logger.debug(f'{entity_id=}. Next checkpoint to visit {ctx.locals._next_checkpoint}.')

        cmd_move_to_init(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            pos=ctx.locals._next_checkpoint,
            **cmd_kwargs
        )

        return CommandStatus.RUNNING

    else:
        return res

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
