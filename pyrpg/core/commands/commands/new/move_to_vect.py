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

### Optional imports
from pyrpg.core.ecs.components.new.position import Position, PositionMock # To work with components in commands (remove search add ...)
from .move_to_pos_tile_vect import process as cmd_move_to_pos_tile_vect # import other existing command
from .move_to_pos_tile_vect import init as cmd_move_to_pos_tile_vect_init # import other existing command

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
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
        >>> cmd_ctx_mock = CommandContextMock(local_bb={})
        >>> ecs_mng_mock = ECSManagerMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=cmd_ctx_mock, pos=[10,10])
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
    path = map.get_path_checkpoints(path)
    cmd_ctx.local_bb['_ent_pos'] = pos_comp
    cmd_ctx.local_bb['_path'] = path
    cmd_ctx.local_bb['_path_idx'] = 0 # move to the first point first

    logger.debug(f'Calling move_to_pos_px_tile_vect_init ...')
    # Reuse existing init from more general move to px function
    cmd_move_to_pos_tile_vect_init(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        cmd_ctx=cmd_ctx,
        pos=(path[0] if len(path) > 0 else None),  #Move to the first point in the path or stay on the same place
        **cmd_kwargs
    )

    logger.debug(f'Locals initiated: {cmd_ctx.local_bb=}')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        pos,
        #proximity_px=10,
        #max_time_s=None,
        #change_dir_ms=0000,
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        _ent_pos=None,
        _path=[],
        _path_idx=0,
        #_last_dir_change=0,
        #_move_axis=None,
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

        :param _ent_pos: Private attribute holding Position component of the entity.
        :type _ent_pos: Component

        :param _path: List of tiles on the path
        :type _path: list

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        -> Test No Context
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=None, pos=[10,10])
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Entity Ceased to Exist
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), pos=[10,10], _ent_pos=None)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position Not Reached in Time
            >>> cmd_ctx_mock = CommandContextMock(duration=20000)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=cmd_ctx_mock, pos=[10,10], max_time_s=5)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position has been Reached
            >>> _ent_pos_mock = PositionMock(x=608, y=608)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), pos=[10,10], proximity_px=20, _ent_pos=_ent_pos_mock)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Target Position has not been Reached
            >>> _ent_pos_mock = PositionMock(x=91, y=120)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), pos=[10,10], _ent_pos=_ent_pos_mock, _last_dir_change = 50)
            <CommandStatus.RUNNING: 'RUNNING'>
    '''

    logger.debug(f'Moving to path point {_path[_path_idx]} -> {(_path[_path_idx][0], _path[_path_idx][1])}')

    res = cmd_move_to_pos_tile_vect(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            cmd_ctx=cmd_ctx,
            # 'Public' attributes specific to this command and used while calling the command
            pos=(_path[_path_idx][0], _path[_path_idx][1]),
            #max_time_s=None,
            dt_comp=dt_comp,
            absolute=absolute,
            # 'Private' attributes that have been prepared by init function
            _ent_pos=_ent_pos,
            #_last_dir_change=0,
            #_move_axis=,
            # The rest of parameters, if needed
            **cmd_kwargs
        )
    
    # In case moving to the next tile succeeds - move to the next tile in the path and return RUNNING
    if res == CommandStatus.SUCCESS:
        logger.debug(f'Moving to tile {(_path[_path_idx][0], _path[_path_idx][1])} ended with success. My position is {_ent_pos.get_tile()}')
        # Check if we are at the end
        if _path_idx == len(_path) - 1: return CommandStatus.SUCCESS

        # New point of the path
        cmd_ctx.local_bb['_path_idx'] = _path_idx + 1
        _path_idx = _path_idx + 1 # also the local variable must be unfortunatelly updated
        logger.debug(f'Targeting to the next point {(_path[_path_idx][0], _path[_path_idx][1])} and returning running')
        
        # Init movement between new 2 points
        logger.debug(f'Calling move_to_pos_px_tile_init ...')
        cmd_move_to_pos_tile_vect_init(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            cmd_ctx=cmd_ctx,
            pos=(_path[_path_idx]),
            **cmd_kwargs
        )

        # Continue on the path with the next point
        return CommandStatus.RUNNING

    elif res == CommandStatus.FAILURE:
        logger.debug(f'Moving to tile {(_path[_path_idx][0], _path[_path_idx][1])} FAILED')

    return res

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
