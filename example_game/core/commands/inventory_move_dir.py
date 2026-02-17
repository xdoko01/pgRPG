''' Module implementing INVENTORY_MOVE_DIR command 

For tests call python -m example_game.core.commands.inventory_move_dir -v

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
from core.components.flag_show_inventory import FlagShowInventory # To work with components in commands (remove search add ...)

# DO NOT REMOVE - Mandatory function
def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        move: str,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:
        :param move: String 'left', 'right', 'up' or 'down'
        :type move: str

        :returns: None

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(), move='left')
    '''
    pass

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        move: str,
        dt_comp=True,
        absolute=False,
        # 'Private' attributes that have been prepared by init function
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move to specified direction ('up', 'down', 'left', 'right').

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param move: String 'left', 'right', 'up' or 'down'
        :type move: str

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        -> Test Movement Successful
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock(), move='left')
            <CommandStatus.SUCCESS: 'SUCCESS'>
        
        -> Test Missing Argument Moves
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock())
            Traceback (most recent call last):
            ...
            TypeError: process() missing 1 required positional argument: 'move'
    '''

    # Comment out, if you want see the stats about the commandd
    logger.debug(f'{ctx=}')

    # Get the FlagShowInventory component. If does not exists then no move can be done (no inventory shown) and it is a FAILURE
    flag_show_inventory = ecs_mng.try_component(entity_id, FlagShowInventory)
    
    if flag_show_inventory is None:
        return CommandStatus.FAILURE

    # Calculate the index offset based on the move
    idx_shifts = {'LEFT': -1, 'RIGHT': +1, 'UP': -flag_show_inventory.slots_per_row, 'DOWN': +flag_show_inventory.slots_per_row}

    # Move to the new selected slot id - make sure that selected_slot_id is never out of bounds
    move = move.upper()
    flag_show_inventory.selected_slot_id = flag_show_inventory.selected_slot_id + idx_shifts[move]

    # Ensures that slot_id is never below 0
    flag_show_inventory.selected_slot_id = max(0, flag_show_inventory.selected_slot_id)

    # Ensures that slot_id is newer above max number of slots
    flag_show_inventory.selected_slot_id = min(flag_show_inventory.inventory_comp.max_items-1, flag_show_inventory.selected_slot_id)
    
    return CommandStatus.SUCCESS


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
