''' Calculate the path in predefined parts, so that the system does not spend a lot of time
    in one frame causing freezing the game.

    Object PathCalculation holds all the information about the progress of finding the path.

        https://www.youtube.com/watch?v=WbzNRTTrX0g

    Terminology:
    ------------
     - agent - entity perceiving its environment
     - state - configuration of agant in its environment
     - initial state - state where agent begins
     - actions - choices that can be done in given state
     - transition model - a description of what state results from performing any applicable action in any state
     - state space - set of all states reachable from the initial state by any sequence of actions
     - goal test - way to determine whether a given state is a goal state
     - path cost - numerical cost associated with given path
     - optimal solution - solution with the lowest path cost among all solutions

    Functions:
    ----------
     - Actions(s) - set of actions that can be executed in state s
     - Result(s,a) - returns the state resulting from performing action a in status s

    Structures:
    ----------
     - Node - keeps track of 
      - a STATE, 
      - a PARENT (node that generated this node), 
      - an ACTION (applied to parent to get node), 
      - a PATH COST (from initial state to the node)

     - Frontier - keeps nodes to visit - stack(DFS), queue (BFS), priority queue(A*)
     - Explored set - keeps already explored nodes
    
    Algorithm:
    ----------
     - Start with a frontier that contains the initial state
     - Repeat:
       - If the frontier is empty, then no solution
       - Remove the node from the frontier
       - If the node contains the goal state, return the solution
       - Add the node to the explored set
       - Expand the node, add resulting nodes to the frontier if they arent already in the frontier or already visited

'''
class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier:
    def __init__(self):
        self.frontier = []
    
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

class Maze:
    def __init__(self, filename):
        
        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("Maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("Maze must have exactly one goal")
        
        # Determine height and width
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        
        self.solution = None

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("X", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i,j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def solve(self):

        # Keep track of number of points visited
        self.num_explored = 0

        # Initialize frontier to the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize empty explored ser
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in tfrontier, then no path
            if frontier.empty():
                raise Exception("No solution")
            
            # Choose node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []

                # Follow parent nodes to find solution
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            
            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbours to frontier
            for action, state in self.neighbours(node.state):
                if not frontier.contains_state(state) and state not in self.explored
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)
