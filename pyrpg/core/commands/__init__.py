from enum import Enum
from typing import Protocol, Iterable
from collections import namedtuple
from dataclasses import dataclass, field

Command = namedtuple('Command', ['name', 'params', 'entity_id'])

'''
@dataclass(frozen=True)
class Command:
    name: str
    params: dict
'''

def cmd_factory(cmd: Iterable) -> Command:
    '''Transform command provided as a list or tuple into
    Command instance.
    '''
    assert isinstance(cmd[0], str), f'Name of the command must be a string value.'
    assert isinstance(cmd[1], dict), f'Parameters of the command must be in the form of a dictionary.'

    entity_id_from_cmd = cmd[1].pop('entity', None)
    assert entity_id_from_cmd is None or isinstance(entity_id_from_cmd, int), f'Entity alias "{entity_id_from_cmd}" is not translated to int!'

    return Command(name=cmd[0], params=cmd[1], entity_id=entity_id_from_cmd) if cmd is not None else cmd

class CommandStatus(Enum):
    '''Class representing possible statuses of the the command'''

    NONE = 'NONE'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

@dataclass
class Container:
    '''Container for data stored as class instance attributes. 
    Used to access data as attributes rather than dictionary.
    '''
    def __init__(self, attrs: dict={}):
        for k, v in attrs.items():
            self.add(k, v)

    def __str__(self):
        return f'{self.__dict__}'

    def __repr__(self):
        return f'{self.__dict__}'

    def add(self, name: str, val) -> None:
        setattr(self, name, val)
    
    def get(self, name: str):
        return getattr(self, name)

@dataclass
class CommandContext(Protocol):
    '''Requirement for information about the status of the 
    CommandGenerator.'''

    globals: Container
    locals: Container
    init_time: int
    duration: int
    tick_count: int
    current_time: int

@dataclass
class CommandContextMock(CommandContext):
    globals: Container = field(default_factory=Container)
    locals: Container = field(default_factory=Container)
    init_time: int = 0
    duration: int = 0
    tick_count: int = 1
    current_time: int = 0


class CommandGenerator(Protocol):
    '''Protocol class for all data structures that can generate
    commands - trees, lists, ...'''

    bb: CommandContext

    def reset(self, new_ai_struct: dict) -> Command:
        '''Return Command based on the CommandGenerator logic.'''
        pass

    def get_command(self) -> Command:
        '''Return next Command based on the CommandGenerator logic.'''
        pass

    def process_command_result(self, result: CommandStatus) -> None:
        '''Callback the result of the command in order to update
        CommandGenerator internal state.'''
        pass

    def notify_command_start(self) -> None:
        '''Callback from command manager before the command starts
        in order to set the CommandContext statistics.'''
        pass

class CommandGeneratorMock(CommandGenerator):
    bb: CommandContextMock = CommandContextMock()
    reset = lambda self, new_ai_struct: None
    get_command = lambda self: CommandStatus.SUCCESS
    process_command_result = lambda self, result: None
    notify_command_start = lambda self: None

