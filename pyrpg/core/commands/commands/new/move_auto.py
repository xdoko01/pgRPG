''' Module implementing MOVE_AUTO command 

For tests call python -m pyrpg.core.commands.commands.new.move_auto -v

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
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove, FlagDoMoveMock # To work with components in commands (remove search add ...)
from pyrpg.core.ecs.components.new.position import Position, PositionMock # To work with components in commands (remove search add ...)

# DO NOT REMOVE - Mandatory function
def init(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        duration_ms=None,
        dt_comp=True,
        absolute=False,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:
        :param duration_ms: Time of ms for auto movement to last
        :type duration_ms: int

        :param dt_comp: Should delta time correction be applied
        :type dt_comp: bool

        :param absolute: Should the velocity be ignored
        :type absolute: bool

        :returns: None

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(local_bb={}))
    '''

    # Get the direction from position of the entity
    cmd_ctx.local_bb['_ent_pos'] = ecs_mng.try_component(entity_id, Position)

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        duration_ms=None,
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        _ent_pos=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move in the current direction for some predefined amount of time.
    If not specified, move indefinetelly.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param duration_ms: Time of ms for auto movement to last
        :type duration_ms: int

        :param dt_comp: Should delta time correction be applied
        :type dt_comp: bool

        :param absolute: Should the velocity be ignored
        :type absolute: bool

        :param _ent_pos: Holding Position Component of the entity (from init)
        :type _ent_pos: Component

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> _ent_pos_mock = PositionMock(dir_name='left')

        Run tests:
        ----------
        -> Test Exception when Context is not Provided
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=None, duration_ms=1000)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Movement Should Continue
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(duration=500), duration_ms=1000, _ent_pos=_ent_pos_mock)
            <CommandStatus.RUNNING: 'RUNNING'>

        -> Test Movement Has Finished (time is up)
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(duration=1200), duration_ms=1000, _ent_pos=_ent_pos_mock)
            <CommandStatus.SUCCESS: 'SUCCESS'>

    '''

    # Comment out, if you want see the stats about the commandd
    logger.debug(f'{cmd_ctx=}')

    # Command must run with context, else does not make sense
    assert cmd_ctx is not None, f'Command cannot run without context.'

    # Continue movement if time is not yet up or no duration was specified or duration is None
    if (duration_ms is None) or (cmd_ctx.duration < duration_ms) :

        # Create new FlagDoMove component
        ecs_mng.add_component(entity_id, FlagDoMove(moves=[_ent_pos.dir_name], dt_on=dt_comp, absolute=absolute))

        # There is still some time to move - return running
        return CommandStatus.RUNNING
    else:
        # Stop auto movement
        return CommandStatus.SUCCESS


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception


    # Run the tests
    import doctest
    doctest.testmod()
