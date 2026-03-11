"""Conftest for command generator tests — patches pygame before btree/blist import."""

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def _mock_pygame_ticks():
    """Auto-patch pygame.time.get_ticks for all btree/blist tests."""
    with patch("pygame.time.get_ticks", return_value=0):
        yield
