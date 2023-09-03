'''Classes implementing the behavior list functionality

Behavior list is a linear array where every item is representing either some
behavior (action/condition) or some special operation - loops, fors, etc.

Use 'python -m pyrpg.core.commands.generators.blist.blist -v' to run
module tests.
'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

import sys
import pygame

#from functools import reduce, partialmethod
from enum import Enum

# BTree must follow all command related protocols
from pyrpg.core.commands import CommandStatus, CommandGenerator, CommandContext

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
        self.global_bb = global_bb
        self.local_bb = {}
        self.init_time = None
        self.duration = None
        self.tick_count = None

    def reset(self):
        self.local_bb = {} # Every Action Node starts with clear memory
        self.init_time = pygame.time.get_ticks()
        self.duration = 0
        self.tick_count = 1

    def update(self):
        self.duration = pygame.time.get_ticks() - self.init_time
        self.tick_count += 1


class BList(CommandGenerator):

    def __init__(self, list_def: list, cmd_factory=(lambda x: x)) -> None:
        '''get_command, notify_command_start, process command result'''
        # Brain algorithm in form of the list
        self.commands = list_def['cmd_list']

        #Apply function to every command if defined
        for cmd_idx in range(len(self.commands)):
            for key in self.commands[cmd_idx].copy():
                if key == 'command':
                    self.commands[cmd_idx][key] = cmd_factory(self.commands[cmd_idx][key])
        
        logger.debug(f'{self.commands = }')

        self.bb = BListBlackboard(global_bb=list_def.get('blackboard'))

        # Idx of command currently in process
        self.current_cmd_idx = 0
        self.last_cmd_idx = None

        self._is_finished = False if self.commands else True
        self._new_action_node_found = True

        # Init the Loop counter - Necessary for loop command
        self.loop_counter = 0

    def _move_to_idx(self, new_idx: int):
        self.last_cmd_idx = self.current_cmd_idx
        self.current_cmd_idx = new_idx
        print(f'Moving from IDX: {self.last_cmd_idx} to IDX: {self.current_cmd_idx}')
        if self.current_cmd_idx > len(self.commands) - 1 or self.current_cmd_idx < 0:
            self._is_finished = True
            print(f'BList is finished {self.last_cmd_idx = }, {self.current_cmd_idx = }')

    def _find_next_action_node(self):
        '''Jump for so long untill you land on the behavior node'''
        # Get the type of the node
        type = self.commands[self.current_cmd_idx].get('type', 'Behavior')
        print(f'Type is {type = }')

        # you have ended up with the action node - end
        if type == 'Behavior' or self._is_finished:
            return

        else:
            if type == 'Loop': 
                if self.loop_counter >= self.commands[self.current_cmd_idx]['repeat']:
                    print(f'{self.loop_counter = } ... reseting to 0')
                    self.loop_counter = 0
                    self._move_to_idx(new_idx=self.current_cmd_idx+1)
                else:
                    print(f'{self.loop_counter = }')
                    self.loop_counter += 1
                    self._move_to_idx(new_idx=self.commands[self.current_cmd_idx]['jmp_to'])

            elif type == 'Goto':
                self._move_to_idx(new_idx=self.commands[self.current_cmd_idx]['jmp_to'])

            self._find_next_action_node() # maybe we have landed on another special node after the jump

    def print(self) -> None:
        '''Print running command in yellow'''
        for cmd_idx in range(len(self.commands)):
            if cmd_idx == self.current_cmd_idx:
                print(f'\033[93m{self.commands[cmd_idx]}\033[00m')
            else:
                print(f'{self.commands[cmd_idx]}')

    def get_command(self) -> tuple:
        '''Search for the next command if not finished'''

        # Jump so long until you reach the Behavior node in currend_cmd_idx
        self._find_next_action_node()

        # If algorithm has finished, return nothing
        if self._is_finished:
            print(f'Behavior list is completed, no more command to return')
            return
        
        print(f'About to get command from IDX: {self.current_cmd_idx = }')
        # If we have some action node, use it
        return self.commands[self.current_cmd_idx]['command']

    def notify_command_start(self) -> None:
        '''Callback from command manager before the command starts
        in order to set the CommandContext statistics.'''

        # calculate the init time and others when it is the first call of the action
        if self._new_action_node_found: 
            self.bb.reset() # Reset statistics for the new action node
            self._new_action_node_found = False
        else:
            self.bb.update() # Update statistics

    def process_command_result(self, result: BListCommandStatus) -> None:
        '''Here mark the BList as finished if finished'''
        # If the command finished succesfully - move to the next command
        if result.is_success:
            self._move_to_idx(new_idx=self.current_cmd_idx+1)
            self._new_action_node_found = True

        elif result.is_failure:
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

    '''On SUCCESS, continue to the next line'''
    '''If not finished, switch to RUNNING status'''
    '''On FAILURE, jump to exception line if defined. If not defined, continue'''
    # line and name and type are optional on Behavior but manddatory on Looper
    b_list_data1 = {
        'blackboard': {},
        'cmd_list': [
            {"line": 0, "type": "Behavior", "name": "Move", "command": ["test_cmd_1", {"bb_key": "bb_target_pos_comp", "bb_entity": "$target_in", "component": "new.position:Position"}], "on_fail_jmp": None},
            {"line": 1, "type": "Behavior", "name": "Move", "command": ["test_cmd_2", {"bb_key": "bb_target_pos_comp", "bb_entity": "$target_in", "component": "new.position:Position"}], "on_fail_jmp": None},
            {"line": 2, "type": "Loop", "name": "Looper1", "repeat": 2, "jmp_to": 0},
            {"line": 3, "type": "Goto", "name": "goto", "jmp_to": -1}
        ]
    }

    b_list_data2 = {
        'blackboard': {},
        'cmd_list' : [
            {"line": 0, 'on_fail_jmp': 0, 'command': ["new_guard", {"enemy": "player01", "radius": 200, "update_time_ms": 2000}] },
            {"line": 1, 'on_fail_jmp': 1, 'command': ["new_move_to_target", {"target" : "player01", "radius": 50, "update_time_ms": 500}]},
            {"line": 2, 'on_fail_jmp': 2, 'command': ["new_attack_full", {"attack_time_ms": 500}]},
            {"line": 3, 'jmp_to': 1, "type": "Goto"}
        ]
    }

    pygame.init()
    from random import randint

    blist = BList(list_def=b_list_data2)


    while not blist._is_finished:
        print(blist.get_command())
        blist.notify_command_start()
        print(f'Blackboard updated ... {blist.bb.init_time = }, {blist.bb.duration = }, {blist.bb.tick_count = }')
        cmd_result = eval("[BListCommandStatus.FAILURE, BListCommandStatus.SUCCESS, BListCommandStatus.RUNNING, BListCommandStatus.RUNNING, BListCommandStatus.RUNNING, BListCommandStatus.RUNNING][randint(0,5)]")
        print(f'Returning result {cmd_result = }')
        blist.process_command_result(result=cmd_result)
        blist.print()
