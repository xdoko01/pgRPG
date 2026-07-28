"""Shared test fixtures for the pgrpg test suite."""

import os

# Force SDL to headless drivers before anything imports pygame. Importing
# pgrpg.core.config calls pygame.init() at module level, and that can happen
# during collection, so this must be set at conftest import time — not inside
# a fixture.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame for the whole test session.

    BTreeBlackboard and BListBlackboard both assert pygame.get_init(), so the
    suite needs pygame initialized. Previously this only worked by accident,
    as an import side effect of pgrpg.core.config, which made results depend
    on collection order and broke single-file runs.
    """
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_pygame_ticks():
    """Mock pygame.time.get_ticks to return 0 for deterministic timing."""
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
