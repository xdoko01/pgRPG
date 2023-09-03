from enum import Enum
from typing import Protocol
from collections import namedtuple

Command = namedtuple('Command', ['name', 'params'])


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

    def get_command(self) -> Command:
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