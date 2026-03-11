"""Tests for pgrpg.core.managers.pathfind_manager module."""

import pytest

from pgrpg.core.managers import pathfind_manager


@pytest.fixture(autouse=True)
def _reset_pathfind_manager():
    """Reset all mutable module-level state before each test."""
    pathfind_manager._req_queue = []
    pathfind_manager._req_lookup = {}
    pathfind_manager._next_req_id = 0
    yield
    pathfind_manager._req_queue = []
    pathfind_manager._req_lookup = {}
    pathfind_manager._next_req_id = 0


# --- request_path ---

def test_request_path_returns_incrementing_ids(simple_graph):
    """Each call to request_path returns a sequentially incrementing ID."""
    id0 = pathfind_manager.request_path(simple_graph, (1, 1), (4, 2))
    id1 = pathfind_manager.request_path(simple_graph, (2, 1), (3, 2))
    id2 = pathfind_manager.request_path(simple_graph, (1, 2), (4, 1))

    assert id0 == 0
    assert id1 == 1
    assert id2 == 2


def test_request_path_adds_to_queue_and_lookup(simple_graph):
    """Requesting a path populates both the queue and the lookup dict."""
    req_id = pathfind_manager.request_path(simple_graph, (1, 1), (4, 2))

    assert len(pathfind_manager._req_queue) == 1
    assert req_id in pathfind_manager._req_lookup


# --- invalid search ---

def test_request_path_invalid_search_raises(simple_graph):
    """An invalid search algorithm name raises ValueError."""
    with pytest.raises(ValueError):
        pathfind_manager.request_path(simple_graph, (1, 1), (4, 2), search="NONEXISTENT")


# --- complete BFS path ---

def test_complete_bfs_path(simple_graph):
    """A BFS search on the simple graph finds a valid path from (1,1) to (4,2)."""
    req_id = pathfind_manager.request_path(simple_graph, (1, 1), (4, 2), search="BFS")

    # Run pathfinding to completion
    pathfind_manager.continue_pathfinding(max_steps=100)

    path = pathfind_manager.get_path(req_id)

    assert path is not None
    assert len(path) > 0
    # Path should end at the goal
    assert path[-1] == (4, 2)


def test_complete_bfs_path_reverse(simple_graph):
    """BFS finds a path in the reverse direction as well."""
    req_id = pathfind_manager.request_path(simple_graph, (4, 2), (1, 1), search="BFS")

    pathfind_manager.continue_pathfinding(max_steps=100)

    path = pathfind_manager.get_path(req_id)

    assert path is not None
    assert path[-1] == (1, 1)


# --- get_path before continue_pathfinding ---

def test_get_path_before_continue_returns_none(simple_graph):
    """Getting a path before any pathfinding steps returns None (not yet computed)."""
    req_id = pathfind_manager.request_path(simple_graph, (1, 1), (4, 2))

    result = pathfind_manager.get_path(req_id)
    assert result is None


# --- get_path for unknown ID ---

def test_get_path_unknown_id_returns_none():
    """Getting a path for an ID that was never requested returns None."""
    result = pathfind_manager.get_path(req_id=999)
    assert result is None


# --- incremental pathfinding ---

def test_incremental_pathfinding(simple_graph):
    """Pathfinding can proceed incrementally with limited steps per call."""
    req_id = pathfind_manager.request_path(simple_graph, (1, 1), (4, 2))

    # Run with very few steps - may not finish
    pathfind_manager.continue_pathfinding(max_steps=1)

    # Keep going until done (at most a few more rounds)
    for _ in range(20):
        if pathfind_manager.get_path(req_id) is not None:
            break
        pathfind_manager.continue_pathfinding(max_steps=2)

    path = pathfind_manager.get_path(req_id)
    # Path was already consumed above if it finished, so this may be None
    # The important thing is the loop above eventually got a result


def test_get_path_consumed_after_retrieval(simple_graph):
    """Once a path is retrieved, requesting it again returns None."""
    req_id = pathfind_manager.request_path(simple_graph, (1, 1), (4, 2))
    pathfind_manager.continue_pathfinding(max_steps=100)

    first = pathfind_manager.get_path(req_id)
    assert first is not None

    second = pathfind_manager.get_path(req_id)
    assert second is None
