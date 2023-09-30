from enum import Enum
from typing import Protocol
from collections import namedtuple

Command = namedtuple('Command', [('name', str), ('entity', str|int), ('params', dict)])


class CommandStatus(Enum):
    '''Class representing possible statuses of the the command'''

    NONE = 'NONE'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

class CommandContext(Protocol):
    '''Requirement for information about the status of the 
    CommandGenerator.'''

    global_bb: dict
    local_bb: dict
    init_time: int
    duration: int
    tick_count: int

class CommandGenerator(Protocol):
    '''Protocol class for all data structures that can generate
    commands - trees, lists, ...'''

    bb: CommandContext

    def get_command(self) -> Command|None:
        '''Return Command based on the CommandGenerator logic.'''
        pass

    def process_command_result(self, result: CommandStatus) -> None:
        '''Callback the result of the command in order to update
        CommandGenerator internal state.'''
        pass

    def notify_command_start(self) -> None:
        '''Callback from command manager before the command starts
        in order to set the CommandContext statistics.'''
        pass

class BList(CommandGenerator):
    '''Particular CommandGenerator implementation where command
    logic is kept in a form of list and goto commands.'''

    bb: CommandContext

    def tick(self) -> Command:
        pass

    def process_result(self, result: CommandStatus) -> None:
        pass

class BTree(CommandGenerator):
    '''Particular CommandGenerator implementation where command
    logic is kept in a form of behavior tree.'''

    bb: CommandContext
    
    _root_node: BTreeNode
    _running_node: BTreeNode
    _is_finished = self.root.is_finished

    def __init__(self, json_def: dict) -> None:
        '''Read the behavior tree from dictionary'''
        pass

    def tick(self) -> Command|None:
        # If the root node is in status SUCCESS or FAILURE, do not continue as the tree has finished.
        if self._root_node.is_finished(): 
            break

        # If some node is RUNNING, execute him directly
        if self._running_node: 
            yield self._running_node.process()

        # else search for some next behavior leaf node to run and execute process function on it
        else:
            yield self._root_node.process()


