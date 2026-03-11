"""Non-blocking pathfinding distributed across game cycles.

Pathfinding requests are queued and incrementally computed over multiple
frames so that no single frame bears the full cost of a long search.

Run ``python -m pgrpg.core.managers.pathfind_manager`` for a quick demo.

Module Globals:
    _req_queue: Pending PathfindRequest objects awaiting computation.
    _req_lookup: Dict mapping request IDs to PathfindRequest objects.
    _next_req_id: Auto-incrementing counter for request IDs.
"""

from enum import Enum
from collections import namedtuple
from pgrpg.core.pathfinding import BFS as BFSearch

import logging
logger = logging.getLogger(__name__)

PathfindAttrs = namedtuple('PathfindAttrs',('search', 'checkpoints', 'start'))

class PathfindOption(Enum):
    BFS = PathfindAttrs(search=BFSearch, checkpoints=False, start=False)
    BFS_CHECKPOINTS = PathfindAttrs(search=BFSearch, checkpoints=True, start=False)
    BFS_CHECKPOINTS_W_FIRST = PathfindAttrs(search=BFSearch, checkpoints=True, start=True)

class PathfindRequest:
    """Hold state for a single pathfinding request."""

    def __init__(self, graph: dict, start: tuple, goal: tuple, option: PathfindOption):
        """Create a pathfinding request.

        Args:
            graph: Adjacency dict mapping (x, y) -> [((nx, ny), cost), ...].
            start: Starting tile coordinates.
            goal: Target tile coordinates.
            option: PathfindOption controlling search algorithm and post-processing.
        """
        self.start = start
        self.goal = goal
        self.options = option
        self.search = option.value.search(graph=graph, start=start, goal=goal)
        logger.debug(f'PathfindRequest created for {start=}, {goal=} using search {option.name=}')

    def __str__(self):
        return f'{self.start=}\n{self.goal=}\n{self.search=}\n{self.options=}\n'

_req_queue: list = [] # list of PathfindRequest objects
_req_lookup: dict = {} # lookup for PathfindRequest based on their req_id
_next_req_id: int = 0 # last calc id generated

logger.debug(f"PathfindManager created.")

def __str__():
    """PathfindManager information."""
    return f"{_req_queue=}\n{_req_lookup=}\n{_next_req_id=}"

def request_path(graph: dict, start: tuple, goal: tuple, search: str='BFS'):
    """Queue a new pathfinding request and return its ID.

    Args:
        graph: Adjacency dict mapping (x, y) -> [((nx, ny), cost), ...].
        start: Starting tile coordinates.
        goal: Target tile coordinates.
        search: Name of a PathfindOption member (default ``'BFS'``).

    Returns:
        Integer request ID used to retrieve the result via ``get_path``.

    Raises:
        ValueError: If the search name is not a valid PathfindOption.
    """
    # Create PathFindRequest object
    try:
        path_req = PathfindRequest(graph=graph, start=start, goal=goal, option=PathfindOption[search])
    except KeyError:
        raise ValueError(f"Requested pathfinding search {search=} is not defined. Available searchs are: " +
                            f"{PathfindOption._member_names_}.")

    # Generate new calc_id under which the path_request is stored
    global _next_req_id
    req_id = _next_req_id
    _next_req_id += 1

    # Generate ID and Register it in the dictionary
    _req_lookup.update({req_id: path_req})
    logger.debug(f"PathfindRequest registered under {req_id=}")

    # Add calc request to the calculation queue
    _req_queue.append(path_req)
    logger.debug(f"Pathfinding request {req_id=} added into the queue for processing. Total enqued requests {len(_req_queue)=}")

    # Return the new ID
    return req_id

def continue_pathfinding(max_steps=None):
    """Advance pending path calculations by a limited number of steps.

    Steps are distributed evenly across all queued requests. Completed
    requests are automatically removed from the queue.

    Args:
        max_steps: Total step budget across all requests. None means
            compute all remaining steps (complete everything).
    """
    # Quit if there is no path for calculation
    if len(_req_queue) == 0: return

    # How many cycles we can spend on each path calculation in the queue
    max_steps_per_calc = max_steps // len(_req_queue) if max_steps is not None else None
    
    for path_req in _req_queue.copy():
        finished, path = path_req.search.proceed(no_of_steps=max_steps_per_calc)
        if finished:
            # remove from queue and continue with next one
            logger.debug(f"Pathfinding request fulfilled and path calculation finished")
            _req_queue.remove(path_req)

def get_path(req_id: int):
    """Retrieve a completed path result by request ID.

    Returns:
        The path as a list of (x, y) tuples if computation is complete,
        an empty list if no path exists, or None if still computing or
        the ID is unknown. The request is consumed on retrieval.
    """
    
    # Find the path using the ID
    path_req = _req_lookup.get(req_id, None) # if not found return None

    # If no such path_id exists
    if path_req is None:
        logger.debug(f"{req_id=} does not exists and/or path already obtained.")
        return None
    
    # If calculation is still running
    if not path_req.search.finished: 
        logger.debug(f"{req_id=} calculation is still in progress.\nDetails:\n{path_req.search}")
        return None

    # If finished
    #  Remove from the dictionaty _req_lookup
    _req_lookup.pop(req_id)

    # Extract only checkpoints - if wanted
    if path_req.options.value.checkpoints: path_req.search.filter_checkpoints()

    # Add start coordinates - if wanted
    if path_req.options.value.start: path_req.search.include_start()
    
    # Return resulting path
    return path_req.search.get_path_result()



if __name__ == '__main__':

    map_graph = {
        (1, 1): [((2, 1), 1), ((1, 2), 1)],
        (1, 2): [((2, 2), 1), ((1, 1), 1)],
        (2, 1): [((3, 1), 1), ((1, 1), 1), ((2, 2), 1)],
        (2, 2): [((3, 2), 1), ((1, 2), 1), ((2, 1), 1)],
        (3, 1): [((4, 1), 1), ((2, 1), 1), ((3, 2), 1)],
        (3, 2): [((4, 2), 1), ((2, 2), 1), ((3, 1), 1)],
        (4, 1): [((3, 1), 1), ((4, 2), 1)],
        (4, 2): [((3, 2), 1), ((4, 1), 1)]
    }

    # Request paths calculation from the manager
    path_req_0 = request_path(map_graph, (1,1), (4,2), 'BFS')
    path_req_1 = request_path(map_graph, (4,2), (1,1), 'BFS_CHECKPOINTS')
    path_req_2 = request_path(map_graph, (4,2), (1,1), 'BFS_CHECKPOINTS_W_FIRST')

    # Process the calculation - maximum 2 calc steps allowed
    continue_pathfinding(max_steps=2)
    continue_pathfinding(max_steps=2)
    continue_pathfinding(max_steps=2)
    continue_pathfinding(max_steps=20)

    # Retrieve the results
    print(f'Request 0 results: {get_path(req_id=path_req_0)}')
    print(f'Request 1 results: {get_path(req_id=path_req_1)}')
    print(f'Request 2 results: {get_path(req_id=path_req_2)}')

# %%
