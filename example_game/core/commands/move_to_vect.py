''' Module implementing MOVE_TO_VECT command 

For tests call python -m pyrpg.core.commands.commands.new.move_to_vect -v

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
from .move_to_pos_tile_vect import process as cmd_move_to_pos_tile_vect # import other existing command
from .move_to_pos_tile_vect import init as cmd_move_to_pos_tile_vect_init # import other existing command

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
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
        >>> ctx_mock = CommandContextMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
        >>> print((ctx_mock.locals._px_pos, ctx_mock.locals._path[0], ctx_mock.locals._path_idx))
        ((96, 96), (1, 1), 0)

    '''

    # Additional parameters that can be used in the command
    pos_comp = ecs_mng.try_component(entity_id, Position)
    map = ecs_mng._game_functions['FNC_GET_MAP'](pos_comp.map)
    path = map.get_path_bfs(
        start=pos_comp.get_tile(), 
        end=(pos[0], pos[1]),
        inc_start=True, # In order to simlify the path in the get_path_checkpoints function, it is necessary to include start 
        avail_moves=((1,1),(1,-1),(-1,-1),(-1,1),(0,1),(1,0),(0,-1),(-1,0))
    )
    path = map.get_path_checkpoints(path) # Path contains only points where direction is changed
    ctx.locals.add('_ent_pos', pos_comp)
    ctx.locals.add('_path', path)
    ctx.locals.add('_path_idx', 0) # move to the first point first

    logger.debug(f'Calling move_to_pos_px_tile_vect_init ...')
    # Reuse existing init from more general move to px function
    cmd_move_to_pos_tile_vect_init(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        pos=(path[0] if len(path) > 0 else None),  #Move to the first point in the path or stay on the same place
        **cmd_kwargs
    )

    logger.debug(f'Locals initiated: {ctx.locals=}')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        pos,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move to the position using the path.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param pos: Target position in tiles
        :type pos: list
        
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

        -> Test Target Position Not Reached in Time
            ctx_mock.duration = 20000
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

    logger.debug(f'Moving to path point {ctx.locals._path[ctx.locals._path_idx]} -> {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])}')

    res = cmd_move_to_pos_tile_vect(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            # 'Public' attributes specific to this command and used while calling the command
            pos=(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1]),
            #max_time_s=None,
            dt_comp=True,
            absolute=False,
            # The rest of parameters, if needed
            **cmd_kwargs
        )
    
    # In case moving to the next tile succeeds - move to the next tile in the path and return RUNNING
    if res == CommandStatus.SUCCESS:
        logger.debug(f'Moving to tile {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])} ended with success. My position is {ctx.locals._ent_pos.get_tile()}')
        # Check if we are at the end
        if ctx.locals._path_idx == len(ctx.locals._path) - 1: return CommandStatus.SUCCESS

        # New point of the path
        ctx.locals._path_idx += 1
        logger.debug(f'Targeting to the next point {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])} and returning running')
        
        # Init movement between new 2 points
        logger.debug(f'Calling move_to_pos_px_tile_init ...')
        cmd_move_to_pos_tile_vect_init(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            pos=(ctx.locals._path[ctx.locals._path_idx]),
            **cmd_kwargs
        )

        # Continue on the path with the next point
        return CommandStatus.RUNNING

    elif res == CommandStatus.FAILURE:
        logger.debug(f'Moving to tile {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])} FAILED')

    return res

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
