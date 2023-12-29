'''Classes implementing the behavior list functionality

Behavior list is a linear array where every item is representing either some
behavior (action/condition) or some special operation - loops, fors, etc.

Use 'python -m pyrpg.core.commands.generators.blist.blist -v' to run
module tests.
'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

import pygame

#from functools import reduce, partialmethod
from enum import Enum

# BTree must follow all command related protocols
from pyrpg.core.commands import CommandStatus, CommandGenerator, CommandContext, Container

class BListCommandStatus(Enum):
    '''Mapping of ComandStatus to internal Statuses used in the behavior list implementation.'''
    NONE = CommandStatus.NONE
    RUNNING = CommandStatus.RUNNING
    SUCCESS = CommandStatus.SUCCESS
    FAILURE = CommandStatus.FAILURE

    @property
    def is_valid(cls) -> bool: return cls in [cls.SUCCESS, cls.FAILURE, cls.RUNNING, cls.NONE]

    @property
    def is_completed(cls) -> bool: return cls in [cls.SUCCESS, cls.FAILURE]

    @property
    def is_failure(cls) -> bool: return cls in [cls.FAILURE]

    @property
    def is_success(cls) -> bool: return cls in [cls.SUCCESS]

    @property
    def is_running(cls) -> bool: return cls in [cls.RUNNING]

class InvalidBehaviorListError(Exception):
    pass

class BListBlackboard(CommandContext):

    def __init__(self, global_bb: dict={}):
        assert pygame.get_init() # without initialization get_ticks function will not work properly
        self.globals = Container(attrs=global_bb)
        self.locals = Container()
        self.init_time = None
        self.duration = None
        self.tick_count = None
        self.current_time = pygame.time.get_ticks()

    def reset(self):
        self.locals = Container() # Every Action Node starts with clear memory
        self.init_time = pygame.time.get_ticks()
        self.duration = 0
        self.tick_count = 1
        self.current_time = pygame.time.get_ticks()

    def update(self):
        self.current_time = pygame.time.get_ticks()
        self.duration = self.current_time - self.init_time
        self.tick_count += 1


class BList(CommandGenerator):

    def __init__(self, list_def: dict, cmd_factory=(lambda x: x)) -> None:
        '''Initiates BList AI structure'''
        # Store cmd factory for init and later usage in reset method in order
        # for the reset method to be executed always with the same command factory
        # that was defined during the init.
        self.cmd_factory = cmd_factory
        self.reset(new_ai_struct=list_def)

    def _move_to_idx(self, new_idx: int) -> None:
        '''Move to the specific line of the BList structure.
        Numbering starts from 0.
        '''
        self.last_cmd_idx = self.current_cmd_idx
        self.current_cmd_idx = new_idx
        logger.debug(f'Moving from {self.last_cmd_idx=} to {self.current_cmd_idx=}')
        if self.current_cmd_idx > len(self.commands) - 1 or self.current_cmd_idx < 0:
            self._is_finished = True
            logger.debug(f'BList is finished {self.last_cmd_idx = }, {self.current_cmd_idx = }')

    def _find_next_action_node(self):
        '''Jump for so long until you land on the behavior/action node.
        '''

        if self._is_finished: 
            logger.debug(f'BList is finished, no more commands to look for.')
            return

        # Get the type of the node
        type = self.commands[self.current_cmd_idx].get('type', 'Behavior')
        logger.debug(f'Currently standing on command with the {type=}')

        # You have ended up with the action node - end
        if type == 'Behavior': 
            logger.debug(f'Currently standing on Behavior command.')
            return

        # Special types behavior
        else:
            if type.lower() == 'loop': 
                if self.loop_counter >= self.commands[self.current_cmd_idx]['repeat']:
                    logger.debug(f'{self.loop_counter = } ... reseting to 0')
                    self.loop_counter = 0
                    self._move_to_idx(new_idx=self.current_cmd_idx+1)
                else:
                    print(f'{self.loop_counter = }')
                    self.loop_counter += 1
                    self._move_to_idx(new_idx=self.commands[self.current_cmd_idx]['jmp_to'])

            elif type.lower() == 'goto':
                self._move_to_idx(new_idx=self.commands[self.current_cmd_idx]['jmp_to'])
            
            # maybe we have landed on another special type after the jump
            # so we need to repeat the search for behavior/action
            self._find_next_action_node() 

    def print(self) -> None:
        '''Print running command in yellow'''
        for cmd_idx in range(len(self.commands)):
            if cmd_idx == self.current_cmd_idx:
                print(f'\033[93m{self.commands[cmd_idx]}\033[00m')
            else:
                print(f'{self.commands[cmd_idx]}')

    def __str__(self):
        return f'{self.commands[self.current_cmd_idx]}'

    def reset(self, new_ai_struct: dict) -> None:
        '''Reset the BList structure and fill it with the new commands.
        '''
        # Brain algorithm in form of the list
        logger.debug(f'About to reset the BList with the following new structure {new_ai_struct=}')
        self.commands = new_ai_struct['cmd_list']
        logger.debug(f'New set of commands in BList before translation is {self.commands=}')

        #Apply function to every command if defined
        for cmd_idx in range(len(self.commands)):
            for key in self.commands[cmd_idx].copy():
                if key == 'command':
                    logger.debug(f'Trying to transform command {self.commands[cmd_idx][key]} using factory function {self.cmd_factory}')
                    self.commands[cmd_idx][key] = self.cmd_factory(self.commands[cmd_idx][key])
        
        logger.debug(f'List of commands after transformation by the command factory: {self.commands=}')

        self.bb = BListBlackboard(global_bb=new_ai_struct.get('blackboard', {}))

        # Idx of command currently in process
        self.current_cmd_idx = 0
        self.last_cmd_idx = None

        self._is_finished = False if self.commands else True
        self._new_action_node_found = True

        # Init the Loop counter - Necessary for loop command
        self.loop_counter = 0

    def get_command(self) -> (any, bool):
        '''Search for the next command, if BList is not finished.
        Returns tuple consisting of whatever stored under the command
        attribute + information if it is the first call of the command.
        '''

        # Jump so long until you reach the Behavior node in currend_cmd_idx
        logger.debug(f'Trying to find the next action node...')
        self._find_next_action_node()

        # If algorithm has finished, return nothing
        if self._is_finished:
            logger.debug(f'Behavior list is completed, no more command to return')
            return (None, False)

        logger.debug(f'About to get and return command from IDX: {self.current_cmd_idx = }')
        
        # If we have some action node, use it
        cmd = self.commands[self.current_cmd_idx]['command']
        return (cmd, self._new_action_node_found)

    def notify_command_start(self) -> None:
        '''Callback from command manager before the command starts
        in order to set the CommandContext statistics.'''

        # calculate the init time and others when it is the first call of the action
        if self._new_action_node_found: 
            self.bb.reset() # Reset statistics for the new action node
            self._new_action_node_found = False
        else:
            self.bb.update() # Update statistics

    def process_command_result(self, result: CommandStatus) -> None:
        '''Here mark the BList as finished if finished'''
        # If the command finished succesfully - move to the next command
        if BListCommandStatus(result).is_success:
            self._move_to_idx(new_idx=self.current_cmd_idx+1)
            self._new_action_node_found = True

        elif BListCommandStatus(result).is_failure:
            # Find out where to skip if there is exception
            goto_on_failure = self.commands[self.current_cmd_idx].get('on_fail_jmp') # if jump clause not found use None

            # If there is some skipping defined
            if goto_on_failure != None:
                self._move_to_idx(new_idx=goto_on_failure)

            else:
                # If the command unit does not have defined goto skip on exception
                # then continue with the next command.
                self._move_to_idx(new_idx=self.current_cmd_idx+1)

            self._new_action_node_found = True

        else: #RUNNING
            self._new_action_node_found = False


if __name__ == '__main__':
    import doctest
    doctest.testmod()
