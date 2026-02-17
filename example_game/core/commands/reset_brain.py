''' Module implementing RESET_BRAIN command 

For tests call python -m example_game.core.commands.reset_brain -v

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
from types import ModuleType # for type hint on importing the ecs_manager module
from pgrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from core.components.brain_ai import BrainAI # To work with components in commands (remove search add ...)

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

        :returns: None

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock
        >>> ctx_mock = CommandContextMock()

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock)
        >>> print(ctx_mock.locals)
        {}
    '''
    pass

def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        new_ai_struct={},
        # 'Private' attributes that have been prepared by init function
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    '''Resets the AI of the entity with the new commands and logic passed
    in the new_ai_struct parameter.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.


    Parameters:
        :param new_ai_struct: New AI structure with commands and logic
        :type new_ai_struct: dict

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock
        >>> from core.components.brain_ai import BrainAIMock

        >>> ctx_mock = CommandContextMock()
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=ctx_mock)

        Run tests:
        ----------
        -> Test Only Reset to No Brain 
            >>> ecs_mng_mock = ECSManagerMock()
            >>> ecs_mng_mock.component_for_entity = lambda e,c: BrainAIMock()
            >>> process(ecs_mng=ecs_mng_mock, entity_id=1, ctx=None)
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Only Reset to Some Brain 
            >>> process(ecs_mng=ecs_mng_mock, entity_id=1, ctx=None, new_ai_struct={})
            <CommandStatus.SUCCESS: 'SUCCESS'>

        -> Test Entity does not have BrainAI Component 
            >>> ecs_mng_mock.component_for_entity = lambda e,c: raise_mock(KeyError)
            >>> process(ecs_mng=ecs_mng_mock, entity_id=1, ctx=None)
            <CommandStatus.FAILURE: 'FAILURE'>
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{ctx=}, {new_ai_struct=}')

    try:
        brain = ecs_mng.component_for_entity(entity_id, BrainAI)
        brain.generator.reset(new_ai_struct)
        logger.debug(f'{entity_id=} - new commands added to the brain {brain}.')
        return CommandStatus.SUCCESS
    except KeyError:
        return CommandStatus.FAILURE

if __name__ == '__main__':

    # Prepare the mocs
    def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
