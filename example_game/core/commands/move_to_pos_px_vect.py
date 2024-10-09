''' Module implementing MOVE_TO_POS_PX_VECT command 

For tests call python -m pyrpg.core.commands.commands.new.move_to_pos_px_vect -v

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
from .move_vect import process as cmd_move_vect # import other existing command
from math import sqrt

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        ctx: CommandContext,
        pos,
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
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(), pos=[100,100])
    '''
    # Additional parameters that can be used in the command
    pos_comp = ecs_mng.component_for_entity(entity_id, Position)
    x, y = pos
    vect = ((x - pos_comp.x), (y - pos_comp.y))
    l = sqrt(vect[0]*vect[0] + vect[1]*vect[1])

    ctx.locals.add('_norm_vect', (vect[0]/l, vect[1]/l))
    ctx.locals.add('_ent_pos', pos_comp)

    logger.debug(f'Locals initiated: {ctx.locals=}')

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        pos,
        max_time_s=None,
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        #_ent_pos=None,
        #_norm_vect=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    '''Move entity to the position defined by px coordinates by going directly, not
    limited to 4 directions.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param pos: Target position in px
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
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=None, pos=[100,100])
            Traceback (most recent call last):
            ...
            AssertionError: Command cannot run without context.

        -> Test Entity Ceased to Exist
            >>> ctx_mock.locals.add("_ent_pos", None)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[100,100])
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position Not Reached in Time
            >>> ctx_mock.duration = 20000
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[100,100], max_time_s=5)
            <CommandStatus.FAILURE: 'FAILURE'>

        -> Test Target Position has been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=98, y=102))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[100,100])
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Target Position has not been Reached
            >>> ctx_mock.locals.add("_ent_pos", PositionMock(x=91, y=120))
            >>> ctx_mock.locals.add("_norm_vect", (0,1))
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock, pos=[100,100])
            <CommandStatus.RUNNING: 'RUNNING'>
    '''

    # Comment out, if you want see the stats about the command
    #logger.debug(f'{cmd_ctx=}')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'

    # Check if entity has still position component, if not finish
    if ctx.locals._ent_pos is None:
        logger.debug(f'Entity component reference is lost, returning failure.')
        return CommandStatus.FAILURE

    # Check, if we are not moving to the point for too long
    if max_time_s is not None and ctx.duration > max_time_s*1000: 
        logger.debug(f'Max time for movement is up. Returning failure.')
        return CommandStatus.FAILURE

    x, y = pos # for readibility

    # Calc the vector between entity position and target position
    vect = ((x - ctx.locals._ent_pos.x), (y - ctx.locals._ent_pos.y))

    # Check, if the distance is closed finish with SUCCESS
    if abs(vect[0]) < 3 and abs(vect[1]) < 3:
        #Close the gap
        #_ent_pos.x = x
        #_ent_pos.y = y

        logger.debug(f'Target position {x}, {y} reached.')
        return CommandStatus.SUCCESS

    # Continue movement
    cmd_move_vect(
        # Mandatory attributes that must be always present
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        # 'Public' attributes specific to this command and used while calling the command
        vector=ctx.locals._norm_vect,
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
