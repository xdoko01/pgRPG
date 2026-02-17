''' Module implementing ARM_AMMO command 

For tests call python -m example_game.core.commands.arm_ammo -v

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
from core.components.flag_is_about_to_arm_ammo import FlagIsAboutToArmAmmo
from core.components.has_weapon import HasWeapon
from core.components.ammo_pack import AmmoPack
from core.components.factory import Factory

# DO NOT REMOVE - Mandatory function
def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        ammo_entity_id: int,
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
        ammo_entity_id: int,
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

    # Entity (figher - probably player or NPC) must have HasWeapon component in order to successfully arm the ammo
    has_weapon: HasWeapon = ecs_mng.try_component(entity_id, HasWeapon)

    # If Entity (figher) does not have HasWeapon component then it cannot arm any ammo - FAILURE
    if has_weapon is None: return CommandStatus.FAILURE

    ''' Handled while processing FlagIsAboutToArmWeapon
    # Before arming the weapon, you must disarm the currently armed weapon if there is any
    armed_weapon_entity_id = has_weapon.weapons[weapon_type]["weapon"]

    if armed_weapon_entity_id is not None:
            ecs_mng.add_component(entity_id, FlagIsAboutToDisarmWeapon(weapon=armed_weapon_entity_id, type=weapon_type))
            logger.debug(f'{entity_id=} - component FlagIsAboutToDisarmWeapon created with params {armed_weapon_entity_id=}, {weapon_type=}.')

    # Also, you need to disarm te weapon that entity is currently using
    weapon_in_use: WeaponInUse = ecs_mng.try_component(entity_id, WeaponInUse)
    weapon_in_use_entity_id = has_weapon.weapons[weapon_in_use.type]["weapons"]
    
    if weapon_in_use_entity_id is not None:
            ecs_mng.add_component(entity_id, FlagIsAboutToDisarmWeapon(weapon=weapon_in_use_entity_id, type=weapon_in_use.type))
            logger.debug(f'{entity_id=} - component FlagIsAboutToDisarmWeapon created with params {weapon_in_use_entity_id=}, {weapon_in_use.type=}.')
    '''
    # If Entity (ammo) must have AmmoPack and Factory components - FAILURE
    ammo: AmmoPack = ecs_mng.try_component(ammo_entity_id, AmmoPack)
    factory: Factory = ecs_mng.try_component(ammo_entity_id, Factory)
    if ammo is None or factory is None: return CommandStatus.FAILURE

    # Create FlagIsAboutToArmAmmo component to the entity (probably player or NPC)
    ecs_mng.add_component(
         entity_id, 
         FlagIsAboutToArmAmmo(
              ammo=ammo_entity_id, 
              weapon=ammo.weapon, 
              type=ammo.type, 
              total_units=factory.max_units,
              used_units=factory.current_units
            )
    )
    logger.debug(f'{entity_id=} - component FlagIsAboutToArmAmmo created with params {ammo_entity_id=}, {ammo.weapon=}, {ammo.type=}, {factory.max_units=}, {factory.current_units=}.')

    # Processor PerformArmAmmo now arms the weapon

    # Return success
    return CommandStatus.SUCCESS


if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
