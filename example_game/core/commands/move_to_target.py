''' Module implementing MOVE_TO_TARGET command 

For tests call python -m example_game.core.commands.move_to_target -v

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
from pyrpg.core.config import GAME # for TILE_RES_PX

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        target,
        upd_path_ms=5000, # after how many ms to update the path
        max_time_s=None, # how long to chase
        proximity_tl=0, # how close to get to finish successfully
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

    logger.debug(f'{entity_id=}. Start move_to_target init')

    # If target not exists or position component not exist, create _tar_pos as None and exit
    try:
        ctx.locals.add('_tar_pos', ecs_mng.try_component(target, Position))
        ctx.locals.add('_last_tar_pos', ctx.locals._tar_pos.get_tile())
        ctx.locals.add('_last_path_change', ctx.current_time)

        cmd_move_to_init(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            # 'Public' attributes specific to this command and used while calling the command
            pos=ctx.locals._last_tar_pos,
            # The rest of parameters, if needed
            **cmd_kwargs
        )

    except KeyError:
        logger.debug(f'{entity_id=}. Target or its position component no longer exists. Exiting init.')
        ctx.locals.add('_tar_pos', None)

    logger.debug(f'{entity_id=}. Locals initiated: {ctx.locals=}')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        target,
        upd_path_ms=5000, # after how many ms to update the path
        max_time_s=None, # how long to chase
        proximity_tl=0, # how close to get to finish successfully
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

    # Check if target still exists
    if ctx.locals._tar_pos is None:
        logger.debug(f'Target Entity component reference is lost, returning failure.')
        return CommandStatus.FAILURE

    # Check if target reached
    proximity_px = proximity_tl * GAME["TILE_RES_PX"]
    if abs(ctx.locals._tar_pos.x - ctx.locals._ent_pos.x) <= proximity_px and abs(ctx.locals._tar_pos.y - ctx.locals._ent_pos.y) <= proximity_px:
        return CommandStatus.SUCCESS

    # Check if it is time to recalc the path
    if ctx.current_time - ctx.locals._last_path_change >= upd_path_ms:

        # Check, if we are not moving to the target for too long
        if max_time_s is not None and ctx.duration > max_time_s*1000: 
            logger.debug(f'Max time for movement is up. Returning failure.')
            return CommandStatus.FAILURE

        # Start over
        init(ecs_mng=ecs_mng, entity_id=entity_id, ctx=ctx, target=target, **cmd_kwargs)

        # Log
        logger.debug(f'Updating/restarting path after {upd_path_ms=} ms. New target pos {ctx.locals._last_tar_pos}. New path {ctx.locals._path=}')

    # Move to _last_tar_pos
    res = cmd_move_to(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            # 'Public' attributes specific to this command and used while calling the command
            pos=ctx.locals._last_tar_pos,
            # The rest of parameters, if needed
            **cmd_kwargs
        )

    # Check if the target is near. If not, continue moving towards it
    if res == CommandStatus.SUCCESS:

        # Check if entity is close enough to the target to finish successfully
        tar_pos_tl = ctx.locals._tar_pos.get_tile()
        ent_pos_tl = ctx.locals._ent_pos.get_tile()

        if abs(tar_pos_tl[0] - ent_pos_tl[0]) <= proximity_tl and abs(tar_pos_tl[1] - ent_pos_tl[1]) <= proximity_tl:
            return CommandStatus.SUCCESS

        else:
            # Start over
            init(ecs_mng=ecs_mng, entity_id=entity_id, ctx=ctx, target=target, **cmd_kwargs)
            return CommandStatus.RUNNING
    else:
        return res

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
