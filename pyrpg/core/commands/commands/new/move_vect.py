''' Module implementing MOVE_VECT command 

For tests call python -m pyrpg.core.commands.commands.new.move_vect -v

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
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove # To work with components in commands (remove search add ...)

def init(
        # Mandatory attributes that must be always present
        # 'Public' attributes specific to this command and used while calling the command
        # The rest of parameters, if needed
        *args, **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:
        :param target: Entity_id of the target
        :type target: integer

        :returns: None

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock())
    '''
    pass

def process(
        # Mandatory attributes that must be always present
        ecs_mng: ECSManager,
        entity_id: int,
        cmd_ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        vector=[0, 0],
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move by specific vector.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param vector: Movement vector
        :type vector: list of 2 values
        :example vector: [5, 13] ... move top-right

        :param dt_comp: Should delta time (dt) correction be taken into account.
        :type dt_comp: bool

        :param absolute: Should velocity be ignored (only move by vector, not multipy by velocity).
        :type absolute: bool

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------

        Run tests:
        ----------
        -> Test Adding FlagDoMove
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, cmd_ctx=CommandContextMock(), vector=[2,2])
            <CommandStatus.SUCCESS: 'SUCCESS'>
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{cmd_ctx=}')

    new_component = FlagDoMove(vector=vector, dt_on=dt_comp, absolute=absolute) # Create new FlagDoMove component
    ecs_mng.add_component(entity_id, new_component)
    logger.debug(f'{entity_id=} - new component created {new_component}.')

    return CommandStatus.SUCCESS

if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()