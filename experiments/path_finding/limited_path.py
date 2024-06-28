""" Calculate the path in predefined parts, so that the system does not spend a lot of time
    in one frame causing freezing the game.

    Object PathCalculation holds all the information about the progress of finding the path.
"""

from abc import ABC
from collections import namedtuple

Vec2 = namedtuple('Vec2', ('x','y'))

class Node:
    def __init__(self, state, parent):
        self.state = state #tuple
        self.parent = parent #node
        #self.cost = cost 
        #self.action = action #up, down left right


class StackFrontier:
    def __init__(self):
        self.frontier = []
    
    def __str__(self):
        return self.frontier

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)
    
    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("Empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("Empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class PathCalculation(ABC):
    def continue_search(self, no_of_steps):
        pass

class BFS(PathCalculation):
    
    def __init__(self, graph: dict, start: Vec2, goal: Vec2):
        # Inputs
        self.graph = graph
        self.start = Node(state=start, parent=None) # Init the search
        self.goal = goal 

        # Helpers
        self.explored = set()
        self.frontier = QueueFrontier()
        self.frontier.add(self.start) # Init the search
        self.num_explored = 0
        self.finished = False
        
        # Outputs
        self.path = [] # resulting path
    
    def __str__(self):
        return f"{self.num_explored=}\n{self.explored=}\n{self.frontier=}\n{self.finished=}"

    def continue_search(self, no_of_steps=None):
        """Perform the search. If no_of_steps is done, search until goal is found or
        there is no path. Else, only perform specified number of steps.

        No path found, returns (self.finished=True, self.path=[])
        Path found, returns (self.finished=True, self.path=path)
        Calculation in progress (self.finished=False, self.path=[])
        """

        
        # Count the calculation steps
        counter = 0

        # Keep looping until solution found
        while no_of_steps is None or counter < no_of_steps:

            # Increase the counter
            counter += 1

            # If nothing left in frontier, then no path and no solution
            if self.frontier.empty():
                self.finished = True
                return (self.finished, self.path)

            # Choose node from the frontier
            node = self.frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:

                # Follow parent nodes to find solution
                while node.parent is not None:
                    self.path.append(node.state)
                    node = node.parent
                self.path.reverse()
                self.finished = True
                return (self.finished, self.path) # return solution
            
            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbours to frontier
            for state, costs in self.graph[node.state]: # iterate all the possible neighbours
                if not self.frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node)
                    self.frontier.add(child)
        
        # If the calculated will continue, return None
        self.finished = False
        return (self.finished, self.path) 


class PathCalcManager:
    '''Manages requests for path calculations and returns them once they are ready.
    It is called regularly by the processor.
    '''
    _queue: list # list of PathCalculation objects
    _paths: dict

    def request_calc_path(self, map: Map, start: Vect, finish: Vect):
        '''Process request for path calculation. 
        Creates the request (ID) and puts the calculation in the queue.

        :returns: UUID - Calc Path Request ID
        '''
        # Create new path calculation object
        new_path_calc = PathCalculation(map, start, finish)

        # Generate ID and Register it in the dictionary
        _paths.update({new_id: new_path_calc})

        # Add the object at the end of the queue
        _queue.add(new_path_calc)

        # Return the new ID
        returns new_id

    def get_path(self, path_id):
        '''Get the path or information that the path is not yet ready.'''
        
        # Find the path using the ID
        calc_path_object = self._paths[path_id]

        # Ask if it is done with calculation
        if not calc_path_object.finished: return False

        # Remove it from dictionary
        self._paths.delete[path_id]

        # return the result
        return calc_path_object.path

    def continue_calc_paths(self, total_number_of_steps_allowed=30):
        '''try part of the path calculation for all paths in the queue.
        It is possible to limit how long to spent here using total_number of_steps_allowed input.
        '''
        
        # How many cycles we can spend on each path calculation in the queue
        no_steps_for_one_callc_path_allowed = total_number_of_steps_allowed // len(self._queue)
        
        for path_calc in self._queue:
            finished = path_calc.continue_search(no_steps_to_do=no_steps_for_one_callc_path_allowed)
            if finished:
                # remove from queue and continue with next one
                self._queue.remove()


if __name__ == "__main__":

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
    
    search = BFS(graph=map_graph, start=(1,1), goal=(4,2))

    found = False

    while not found:

        found, path = search.continue_search(no_of_steps=3)
        print(search)

    print(path)