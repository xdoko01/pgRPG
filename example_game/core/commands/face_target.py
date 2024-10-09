''' Module implementing FACE_TARGET command 

For tests call python -m pyrpg.core.commands.commands.new.face_target -v

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
from core.components.flag_do_move import FlagDoMove # To work with components in commands (remove search add ...)
from core.components.position import Position

sign = lambda x: -1 if x<0 else (1 if x>0 else 0)

# DO NOT REMOVE - Mandatory function
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
        :param target: Entity id of the target
        :type target: int

        :returns: None

    Tests:

        Prepare mocs:
        -------------
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(), moves=['left', 'up'])
    '''

    logger.debug(f'{entity_id=}. Starting init')

    # Add new locals - position component of the target and the entity
    ctx.locals.add('_tar_pos', ecs_mng.try_component(target, Position))
    ctx.locals.add('_ent_pos', ecs_mng.try_component(entity_id, Position))
    
    logger.debug(f'{entity_id=}. Locals initiated: {ctx.locals=}')


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        target,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Set entity to face towards the target entity.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param target: Entity id of the target
        :type target: int

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pyrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pyrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        -> Test Movement Successful
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(), moves=['left'])
            <CommandStatus.SUCCESS: 'SUCCESS'>
        
        -> Test Missing Argument Moves
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock())
            Traceback (most recent call last):
            ...
            TypeError: process() missing 1 required positional argument: 'moves'
    '''

    # Comment out, if you want see the stats about the commandd
    logger.debug(f'{ctx=}')

    # Command must run with context, else does not make sense
    assert ctx is not None, f'Command cannot run without context.'

    # Check if target still exists
    if ctx.locals._tar_pos is None or ctx.locals._ent_pos is None:
        logger.debug(f'Target or Entity position component reference is lost, returning failure.')
        return CommandStatus.FAILURE

    # Calculate the vector between target and entity

    # if possitive, pos_entity must face Right
    x_dir = ctx.locals._tar_pos.x - ctx.locals._ent_pos.x
    # if positive, pos_entity must face Down
    y_dir = ctx.locals._tar_pos.y - ctx.locals._ent_pos.y

    if abs(x_dir) > abs(y_dir): # turn left or right
        vect = (sign(x_dir), 0)
    else:
        vect = (0, sign(y_dir)) # turn up or down

    logger.debug(f'{x_dir=}, {y_dir=}, {vect=}')

    # Move one pixel (absolute=True) and effectively change the facing direction
    ecs_mng.add_component(entity_id, FlagDoMove(vector=vect, absolute=True))

    logger.debug(f'{entity_id=}. Now facing the target {target=}')

    return CommandStatus.SUCCESS


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