class BTreeComponent(Component):
    '''ECS component holding instance of given behavior tree'''

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new BTree component.

            Parameters:
                :param blackboard: List of commands to execute
                :type blackboard: list

                :param tree: Definition of the tree in the form of dict.
                :type tree: dict
        '''
        super().__init__()

        try:
            self.command_generator = BTree(json_def=kwargs['tree'])
        except ValueError:
            # Notify component factory that initiation has failed
            raise ValueError


class GenerateBTreeProcessor(Processor):
    '''Extract command from the behavior tree and put it into command queue'''

    cmd = btree.generator.get_command()

    if cmd:
        cmd_fnc, cmd_params = cmd

        # Put the command into the queue for processing - entity and btree can be override by the command
        # itself. It is used for global scripting functionality.
        # UPDATE: If comand parameters contain entity, use the entity from the command parameters
        # else use entity from the owner of the brain component

        self.add_command_fnc(
            cmd=(cmd_fnc, cmd_params),
            entity_id=cmd_params.pop("entity", ent), # who should perform the command
            generator=btree.generator # who generated command - and who needs to be notified that command has started and about the result of the command
        )

class PerformCommandProcessor(Processor):
    # Call command handler - processing commands from the queue
    self.game_commands_handler(ecs_mng=self.ecs_mng, keys=keys, events=events)

class CommandManager:

    def add_command(self, cmd: tuple, entity_id: int, generator: CommandGenerator=None) -> None:
        ''' Adds single command (tuple) to the command queue. Can be called also from the console for
        the ad hoc commands that do not originate from any context.

            :param cmd: Command (tuple or list with 3 items)
            :returns: 0 on success
        '''
        self._command_queue.append((cmd, entity_id, generator))
        logger.debug(f'Command "{cmd = }", "{entity_id = }", "{generator =}" added to the command queue.')

    def process_commands(self, ecs_mng=None, keys=None, events=None) -> None:
        ''' Process game commands. It is called by CommandsProcessor.
        Processes the command_queue.
        '''

        # Process every command in the queue
        while self._command_queue:

            # pop out command from the beginning of the queue
            command = self._command_queue.pop(0)

            ((cmd_fnc, cmd_params), entity_id, generator) = command

            # Notify the Brain that processing of the command is starting - in order to fill the statistics on
            # the blackboard.
            if generator:
                generator.command_starts()

                # Execute command
                result = self.execute_command(ecs_mng=ecs_mng, entity_id=entity_id, cmd_ctx=generator.bb command_module_name=cmd_fnc, **cmd_params)

                # Notify the Brain (for example BTree that comand has finished with some status)
                generator.process_result(result)
            else:
                # commands without context
                self.execute_command(ecs_mng=ecs_mng, entity_id=entity_id, cmd_ctx=None, command_module_name=cmd_fnc, **cmd_params)


    def register_command(self, command_module_name):
        '''Registers the command and returns the registered command function'''

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

        return self._commands.get(command_module_name)

    def get_command(self, command_module_name):
        '''Gets the command module from the storage if registered or register it'''

        # Try to get the command from the storage and if not found register it
        return self._commands.get(command_module_name, self.register_command(command_module_name))

    def execute_command(self, ecs_mng, entity_id: str|int, cmd_ctx, command_module_name: str, *cmd_args, **cmd_kwargs):
        '''Executes command and returns the result
            self.execute_command(ecs_mng, entity_id, cmd_ctx, cmd_fnc, **cmd_params)
            
            This function should not be called directly from the console if the player
            wants to execute some ad hoc command. It must be always called from process_commands function
            that will deliver the necessary ecs_mng object that is necessary for every command.

            From console probably COmmandManager.add_command(command) would need to be called. This will add the
            command to the queue and consequently processes the command in the next run of the PerformCommand 
            processor.
        '''


        command_fnc = self.get_command(command_module_name)

        # Run the command function
        return command_fnc(ecs_mng, entity_id, cmd_ctx, *cmd_args, **cmd_kwargs)


#### Command Function Example
def cmd_attack_full(ecs_mng, entity_id, cmd_ctx: CommandContext, *cmd_args, **cmd_kwargs):
    ''' Add FlagDoAttack to the entity so long to fill the full attack animation cycle

    Functionality:
    **************

    *Goal*
        - Use weapon on the current position/direction for given time period

    *Results*
        - `SUCCESS` - time `attack_time_ms` is over
        - `RUNNING` - attack in progress
        - `FAILURE` - no more ammo or entity destroyed or target destroyed

    *Params*
        - `attack_time_ms` - how long to generate the attack commands
        - `target_damageable_comp` - Damageable component of the target on the blackboard
        - `entity_damageable_comp` - Damageable component of the entity on the blackboard

    *Steps*
        - Prereq: Save target health component
        - Prereq: Save entity health component

        - Check, if entity/target destroyed
          - if YES,
            - finish with `FAILURE`

        - Check, if within `attack_duration_ms`
          - if YES,
            - assign `FlagHasAttacked` component to entity
            - finish with `RUNNING`
          - if NO,
            - finish with `SUCCESS`

    Example:
    ********
    {
        "type": "Behavior",
        "name": "Attack the target",
        "cmd_process": [
            "btree.attack_full", 
            {
                "target_damageable_comp": "bb_target_damageable_comp", 
                "entity_damageable_comp": "bb_entity_damageable_comp",
                "attack_time_ms": 750
            }
        ]
    }
    '''

    # Get the entity and the target Position components
    target_damageable_comp = cmd_ctx.global_bb.get(cmd_kwargs["target_damageable_comp"])
    entity_damageable_comp = cmd_ctx.global_bb.get(cmd_kwargs["entity_damageable_comp"])

    if target_damageable_comp.health <=0 or entity_damageable_comp.health <= 0:
        return 'FAILURE'

    if cmd_ctx.duration >= cmd_kwargs.get("attack_time_ms", 500):
        # Unit has been executed long enough - continue without exception
        return 'SUCCESS'
    else:
        # There is still time to execute - return exception
        ecs_mng._world.add_component(entity_id, FlagDoAttack())
        return 'RUNNING'
