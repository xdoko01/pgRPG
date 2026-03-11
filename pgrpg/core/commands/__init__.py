"""Command types, protocols, and factories for entity command generation.

Defines the Command namedtuple, CommandStatus enum, CommandContext protocol,
CommandGenerator protocol, and the Container helper dataclass used as a
simple attribute-based key-value store for blackboard data.
"""

from enum import Enum
from typing import Protocol, Iterable
from collections import namedtuple
from dataclasses import dataclass, field

Command = namedtuple('Command', ['name', 'params', 'entity_id'])

def cmd_factory(cmd: Iterable) -> Command:
    """Transform a list/tuple command definition into a Command namedtuple.

    Args:
        cmd: A sequence of [name, params_dict] where params may contain
            an ``'entity'`` key that is extracted as the target entity_id.

    Returns:
        A Command namedtuple, or the original value if cmd is None.

    Raises:
        AssertionError: If name is not a string, params is not a dict,
            or entity alias was not translated to int.
    """
    assert isinstance(cmd[0], str), f'Name of the command must be a string value.'
    assert isinstance(cmd[1], dict), f'Parameters of the command must be in the form of a dictionary.'

    entity_id_from_cmd = cmd[1].pop('entity', None)
    assert entity_id_from_cmd is None or isinstance(entity_id_from_cmd, int), f'Entity alias "{entity_id_from_cmd}" is not translated to int!'

    return Command(name=cmd[0], params=cmd[1], entity_id=entity_id_from_cmd) if cmd is not None else cmd

class CommandStatus(Enum):
    """Possible result statuses returned by command execution."""

    NONE = 'NONE'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

@dataclass
class Container:
    """Attribute-based key-value store for blackboard data.

    Used by CommandContext to hold globals/locals as named attributes
    rather than dict keys.
    """
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
    """Protocol defining the required state interface for command generators."""

    globals: Container
    locals: Container
    init_time: int
    duration: int
    tick_count: int
    current_time: int

class CommandGenerator(Protocol):
    """Protocol for command-generating data structures (trees, lists, etc.)."""

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

