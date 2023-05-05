import pygame # for passing current time as parameter of command
import logging
import pyrpg.core.commands as commands

from importlib import import_module
from pyrpg.core.config.paths import COMMAND_MODULE_PATH
from pyrpg.core.ecs.esper import World

# Create logger
logger = logging.getLogger(__name__)

# Keys that are used to pass information to every command
CMD_GLOBAL_KEYS = ['current_time', 'keys', 'events', 'world', 'entity', 'brain']

class CommandManager:

    def __init__(self) -> None:

        self._command_queue = []
        self._commands = {}
        logger.info(f'CommandManager initiated.')

    def register_command(self, fnc, alias) -> None:
        '''Registers new command in CommandManager under some
        specific name.
        It is called from command module initialize function.
        '''
        self._commands.update({alias: fnc})
        logger.info(f'Command function name: {alias} registered at CommandManager.')

    def get_commands(self) -> list:
        ''' Returns commands contained in the command queue.'''
        return self._command_queue

    def add_command(self, cmd: tuple) -> int:
        ''' Adds single command (tuple) to the command queue

            :param cmd: Command (tuple or list with 2 items)
            :returns: 0 on success
        '''
        try:
            cmd_fnc, cmd_params = cmd
            self._command_queue.append((cmd_fnc, cmd_params))
            logger.debug(f'Command "{cmd_fnc}" added.')
            return 0
        except ValueError:
            raise

    def clear_commands(self) -> None:
        ''' Deletes all commands from the command queue.'''

        del self._command_queue[:]
        logger.info(f'All commands cleared.')

    def execute_command(self, command_module_name: str, *cmd_args, **cmd_kwargs):
        '''Executes command and returns the result'''
        
        # Check if command module is already registered
        command_fnc = self._commands.get(command_module_name, None)

        # Register the command
        if not command_fnc:

            command_module_path_absolute = COMMAND_MODULE_PATH + command_module_name

            # Try to find the command module and get its reference
            try:
                command_module = import_module(command_module_path_absolute)
            except ValueError:
                logger.error(f'Error during loading of command module "{command_module_path_absolute}".')
                raise ValueError(f'Error during loading of command module "{command_module_path_absolute}".')

            # Try to register the script
            try:
                command_module.initialize(self.register_command, command_module_name)
            except ValueError:
                logger.error(f'Error during initiating/registering of command "{command_module_path_absolute}".')
                raise ValueError(f'Error during initiating/registering of command module "{command_module_path_absolute}".')

            # Get the command function
            command_fnc = self._commands.get(command_module_name)
        
        # Run the script
        return command_fnc(*cmd_args, **cmd_kwargs)

    def process_commands(self, alias_to_entity_fnc, world: World=None, ecs_mng=None, keys=None, events=None) -> None:
        ''' Process game commands. It is called by CommandsProcessor.
        Processes the command_queue.
        '''

        # Process every command in the queue
        while self._command_queue:

            # pop out command from the beginning of the queue
            command = self._command_queue.pop(0)

            (cmd_fnc, cmd_params) = command

            # Add current time to the parameters
            cmd_params.update({'current_time' : pygame.time.get_ticks()})

            # Add reference to pressed keys and keyboard/mouse events to the parameters of md
            cmd_params.update({'keys' : keys})
            cmd_params.update({'events' : events})

            # Add reference to the game world so that command can 'see' the world objects
            cmd_params.update({'world' : world})
            cmd_params.update({'ecs_mng' : ecs_mng})

            # Check if in cmd_params there is entity parameter that is not an integer but a string.
            # Such commands can be submitted by the global script processor Brain
            entity_id = cmd_params.get('entity')
            if isinstance(entity_id, str): cmd_params.update({'entity' : alias_to_entity_fnc(entity_id)})

            brain = cmd_params.get("brain", None)

            # Execute the command - command is a text hence need to get reference to command func. first
            # result = cmd_fnc(**cmd_params) # originally, this was called when command fnc was reference to the fnc
            # If command is not recognized by the command module, none command function is returned
            #result = commands.get_cmd_fnc(cmd_fnc)(**cmd_params)

            result = self.execute_command(cmd_fnc, **cmd_params)
            logger.debug(f'Command "{cmd_fnc}" with parameters {cmd_params} executed with status {result}.')

            if brain: brain.process_result(result)
