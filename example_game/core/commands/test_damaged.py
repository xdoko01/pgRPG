''' Module implementing TEST_DAMAGED command 

For tests call python -m example_game.core.commands.test_damaged -v

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
    - ctx: CommandContext,      # Contains information from other commands and statistics
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
from pyrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from core.components.flag_was_damaged_by import FlagWasDamagedBy

def init(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        entities=[],
        out_bb_key=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> None:
    '''This function is called only if CommandContext is not None - i.e., in case of more
    complicated commands that require multiple cycles for processing (can return CommandStatus.RUNNING).
    It runs before the first cycle of the command is executed. It is used to introduce new internal
    variables that can be used in the process() function later.
    In case that no specific steps are required before the first run of process(), pass it.

    Parameters:

        :param entities: list of entities that we want to test for damaging us - if empty, all entities are taken into account
        :type entities: list

        :param out_bb_key: blackboard key to which to write the entity that is attacking us last (optional)
        :type out_bb_key: str
    '''
    pass # Empty as we need to perform the check for FlagWasDamagedBy every time in process part of the code


# DO NOT REMOVE - Mandatory function
def process(
        # Mandatory attributes that must be always present
        ecs_mng: ModuleType,
        entity_id: int,
        ctx: CommandContext,
        # 'Public' attributes specific to this command and used while calling the command
        entities=[],
        out_bb_key=None,
        # The rest of parameters, if needed
        **cmd_kwargs
    ) -> CommandStatus:
    ''' Move to the target entity position using the path.

    This function represents the body of the command. It can be executed once and 
    finish with the CommandStatus.SUCCESS or ComandStatus.FAILURE, or can be called
    several times in case that CommandStatus.RUNNING is returned. The process() function
    can use 'private' attributes that have been prepared in the init() function. Those
    'private' attributes are passed to it by CommandManager.

    Parameters:
        :param entities: list of entities that we want to test for damaging us - if empty, all entities are taken into account
        :type entities: list

        :param out_bb_key: blackboard key to which to write the entity that is attacking us last (optional)
        :type out_bb_key: str
        
        :returns: CommandStatus
    '''

    # Comment out, if you want see the stats about the command
    #logger.debug(f'{ctx=}')

    # Check existence of component FlagWasDamagedBy
    flag_was_damaged_by_comp = ecs_mng.try_component(entity_id, FlagWasDamagedBy) # must not be in init we need to check everytime

    if flag_was_damaged_by_comp: 

        # What entities we are monitoring as possible damage source. If empty, all entities are possible damage source.
        tested_damage_sources = set(entities) if entities else flag_was_damaged_by_comp.entities

        # What entities are causing damage - resulting set of entities
        damage_source_entities = tested_damage_sources.intersection(flag_was_damaged_by_comp.entities)

        # Was damaged by the specific entity
        if damage_source_entities:
            logger.debug(f'{entity_id=}. Entity was damaged by {damage_source_entities=} entities.')

            # Record on the global blackboard, if wanted
            if out_bb_key is not None:
                damage_source =  damage_source_entities.pop() # can take of possibly many
                ctx.globals.add(out_bb_key, damage_source) # can be one of many

            logger.debug(f'{entity_id=}. Recorded on blackboard {out_bb_key=}, {damage_source=}.')

            return CommandStatus.SUCCESS
    
    return CommandStatus.FAILURE

    '''
    # Check if Damageable component still exists - if not return FAILURE
    if not ctx.locals._damageable_comp: 
        logger.debug(f'{entity_id=}. Entity does not have Damageable componment. Ending with FAILURE.')
        return CommandStatus.FAILURE

    # Check if entity is damaged by some other component
    if len(ctx.locals._damageable_comp.damages) > 1: # some damage must be recorded

        damage = ctx.locals._damageable_comp.damages[-1] # take the last damage recorded

        if out_bb_key is not None: # put it on the blackboard if wanted
            damage_source = damage.parent if damage.parent else damage.entity
            ctx.globals.add(out_bb_key, damage_source) # record parent if exists (shooter, not arrow)

        logger.debug(f'{entity_id=}. Entity {damage_source=} was attacking. Ending with SUCCESS.')
        return CommandStatus.SUCCESS

    # If not damaged, end with FAILURE
    return CommandStatus.FAILURE
    '''
    
if __name__ == '__main__':

    # Prepare the mocs
    #def raise_mock(exception): raise exception

    # Run the tests
    import doctest
    doctest.testmod()
