''' Module implementing MOVE_TO_POS_TILE_VECT command 

For tests call python -m example_game.core.commands.move_to_pos_tile_vect -v

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
from .move_to_pos_px_vect import process as cmd_move_to_pos_px_vect # import other existing command
from .move_to_pos_px_vect import init as cmd_move_to_pos_px_vect_init
from pyrpg.core.config import GAME # for TILE_RES_PX

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        pos,
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
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock
        
        >>> ctx_mock =  CommandContextMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
        >>> print(ctx_mock.locals._px_pos)
        (672, 672)
    '''

    # Add new local - position recalculated to px
    ctx.locals.add('_px_pos', ((pos[0] * GAME["TILE_RES_PX"]) + (GAME["TILE_RES_PX"] // 2), (pos[1] * GAME["TILE_RES_PX"]) + (GAME["TILE_RES_PX"] // 2)))
    
    # Reuse existing init from more general move to px function
    logger.debug(f'Calling move_to_pos_px_init ...')
    cmd_move_to_pos_px_vect_init(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        pos=ctx.locals._px_pos,
        **cmd_kwargs
    )

    logger.debug(f'Locals initiated: {ctx.locals=}')

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        pos,
        max_time_s=None,
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        #_px_pos=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move to the position of specified in tiles on the current map via straight line.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param pos: Target position in tiles
        :type pos: list
                
        :param max_time_s: Maximum time before ending with failure. If None, never fails.
        :type max_time_s: int

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
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=None, pos=[10,10])
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Entity Ceased to Exist
            >>> ctx_mock.locals.add("_ent_pos", None)
            >>> ctx_mock.locals.add("_px_pos", (610,610))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position Not Reached in Time
            >>> ctx_mock.duration = 20000
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10], max_time_s=5)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position has been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=608, y=608))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10], proximity_px=20)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Target Position has not been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=91, y=120))
            >>> ctx_mock.locals.add("_last_dir_change", 50)
            >>> ctx_mock.locals.add("_norm_vect", (0,1))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
            <CommandStatus.RUNNING: 'RUNNING'>
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{ctx=}')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'

    logger.debug(f'Moving to tile {pos[0]}, {pos[1]} -> px pos {ctx.locals._px_pos[0]},{ctx.locals._px_pos[1]}')

    res = cmd_move_to_pos_px_vect(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        # 'Public' attributes specific to this command and used while calling the command
        pos=(ctx.locals._px_pos[0], ctx.locals._px_pos[1]),
        max_time_s=max_time_s,
        dt_comp=dt_comp,
        absolute=absolute,
        # 'Private' attributes that have been prepared by init function
        #_ent_pos=_ent_pos,
        # The rest of parameters, if needed
        **cmd_kwargs
    )

    if res == CommandStatus.SUCCESS:
        logger.debug(f'Moving to tile {pos[0]}, {pos[1]} -> px pos {ctx.locals._px_pos[0]},{ctx.locals._px_pos[1]} was SUCCESSFUL')
    elif res == CommandStatus.FAILURE:
        logger.debug(f'Moving to tile {pos[0]}, {pos[1]} -> px pos {ctx.locals._px_pos[0]},{ctx.locals._px_pos[1]} has FAILED')
    return res


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
