""" Calculate the path in predefined parts, so that the system does not spend a lot of time
    in one frame causing freezing the game.

    Object PathCalculation holds all the information about the progress of finding the path.
"""
from typing import Protocol, Iterable
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

class PathCalculation(Protocol):
    graph: dict
    start: Vec2
    goal: Vec2
    path: list
    finished: bool

    def proceed(self, no_of_steps):
        pass

    def include_start(self):
        '''Adds start position to the resulting path'''
        assert self.finished, f'Cannot add start to not calculated path.'
        self.path = [self.start] + self.path
        return self
    
    def filter_checkpoints(self):
        '''Extract only points from the path where
        direction is changed - checkpoints.

        Path needs to include start point and end point.
        '''

        # Add the start node
        self.include_start()

        if len(self.path) < 2: return self.path

        movement = None
        checkpoints = []

        for i in range(len(self.path)-1):
            if (self.path[i+1].state[0] - self.path[i].state[0] , self.path[i+1].state[1] - self.path[i].state[1]) != movement:
                checkpoints.append(self.path[i])
                movement = (self.path[i+1].state[0] - self.path[i].state[0], self.path[i+1].state[1] - self.path[i].state[1])

        # Always append end 
        checkpoints.append(self.path[-1])
        
        # Always remove start
        checkpoints.pop(0)

        self.path = checkpoints
        return self.path

    def get_path_result(self):
        path = []
        for p in self.path:
            path.append(p.state)
        return path

class BFS(PathCalculation):
    
    def __init__(self, graph: dict, start: Vec2, goal: Vec2):
        # Inputs
        self.graph = graph
        self.start = start
        self.goal = goal

        # Helpers
        self.explored = set()
        self.frontier = QueueFrontier()
        self.num_explored = 0
        self.finished = False
        
        # Outputs
        self.path = []# resulting path

        # Search init
        self.start = Node(state=self.start, parent=None) # Init the search
        self.frontier.add(self.start) # Init the search

    def __str__(self):
        return f"{self.num_explored=}\n{self.explored=}\n{self.frontier=}\n{self.finished=}"

    def proceed(self, no_of_steps=None):
        """Perform the search. If no_of_steps is done, search until goal is found or
        there is no path. Else, only perform specified number of steps.

        No path found, returns (self.finished=True, self.path=[])
        Path found, returns (self.finished=True, self.path=path)
        Calculation in progress (self.finished=False, self.path=[])
        """

        # Check if path can be found (start and goal exists in graph)
        if self.start.state not in self.graph or self.goal not in self.graph:
            self.finished = True
            return (self.finished, self.path)
        
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
                    #self.path.append(node.state)
                    self.path.append(node)
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
        
        # If the calculation will continue, return None
        self.finished = False
        return (self.finished, self.path) 


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
    path = []

    while not found:

        found, path = search.proceed(no_of_steps=3)
        print(search)

    # finished
    print(f'Raw path: {path=}')
    print(f'Path as list of points: {search.get_path_result()=}')
    search.filter_checkpoints()
    print(f'Path with only checkpoints {search.get_path_result()=}')
    search.include_start()
    print(f'Path with only checkpoints and start point {search.get_path_result()=}')


    