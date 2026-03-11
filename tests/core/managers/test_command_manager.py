"""Tests for pgrpg.core.managers.command_manager module."""

import pytest
from collections import namedtuple

from pgrpg.core.managers import command_manager
from pgrpg.core.commands import Command


@pytest.fixture(autouse=True)
def _reset_command_manager():
    """Reset all mutable module-level state before each test."""
    command_manager._command_queue = []
    command_manager._commands = {}
    yield
    command_manager._command_queue = []
    command_manager._commands = {}


# --- add_command ---

def test_add_command_none_is_ignored():
    """Passing None as the command should be silently ignored."""
    command_manager.add_command(cmd=None, orig_entity_id=1)
    assert len(command_manager._command_queue) == 0


def test_add_command_appends_to_queue():
    """A valid command is added to the queue."""
    cmd = Command(name="move", params={"dx": 1}, entity_id=None)
    command_manager.add_command(cmd=cmd, orig_entity_id=42)

    assert len(command_manager._command_queue) == 1
    queued_cmd, entity_id, generator = command_manager._command_queue[0]
    assert queued_cmd is cmd
    assert entity_id == 42
    assert generator is None


def test_add_command_uses_cmd_entity_id_over_orig():
    """When the command has its own entity_id, it takes precedence."""
    cmd = Command(name="attack", params={}, entity_id=99)
    command_manager.add_command(cmd=cmd, orig_entity_id=1)

    _, entity_id, _ = command_manager._command_queue[0]
    assert entity_id == 99


def test_add_command_string_entity_id_raises():
    """A string entity_id should raise AssertionError (must be int)."""
    cmd = Command(name="move", params={}, entity_id="player")
    with pytest.raises(AssertionError):
        command_manager.add_command(cmd=cmd, orig_entity_id="player")


# --- clear_command_queue ---

def test_clear_command_queue():
    """Clearing the queue removes all commands."""
    cmd = Command(name="idle", params={}, entity_id=None)
    command_manager.add_command(cmd=cmd, orig_entity_id=1)
    command_manager.add_command(cmd=cmd, orig_entity_id=2)

    assert len(command_manager._command_queue) == 2
    command_manager.clear_command_queue()
    assert len(command_manager._command_queue) == 0


# --- get_command_queue ---

def test_get_command_queue_returns_list():
    """get_command_queue returns the internal list reference."""
    queue = command_manager.get_command_queue()
    assert isinstance(queue, list)
    assert queue is command_manager._command_queue


def test_get_command_queue_reflects_additions():
    """The returned queue reflects commands added after retrieval."""
    queue = command_manager.get_command_queue()
    assert len(queue) == 0

    cmd = Command(name="wait", params={}, entity_id=None)
    command_manager.add_command(cmd=cmd, orig_entity_id=10)
    assert len(queue) == 1
