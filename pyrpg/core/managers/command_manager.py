import pygame # for passing current time as parameter of command
import logging
import pyrpg.core.commands as commands

from pyrpg.core.ecs.esper import World

# Create logger
logger = logging.getLogger(__name__)

# Keys that are used to pass information to every command
CMD_GLOBAL_KEYS = ['current_time', 'keys', 'events', 'world', 'entity', 'brain']

class CommandManager:

    def __init__(self) -> None:

        self._command_queue = []
        logger.info(f'CommandManager initiated.')

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

    def process_commands(self, alias_to_entity_fnc, world: World=None, keys=None, events=None) -> None:
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

            # Check if in cmd_params there is entity parameter that is not an integer but a string.
            # Such commands can be submitted by the global script processor Brain
            entity_id = cmd_params.get('entity')
            if isinstance(entity_id, str): cmd_params.update({'entity' : alias_to_entity_fnc(entity_id)})

            brain = cmd_params.get("brain", None)

            # Execute the command - command is a text hence need to get reference to command func. first
            # result = cmd_fnc(**cmd_params) # originally, this was called when command fnc was reference to the fnc
            # If command is not recognized by the command module, none command function is returned

            result = commands.get_cmd_fnc(cmd_fnc)(**cmd_params)
            logger.debug(f'Command "{cmd_fnc}" with parameters {cmd_params} executed with status {result}.')

            if brain: brain.process_result(result)
