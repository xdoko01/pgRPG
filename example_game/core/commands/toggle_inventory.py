''' Module implementing TOGGLE_INVENTORY command 

For tests call python -m example_game.core.commands.toggle_inventory -v

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
from core.components.flag_show_inventory import FlagShowInventory
from core.components.camera import Camera
from core.components.has_inventory import HasInventory

# DO NOT REMOVE - Mandatory function
def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        slots_per_row: int=5,
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

    '''
    pass

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        slots_per_row: int=5,
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

        :returns: CommandStatus

    Tests:

    '''

    # Comment out, if you want see the stats about the commandd
    #logger.debug(f'{ctx=}')

    # If component FlagShowInventory is present, remove it. If it is not present, add it
    if ecs_mng.try_component(entity_id, FlagShowInventory):
        ecs_mng.remove_component(entity_id, FlagShowInventory)
        logger.debug(f'{entity_id=}. FlagShowInventory removed.')

    else:
        camera_comp: Camera = ecs_mng.try_component(entity_id, Camera)
        inventory_comp: HasInventory = ecs_mng.try_component(entity_id, HasInventory)

        if camera_comp is None or inventory_comp is None: return CommandStatus.FAILURE
        
        ecs_mng.add_component(entity_id, FlagShowInventory(inventory_comp=inventory_comp, camera_comp=camera_comp, slots_per_row=slots_per_row))
        logger.debug(f'{entity_id=}. FlagShowInventory added.')

    return CommandStatus.SUCCESS


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
