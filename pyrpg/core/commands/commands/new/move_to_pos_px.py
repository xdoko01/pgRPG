''' Module implementing MOVE_TO_POS_PX command 

For tests call python -m pyrpg.core.commands.commands.new.move_to_pos_px -v

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
import typing
from pyrpg.core.ecs.components.new.position import Position, PositionMock # To work with components in commands (remove search add ...)
from .move_dir import process as cmd_move_dir # import other existing command

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
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
        >>> cmd_ctx_mock = CommandContextMock(local_bb={})
        >>> ecs_mng_mock = ECSManagerMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=cmd_ctx_mock)
    '''
    # Additional parameters that can be used in the command
    cmd_ctx.local_bb['_ent_pos'] = ecs_mng.component_for_entity(entity_id, Position)
    cmd_ctx.local_bb['_last_dir_change'] = 0
    cmd_ctx.local_bb['_move_axis'] = None
    
    logger.debug(f'Locals initiated: {cmd_ctx.local_bb=}')

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        pos,
        proximity_px=10,
        max_time_s=None,
        change_dir_ms=1000,
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        _ent_pos=None,
        _last_dir_change=None,
        _move_axis=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    '''Move entity to the position defined by px or tile coordinates.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param pos: Target position in px
        :type pos: list

        :param proximity_px: How far from the target position to stop
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

        :param _last_dir_change: Private attribute holding time when the direction was last changed.
        :type _last_dir_change: int

        :param _move_axis: Private attribute keeping direction of current movement.
        :type _move_axis: str (X,Y)

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        -> Test No Context
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=None, pos=[100,100])
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Entity Ceased to Exist
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), pos=[100,100], _ent_pos=None)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position Not Reached in Time
            >>> cmd_ctx_mock = CommandContextMock(duration=20000)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=cmd_ctx_mock, pos=[100,100], max_time_s=5)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position has been Reached
            >>> _ent_pos_mock = PositionMock(x=91, y=105)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), pos=[100,100], _ent_pos=_ent_pos_mock)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Target Position has not been Reached
            >>> _ent_pos_mock = PositionMock(x=91, y=120)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), pos=[100,100], _ent_pos=_ent_pos_mock, _last_dir_change = 50)
            <CommandStatus.RUNNING: 'RUNNING'>
    '''

    # Comment out, if you want see the stats about the command
    #logger.debug(f'{cmd_ctx=}')

    # Command must run with context, else does not make sense
    assert cmd_ctx is not None, f'Command cannot run without context.'

    # Check if entity has still position component, if not finish
    if _ent_pos is None:
        logger.debug(f'Entity component reference is lost, returning failure.')
        return CommandStatus.FAILURE

    # Check, if we are not moving to the point for too long
    if max_time_s is not None and cmd_ctx.duration > max_time_s*1000: 
        logger.debug(f'Max time for movement is up. Returning failure.')
        return CommandStatus.FAILURE

    x, y = pos # for readibility

    # Check, if the distance is closed finish with SUCCESS
    if abs(y - _ent_pos.y) < proximity_px and abs(x - _ent_pos.x) < proximity_px:
        logger.debug(f'Target position {x}, {y} reached with {proximity_px=}')
        return CommandStatus.SUCCESS

    # Check, if it is time to change the direction
    if cmd_ctx.current_time - _last_dir_change >= change_dir_ms:
        cmd_ctx.local_bb['_last_dir_change'] = cmd_ctx.current_time

        logger.debug(f'Changing direction after {change_dir_ms=}')

        # Decide on which axis we will be closing the gap - close the smaller gap
        if abs(x - _ent_pos.x) > abs(y - _ent_pos.y):
            cmd_ctx.local_bb['_move_axis'] = 'X'
        else:
            cmd_ctx.local_bb['_move_axis'] = 'Y'

    # Continue movement
    if _move_axis == 'X':
        # use existing command
        cmd_move_dir(
            ecs_mng=ecs_mng, 
            entity_id=entity_id, 
            cmd_ctx=None, 
            moves=['left' if x - _ent_pos.x < 0 else 'right' if x - _ent_pos.x > 0 else 'right'],
            dt_comp=dt_comp,
            absolute=absolute
        )
    else:
        cmd_move_dir(
            ecs_mng=ecs_mng, 
            entity_id=entity_id, 
            cmd_ctx=None, 
            moves=['up' if y - _ent_pos.y < 0 else 'down' if y - _ent_pos.y > 0 else 'down'],
            dt_comp=dt_comp,
            absolute=absolute
        )

    return CommandStatus.RUNNING


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
