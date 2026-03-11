"""Shared test fixtures for the pgrpg test suite."""

import pytest
from unittest.mock import patch


@pytest.fixture
def mock_pygame_ticks():
    """Mock pygame.time.get_ticks to return 0, avoiding pygame init requirement."""
    with patch("pygame.time.get_ticks", return_value=0):
        yield


@pytest.fixture
def simple_graph():
    """A small 4x2 grid graph for pathfinding tests."""
    return {
        (1, 1): [((2, 1), 1), ((1, 2), 1)],
        (1, 2): [((2, 2), 1), ((1, 1), 1)],
        (2, 1): [((3, 1), 1), ((1, 1), 1), ((2, 2), 1)],
        (2, 2): [((3, 2), 1), ((1, 2), 1), ((2, 1), 1)],
        (3, 1): [((4, 1), 1), ((2, 1), 1), ((3, 2), 1)],
        (3, 2): [((4, 2), 1), ((2, 2), 1), ((3, 1), 1)],
        (4, 1): [((3, 1), 1), ((4, 2), 1)],
        (4, 2): [((3, 2), 1), ((4, 1), 1)],
    }
