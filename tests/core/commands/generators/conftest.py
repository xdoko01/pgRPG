"""Conftest for command generator tests — freezes the clock for btree/blist."""

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def _mock_pygame_ticks():
    """Freeze pygame.time.get_ticks at 0 so blackboard timings are deterministic.

    This does not remove the need for pygame to be initialized — the blackboards
    assert pygame.get_init() directly. That is handled by the session-scoped
    init_pygame fixture in the root conftest.
    """
    with patch("pygame.time.get_ticks", return_value=0):
        yield
