"""Tests for pgrpg.core.managers.message_manager module."""

import pytest
from unittest.mock import patch, MagicMock

from pgrpg.core.managers import message_manager


class _FakeMessage:
    """Lightweight stand-in for Message to avoid pygame init."""

    def __init__(self, text, created, ttl):
        self.text = text
        self.created = created
        self.ttl = ttl


@pytest.fixture(autouse=True)
def _reset_message_manager():
    """Reset all mutable module-level state before each test."""
    message_manager._message_queue = []
    yield
    message_manager._message_queue = []


# --- add_message ---

def test_add_message():
    """Adding a message appends it to the queue."""
    msg = _FakeMessage(text="Hello", created=0, ttl=5000)
    message_manager.add_message(msg)

    assert len(message_manager._message_queue) == 1
    assert message_manager._message_queue[0].text == "Hello"


def test_add_multiple_messages():
    """Multiple messages are appended in order."""
    msg1 = _FakeMessage(text="First", created=0, ttl=5000)
    msg2 = _FakeMessage(text="Second", created=100, ttl=5000)
    message_manager.add_message(msg1)
    message_manager.add_message(msg2)

    assert len(message_manager._message_queue) == 2
    assert message_manager._message_queue[0].text == "First"
    assert message_manager._message_queue[1].text == "Second"


# --- get_messages ---

@patch("pgrpg.core.managers.message_manager.get_ticks", return_value=10000)
def test_get_messages_filters_expired(mock_ticks):
    """Expired messages (current_time - created >= ttl) are removed."""
    expired = _FakeMessage(text="Old", created=0, ttl=5000)
    message_manager._message_queue.append(expired)

    result = message_manager.get_messages()

    assert len(result) == 0


@patch("pgrpg.core.managers.message_manager.get_ticks", return_value=1000)
def test_get_messages_keeps_active(mock_ticks):
    """Active messages (current_time - created < ttl) are retained."""
    active = _FakeMessage(text="Active", created=500, ttl=5000)
    message_manager._message_queue.append(active)

    result = message_manager.get_messages()

    assert len(result) == 1
    assert result[0].text == "Active"


@patch("pgrpg.core.managers.message_manager.get_ticks", return_value=6000)
def test_get_messages_mixed_active_and_expired(mock_ticks):
    """Only active messages survive filtering."""
    expired = _FakeMessage(text="Expired", created=0, ttl=5000)
    active = _FakeMessage(text="Active", created=5500, ttl=5000)
    message_manager._message_queue.extend([expired, active])

    result = message_manager.get_messages()

    assert len(result) == 1
    assert result[0].text == "Active"


# --- clear_messages ---

def test_clear_messages():
    """Clearing messages empties the queue."""
    msg = _FakeMessage(text="Msg", created=0, ttl=5000)
    message_manager.add_message(msg)
    message_manager.add_message(msg)

    assert len(message_manager._message_queue) == 2
    message_manager.clear_messages()
    assert len(message_manager._message_queue) == 0
