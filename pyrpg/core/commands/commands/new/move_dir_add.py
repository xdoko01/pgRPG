''' Module implementing command XXX

One module can implement many commands - many functions. Each such command must be registered within
the initialize function under its own name in order to invoke it from the game.

One command can be theoretically registered under more than one name however it is not recommended.

Every command function must have the following parameters:

def example_cmd_fnc(
        ecs_mng: ECSManager,      # Provides all necessary tools for manipulating the game world
        entity_id: int,           # Game world entity to which the command should be applied
        cmd_ctx: CommandContext,  # Contains information from other commands and statistics
        *cmd_args, **cmd_kwargs   # Command parameters
    ) -> CommandStatus:
'''

######## INIT PART

### Include if logging of command is required
import logging
logger = logging.getLogger(__name__)

### Mandatory registration function - DO NOT REMOVE
def initialize(register, module_name):
    '''Command registers itself at CommandManager under specific name
    that will be used to call the command.'''
    register(fnc=cmd_move_dir_add, alias=module_name)  # mandatory register the command under the name of the module
    #register(fnc=cmd_new_move_add, alias="move_add")  # optionally, register under some different name

######## COMMAND(S) PART

### Mandatory imports, DO NOT REMOVE
from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.commands import CommandContext, CommandStatus

### Optional imports
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove # To work with components in commands (remove search add ...)

def cmd_move_dir_add(
        ecs_mng: ECSManager,      # Provides all necessary tools for manipulating the game world
        entity_id: int,           # Game world entity to which the command should be applied
        cmd_ctx: CommandContext,  # Contains information from other commands and statistics
        #*cmd_args, **cmd_kwargs   # Command parameters
        moves # list ov movements
    ) -> CommandStatus:
    ''' Move to specified direction ('up', 'down', 'left', 'right').
    Move command that supports adding moves to already existing
    moves and hence constructs FlagDoMove entity from multiple commands.
    Typical example is pressing 'up' + 'left' at the same time which results
    in moving diagonaly in case this command is used.

    Command Params:
        :param moves: List of moves
        :type moves: list

    Returns:
        SUCCESS - ALWAYS
        FAILURE - NEVER
        RUNNING - NEVER
    
    Summary of Steps:
        - get FlagDoMove entity and add more movement to it if exists
        - if not exists, create a new movement entity
    '''

    # Comment out, if you want see the stats about the command
    logger.debug(f'{cmd_ctx=}')

    try:
        flag_do_move = ecs_mng.component_for_entity(entity_id, FlagDoMove)
        flag_do_move.add_moves(moves)
        logger.debug(f'{entity_id=} - moves added to already existing component {flag_do_move}.')
    except KeyError:
        new_component = FlagDoMove(moves=moves) # Create new FlagDoMove component
        ecs_mng.add_component(entity_id, new_component)
        logger.debug(f'{entity_id=} - new component created {new_component}.')

    return CommandStatus.SUCCESS
