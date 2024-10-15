''' Module implementing MOVE_TO command 

For tests call python -m pyrpg.core.commands.commands.new.move_to -v

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
from .move_to_pos_tile import process as cmd_move_to_pos_tile # import other existing command
from .move_to_pos_tile import init as cmd_move_to_pos_tile_init # import other existing command

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
        >>> ctx_mock = CommandContextMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[10,10])
        >>> print((ctx_mock.locals._px_pos, ctx_mock.locals._path[0], ctx_mock.locals._path_idx))
        ((96, 96), (1, 1), 0)
    '''

    logger.debug(f'{entity_id=}. Start move_to init')

    # Must be here. Did not want to put the whole tile move init here.
    ctx.locals.add('_ent_pos', ecs_mng.component_for_entity(entity_id, Position))

    # Additional parameters that can be used in the command
    #pos_comp = ecs_mng.try_component(entity_id, Position)
    map = ecs_mng._game_functions['FNC_GET_MAP'](ctx.locals._ent_pos.map)

    path_calc_request_id = ecs_mng._game_functions['FNC_REQUEST_PATHFIND'](
        graph=map.path_graph, 
        start=ctx.locals._ent_pos.get_tile(), 
        goal=(pos[0], pos[1]),
        search='BFS_CHECKPOINTS'
    )

    ctx.locals.add('_path_calc_request_id', path_calc_request_id)
    ctx.locals.add('_path', None) # path not yet found
    #ctx.locals.add('_path_idx', 0)

    logger.debug(f'{entity_id=}. Path calculation request from {ctx.locals._ent_pos.get_tile()} to {(pos[0], pos[1])} created')

    logger.debug(f'{entity_id=}. Locals initiated: {ctx.locals=}')
    logger.debug(f'{entity_id=}. End move_to init')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
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

    logger.debug(f'{entity_id=}. Start move_to process')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'

    # Still waiting for the path to be calculated
    if ctx.locals._path is None:
        logger.debug(f'{entity_id=}. Path not yet initialized, checking the path calculation request id: {ctx.locals._path_calc_request_id}')

        # Check if the path is already calculated
        path = ecs_mng._game_functions['FNC_GET_PATH'](ctx.locals._path_calc_request_id)

        # Still calculating, wait further
        if path is None: 
            logger.debug(f'{entity_id=}. Pathfinding is still in progress. Ending with RUNNING.')
            return CommandStatus.RUNNING

        # If no path to the target can be found, end with failure
        if path == []:
            logger.debug(f'{entity_id=}. No path to the target found, ending with FAILURE')
            return CommandStatus.FAILURE

        # PATH FOUND, calculation done, store the path and init movement to the first point on the path
        ctx.locals.add('_path', path)
        ctx.locals.add('_path_idx', 0) # move to the first point first
        logger.debug(f'{entity_id=}. Path found. {ctx.locals._path=}, {ctx.locals._path_idx=}')

        # Reuse existing init from more general move to px function - this will help you to get variables in the locals such as _ent_pos
        logger.debug(f'{entity_id=}. Calling move_to_pos_tile_init ...')
        cmd_move_to_pos_tile_init(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            pos=(path[ctx.locals._path_idx]), # init movement to the first point on the path
            **cmd_kwargs
        )


    # Move along the path
    logger.debug(f'{entity_id=}. Moving to path point {ctx.locals._path[ctx.locals._path_idx]} on index {ctx.locals._path_idx}')

    logger.debug(f'{entity_id=}. Calling move_to_pos_tile command to move to {ctx.locals._path[ctx.locals._path_idx]}')
    res = cmd_move_to_pos_tile(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            # 'Public' attributes specific to this command and used while calling the command
            pos=(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1]),
            proximity_px=5,
            max_time_s=None,
            change_dir_ms=0,
            #dt_comp=dt_comp,
            #absolute=absolute,
            # 'Private' attributes that have been prepared by init function
            #_ent_pos=_ent_pos,
            #_last_dir_change=0,
            #_move_axis=,
            # The rest of parameters, if needed
            **cmd_kwargs
        )
    
    # In case moving to the next tile succeeds - move to the next tile in the path and return RUNNING
    if res == CommandStatus.SUCCESS:
        logger.debug(f'{entity_id=}. Moving to tile {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])} ended with success. My position is {ctx.locals._ent_pos.get_tile()}')
        # Check if we are at the end
        if ctx.locals._path_idx == len(ctx.locals._path) - 1: 
            logger.debug(f'{entity_id=}. End of the path reached. Returning SUCCESS.')
            return CommandStatus.SUCCESS

        # New point of the path
        ctx.locals._path_idx += 1
        logger.debug(f'{entity_id=}. Targeting to the next point {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])} and returning running')
        
        # Init movement between new 2 points
        logger.debug(f'{entity_id=}. Calling move_to_pos_tile_init ...')
        cmd_move_to_pos_tile_init(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            pos=(ctx.locals._path[ctx.locals._path_idx]),
            **cmd_kwargs
        )

        # Continue on the path with the next point
        return CommandStatus.RUNNING

    elif res == CommandStatus.FAILURE:
        logger.debug(f'{entity_id=}. Moving to tile {(ctx.locals._path[ctx.locals._path_idx][0], ctx.locals._path[ctx.locals._path_idx][1])} FAILED')

    return res

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
