import logging

#from importlib import import_module
from pyrpg.functions import str_to_package_module
from pyrpg.core.config.paths import COMMAND_MODULE_PATH
from pyrpg.core.ecs.esper import World

from pyrpg.core.commands import CommandGenerator, Command, CommandContext

# Create logger
logger = logging.getLogger(__name__)


class CommandManager:

    def __init__(self) -> None:
        self._command_queue = []
        self._commands = {}
        logger.info(f'CommandManager initiated.')

    def get_command_queue(self) -> list:
        ''' Returns commands contained in the command queue.'''
        return self._command_queue

    def clear_command_queue(self) -> None:
        ''' Deletes all commands from the command queue.'''

        del self._command_queue[:]
        logger.info(f'All commands cleared from the queue.')

    def add_command(self, cmd: Command, orig_entity_id: int, generator: CommandGenerator=None) -> None:
        ''' Adds single command (tuple) to the command queue. Can be called also from the console for
        the ad hoc commands that do not originate from any context.

            :param cmd: Command is tuple or list with 2 items - name(str) and parameters(dict)
            :type cmd: Command

            :param orig_entity_id: Number of the entity that has generated the command (owner of Brain, Controllable)
                                    or other component.
            :type orig_entity_id: int

            :param generator: Reference to instance of CommandGenerator class. When command is processed, the generator
                              must be notified about the result of the command in order to generate the proper wanted
                              next command (check process_commands method).
            :type generator: CommandGenerator
        '''

        if cmd is None: return # ignore empty commands

        cmd_fnc, cmd_params = cmd # comand has name and parameters in form of dictionary

        # Use entity_id from parameters, if not exists, use entity of the brain owner
        # Remove entity from command parameters
        entity_id = cmd_params.pop("entity", orig_entity_id)

        # Make sure that entity_id is an integer and not a string. Entity_id should be translated
        # from entity on component creation level.
        # Translation is performed in ECSManager.create_component_from_def function
        assert isinstance(entity_id, int), f'Here entity should be already translated, but ut us not.'

        self._command_queue.append(((cmd_fnc, cmd_params), entity_id, generator))
        logger.debug(f'Command "{(cmd_fnc, cmd_params)=}", "{entity_id=}", "{generator=}" added to the command queue.')

    def _register_command(self, fnc, alias) -> None:
        '''Registers new command in CommandManager under some
        specific name.
        It is called from command module initialize function.
        '''
        self._commands.update({alias: fnc})
        #TODO this is called always which is wrong!!!
        logger.info(f'Command function name: {alias} registered at CommandManager.')

    def register_command(self, command_module_name: str):
        '''Returns the registered command function if registered. Else register it first.'''

        command_module_path_absolute = COMMAND_MODULE_PATH + command_module_name

        # Try to find the command module and get its reference
        try:
            #command_module = import_module(command_module_path_absolute)
            command_module = str_to_package_module(None, command_module_path_absolute)

        except ValueError:
            logger.error(f'Error during loading of command module "{command_module_path_absolute}".')
            raise ValueError(f'Error during loading of command module "{command_module_path_absolute}".')

        # Try to register the script
        try:
            command_module.initialize(self._register_command, command_module_name)
        except ValueError:
            logger.error(f'Error during initiating/registering of command "{command_module_path_absolute}".')
            raise ValueError(f'Error during initiating/registering of command module "{command_module_path_absolute}".')

        return self._commands.get(command_module_name)

    def get_command(self, command_module_name):
        '''Gets the command module from the storage if registered or register it first'''
        logger.debug(f'Command module search in the _commands {self._commands.get(command_module_name, "NOT FOUND")}')
        command_module = self._commands.get(command_module_name)
        return command_module if command_module is not None else self.register_command(command_module_name)

    def execute_command(self, ecs_mng, entity_id: int, cmd_ctx: CommandContext, command_module_name: str, *cmd_args, **cmd_kwargs):
        '''Executes command and returns the result
            
            This function should not be called directly from the console if the player
            wants to execute some ad hoc command. It must be always called from process_commands function
            that will deliver the necessary ecs_mng object that is necessary for every command.

            From console probably CommandManager.add_command(command) would need to be called. This will add the
            command to the queue and consequently processes the command in the next run of the PerformCommand 
            processor.
        '''

        command_fnc = self.get_command(command_module_name)

        # Run the command function
        return command_fnc(ecs_mng, entity_id, cmd_ctx, *cmd_args, **cmd_kwargs)

    def process_commands(self, ecs_mng, keys=None, events=None) -> None:
        ''' Process game commands. It is called by CommandsProcessor.
        Processes the command_queue.
        '''

        # Process every command in the queue
        while self._command_queue:

            # pop out command from the beginning of the queue
            command = self._command_queue.pop(0)

            ((cmd_fnc, cmd_params), entity_id, generator) = command

            # In case that command is generated by the generator and not ad hoc from the console
            # update the generator based on the command result.
            if generator is not None:
                generator.command_starts() # CommandGenerator calculates the statistics on cmd_ctx
                result = self.execute_command(ecs_mng=ecs_mng, entity_id=entity_id, cmd_ctx=generator.bb, command_module_name=cmd_fnc, **cmd_params)
                generator.process_command_result(result) # Callback result to the generator to modify its state
            else:
                # commands without context - ad hoc from console
                self.execute_command(ecs_mng=ecs_mng, entity_id=entity_id, cmd_ctx=None, command_module_name=cmd_fnc, **cmd_params)
