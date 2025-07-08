''' For the module test run python -m pyrpg.core.managers.pathfind_manager -v
while being in the pyRPG root dictionary
'''
from enum import Enum
from collections import namedtuple
from pyrpg.core.pathfinding import BFS as BFSearch # available pathfinding searchs

# Initiate logging
import logging
logger = logging.getLogger(__name__)

PathfindAttrs = namedtuple('PathfindAttrs',('search', 'checkpoints', 'start'))

class PathfindOption(Enum):
    BFS = PathfindAttrs(search=BFSearch, checkpoints=False, start=False)
    BFS_CHECKPOINTS = PathfindAttrs(search=BFSearch, checkpoints=True, start=False)
    BFS_CHECKPOINTS_W_FIRST = PathfindAttrs(search=BFSearch, checkpoints=True, start=True)

class PathfindRequest:
    '''Class representing an object holding information about the request for 
    finding a path.
    '''
    def __init__(self, graph: dict, start: tuple, goal: tuple, option: PathfindOption):
        '''Creates pathfinding request object
        '''
        self.start = start
        self.goal = goal
        self.options = option
        self.search = option.value.search(graph=graph, start=start, goal=goal)
        logger.debug(f'PathfindRequest created for {start=}, {goal=} using search {option.name=}')

    def __str__(self):
        return f'{self.start=}\n{self.goal=}\n{self.search=}\n{self.options=}\n'

###

_req_queue: list = [] # list of PathfindRequest objects
_req_lookup: dict = {} # lookup for PathfindRequest based on their req_id
_next_req_id: int = 0 # last calc id generated

logger.debug(f"PathfindManager created.")

def __str__():
    """PathfindManager information."""
    return f"{_req_queue=}\n{_req_lookup=}\n{_next_req_id=}"

def request_path(graph: dict, start: tuple, goal: tuple, search: str='BFS'):
    """Registers PathfindRequest with the processor and enqueue it for processing.

    :returns: int - Path Request ID
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
    """Try part of the path calculation for all paths in the queue.
    It is possible to limit how long to spent here using total_number of_steps_allowed input.

    If total_number_of_steps_allowed=None then calculate all what is in he queue.
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
    """Get the path or information that the path is not yet ready.
    returns None if path calculation is in progress or path_id no longer exists
    returns path if path found (empty list if path does not exist).
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


###
"""
class PathfindManager:
    '''Manages requests for path calculations and returns the resulting path once it is ready.
    The continue_pathfinding function is called by the processor from the main game loop.
    '''

    def __init__(self):
        '''Prepares structures to keep the path calculation status.'''
        self._req_queue = [] # list of PathfindRequest objects
        self._req_lookup = dict() # lookup for PathfindRequest based on their req_id
        self._next_req_id = 0 # last calc id generated
        logger.debug(f'PathfindManager created.')

    def __str__(self):
        '''PathfindManager information.'''
        return f'{self._req_queue=}\n{self._req_lookup=}\n{self._next_req_id=}'

    def request_path(self, graph: dict, start: tuple, goal: tuple, search: str='BFS'):
        '''Registers PathfindRequest with the processor and enqueue it for processing.

        :returns: int - Path Request ID
        '''
        # Create PathFindRequest object
        try:
            path_req = PathfindRequest(graph=graph, start=start, goal=goal, option=PathfindOption[search])
        except KeyError:
            raise ValueError(f'Requested pathfinding search {search=} is not defined. Available searchs are: ' +
                             f'{PathfindOption._member_names_}.')

        # Generate new calc_id under which the path_request is stored
        req_id = self._next_req_id
        self._next_req_id += 1

        # Generate ID and Register it in the dictionary
        self._req_lookup.update({req_id: path_req})
        logger.debug(f'PathfindRequest registered under {req_id=}')

        # Add calc request to the calculation queue
        self._req_queue.append(path_req)
        logger.debug(f'Pathfinding request {req_id=} added into the queue for processing. Total enqued requests {len(self._req_queue)=}')

        # Return the new ID
        return req_id

    def continue_pathfinding(self, max_steps=None):
        '''try part of the path calculation for all paths in the queue.
        It is possible to limit how long to spent here using total_number of_steps_allowed input.

        If total_number_of_steps_allowed=None then calculate all what is in he queue
        '''
        # Quit if there is no path for calculation
        if len(self._req_queue) == 0: return

        # How many cycles we can spend on each path calculation in the queue
        max_steps_per_calc = max_steps // len(self._req_queue) if max_steps is not None else None
        
        for path_req in self._req_queue.copy():
            finished, path = path_req.search.proceed(no_of_steps=max_steps_per_calc)
            if finished:
                # remove from queue and continue with next one
                logger.debug(f'Pathfinding request fulfilled and path calculation finished')
                self._req_queue.remove(path_req)

    def get_path(self, req_id: int):
        '''Get the path or information that the path is not yet ready.
        returns None if path calculation is in progress or path_id no longer exists
        returns path if path found (empty list if path does not exist)
        '''
        
        # Find the path using the ID
        path_req = self._req_lookup.get(req_id, None) # if not found return None

        # If no such path_id exists
        if path_req is None:
            logger.debug(f'{req_id=} does not exists and/or path already obtained.')
            return None
        
        # If calculation is still running
        if not path_req.search.finished: 
            logger.debug(f'{req_id=} calculation is still in progress.\nDetails:\n{path_req.search}')
            return None

        # If finished
        #  Remove from the dictionaty _req_lookup
        self._req_lookup.pop(req_id)

        # Extract only checkpoints - if wanted
        if path_req.options.value.checkpoints: path_req.search.filter_checkpoints()

        # Add start coordinates - if wanted
        if path_req.options.value.start: path_req.search.include_start()
        
        # Return resulting path
        return path_req.search.get_path_result()
"""

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
