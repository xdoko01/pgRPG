"""Tests for pgrpg.core.managers.event_manager module."""

import pytest
from collections import deque
from unittest.mock import MagicMock

from pgrpg.core.managers import event_manager
from pgrpg.core.events.event import Event


@pytest.fixture(autouse=True)
def _reset_event_manager():
    """Reset all mutable module-level state before each test."""
    event_manager._event_queue = deque()
    event_manager._event_handlers = {}
    event_manager._exec_event_actions_fnc = lambda x: None
    yield
    event_manager._event_queue = deque()
    event_manager._event_handlers = {}
    event_manager._exec_event_actions_fnc = lambda x: None


# --- load_handler ---

def test_load_handler_new_event_type():
    """Loading a handler for a new event type creates the event type entry."""
    handler_def = ["SCENE_START", {"id": "h1", "actions": ["SCRIPT", "do_thing", {}]}]
    event_manager.load_handler(handler_def)

    assert "SCENE_START" in event_manager._event_handlers
    assert "h1" in event_manager._event_handlers["SCENE_START"]
    assert event_manager._event_handlers["SCENE_START"]["h1"]["actions"] == ["SCRIPT", "do_thing", {}]


def test_load_handler_existing_event_type():
    """Loading a second handler for an existing event type appends it."""
    event_manager.load_handler(["COLLISION", {"id": "h1", "actions": ["A"]}])
    event_manager.load_handler(["COLLISION", {"id": "h2", "actions": ["B"]}])

    assert len(event_manager._event_handlers["COLLISION"]) == 2
    assert "h1" in event_manager._event_handlers["COLLISION"]
    assert "h2" in event_manager._event_handlers["COLLISION"]


def test_load_handler_overwrites_same_id():
    """Loading a handler with the same id overwrites the previous one."""
    event_manager.load_handler(["KILL", {"id": "h1", "actions": ["OLD"]}])
    event_manager.load_handler(["KILL", {"id": "h1", "actions": ["NEW"]}])

    assert event_manager._event_handlers["KILL"]["h1"]["actions"] == ["NEW"]


# --- delete_handler ---

def test_delete_handler():
    """Deleting a handler by id removes it from all event types."""
    event_manager.load_handler(["DAMAGE", {"id": "dmg_handler", "actions": []}])
    assert "dmg_handler" in event_manager._event_handlers["DAMAGE"]

    event_manager.delete_handler("dmg_handler")
    assert "dmg_handler" not in event_manager._event_handlers["DAMAGE"]


def test_delete_handler_nonexistent():
    """Deleting a handler that does not exist does not raise."""
    event_manager.load_handler(["DAMAGE", {"id": "h1", "actions": []}])
    event_manager.delete_handler("nonexistent")  # should not raise


# --- delete_handlers_pattern ---

def test_delete_handlers_pattern():
    """Deleting handlers by wildcard pattern removes all matching."""
    event_manager.load_handler(["SCORE", {"id": "enemy_1", "actions": []}])
    event_manager.load_handler(["SCORE", {"id": "enemy_2", "actions": []}])
    event_manager.load_handler(["SCORE", {"id": "player_1", "actions": []}])

    event_manager.delete_handlers_pattern("enemy_*")

    assert "enemy_1" not in event_manager._event_handlers["SCORE"]
    assert "enemy_2" not in event_manager._event_handlers["SCORE"]
    assert "player_1" in event_manager._event_handlers["SCORE"]


# --- add_event / clear_events / get_events ---

def test_add_event_increases_queue():
    """Adding an event increases the queue length."""
    assert len(event_manager.get_events()) == 0

    ev = Event(event_type="COLLISION", generator_obj=None, other_obj=None, params={})
    event_manager.add_event(ev)
    assert len(event_manager.get_events()) == 1

    event_manager.add_event(ev)
    assert len(event_manager.get_events()) == 2


def test_clear_events_empties_queue():
    """Clearing events results in an empty queue."""
    ev = Event(event_type="KILL", generator_obj=None, other_obj=None, params={})
    event_manager.add_event(ev)
    event_manager.add_event(ev)

    event_manager.clear_events()
    assert len(event_manager.get_events()) == 0


# --- create_event ---

def test_create_event_returns_event():
    """create_event returns an Event instance with the correct type and params."""
    ev = event_manager.create_event(type="TELEPORTATION", params={"dest": (5, 5)})

    assert isinstance(ev, Event)
    assert ev.event_type == "TELEPORTATION"
    assert ev.params == {"dest": (5, 5)}
    assert ev.generator_obj is None
    assert ev.other_obj is None


# --- process_events ---

def test_process_events_calls_exec_function():
    """process_events dispatches matching events through the exec function."""
    mock_exec = MagicMock()
    event_manager.init(mock_exec)

    event_manager.load_handler(["SCENE_START", {"id": "h1", "actions": ["SCRIPT", "test", {}]}])

    ev = Event(event_type="SCENE_START", generator_obj=None, other_obj=None, params={})
    event_manager.add_event(ev)

    event_manager.process_events()

    mock_exec.assert_called_once()
    call_args = mock_exec.call_args
    assert call_args[0][0] is ev  # first positional arg is the event
    assert call_args[0][1] == ["SCRIPT", "test", {}]  # second is the actions


def test_process_events_with_ignore_filter():
    """Events in the ignore list are skipped during processing."""
    mock_exec = MagicMock()
    event_manager.init(mock_exec)

    event_manager.load_handler(["KILL", {"id": "h1", "actions": ["A"]}])
    event_manager.load_handler(["DAMAGE", {"id": "h2", "actions": ["B"]}])

    event_manager.add_event(Event(event_type="KILL", generator_obj=None, other_obj=None, params={}))
    event_manager.add_event(Event(event_type="DAMAGE", generator_obj=None, other_obj=None, params={}))

    event_manager.process_events(ignore=["KILL"])

    # Only DAMAGE handler should have been called
    assert mock_exec.call_count == 1
    call_args = mock_exec.call_args
    assert call_args[0][1] == ["B"]


def test_process_events_drains_queue():
    """After process_events, the queue should be empty."""
    mock_exec = MagicMock()
    event_manager.init(mock_exec)

    event_manager.add_event(Event(event_type="UNKNOWN", generator_obj=None, other_obj=None, params={}))
    event_manager.process_events()

    assert len(event_manager.get_events()) == 0
