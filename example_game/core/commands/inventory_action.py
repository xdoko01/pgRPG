''' Module implementing INVENTORY_ACTION command 

For tests call python -m example_game.core.commands.inventory_action -v

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
from core.components.has_inventory import HasInventory
from core.components.weapon import Weapon
from core.components.ammo_pack import AmmoPack
from core.components.factory import Factory

from .arm_weapon import process as cmd_arm_weapon
from .arm_ammo import process as cmd_arm_ammo
from .use_weapon import process as cmd_use_weapon


# DO NOT REMOVE - Mandatory function
def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
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
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        >>> init(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock())
    '''
    pass

# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        # 'Private' attributes that have been prepared by init function
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    '''
    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:

        :returns: CommandStatus

    Tests:

        Prepare mocs:
        -------------
        >>> from pgrpg.core.managers.ecs_manager import ECSManagerMock
        >>> from pgrpg.core.commands import CommandContextMock

        Run tests:
        ----------
        -> Test Movement Successful
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock())
            <CommandStatus.SUCCESS: 'SUCCESS'>
        
        -> Test Missing Argument Moves
            >>> process(ecs_mng=ECSManagerMock(), entity_id=1, ctx=CommandContextMock())
            Traceback (most recent call last):
            ...
            TypeError: process() missing 1 required positional argument: 'move'
    '''

    # Comment out, if you want see the stats about the commandd
    logger.debug(f'{ctx=}')

    # Get the FlagShowInventory component. If does not exists then no inventory action can be done (no inventory shown) and it is a FAILURE
    flag_show_inventory: FlagShowInventory = ecs_mng.try_component(entity_id, FlagShowInventory)
    has_inventory: HasInventory = ecs_mng.try_component(entity_id, HasInventory)

    if flag_show_inventory is None or has_inventory is None:
        logger.debug(f'{entity_id=} - component FlagShowInventory or HasInventory do not exist, failure.')
        return CommandStatus.FAILURE

    # Get the entity_id of the selected inventory item
    inv_item_entity_id = has_inventory.slots[flag_show_inventory.selected_slot_id]
    
    # In case focus is on empty slot without any entity/item - return failure
    if inv_item_entity_id is None:
        logger.debug(f'{entity_id=} - No entity in the slot, failure.')
        return CommandStatus.FAILURE

    # Try arming the entity using arm_command
    arm_weapon_res: CommandStatus = cmd_arm_weapon(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        weapon_entity_id=inv_item_entity_id,
        **cmd_kwargs
    )
    logger.debug(f'{entity_id=} - Command arm_weapon result: {arm_weapon_res=}')

    """
    # Try switching the weapon for usage if arming was successful
    if arm_weapon_res == CommandStatus.SUCCESS: 
        weapon: Weapon = ecs_mng.try_component(inv_item_entity_id, Weapon) # if arming was successful, Weapon component exists

        use_weapon_res: CommandStatus = cmd_use_weapon(
            ecs_mng=ecs_mng,
            entity_id=entity_id,
            ctx=ctx,
            weapon_type=weapon.type
        )
        logger.debug(f'{entity_id=} - Command use_weapon result: {use_weapon_res=}')
    """

    # Try arming the entity using arm_ammo
    arm_ammo_res: CommandStatus = cmd_arm_ammo(
        ecs_mng=ecs_mng,
        entity_id=entity_id,
        ctx=ctx,
        ammo_entity_id=inv_item_entity_id,
        **cmd_kwargs
    )
    logger.debug(f'{entity_id=} - Command arm_ammo result: {arm_ammo_res=}')

    # if at least one of the arming commands suceeds, return success. Otherwise, return failure.
    return CommandStatus.SUCCESS if arm_weapon_res == CommandStatus.SUCCESS or arm_ammo_res == CommandStatus.SUCCESS else CommandStatus.FAILURE


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
