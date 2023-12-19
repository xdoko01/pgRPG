MAP_WIDTH = 20
MAP_HEIGHT = 10
MAP = '11111111111111111111' + \
      '10000000000000000001' + \
      '10000000000000000001' + \
      '10000011111000000001' + \
      '10000010000000000001' + \
      '10000010010000000001' + \
      '10000011110000000001' + \
      '10000000000000000001' + \
      '10000000000000000001' + \
      '11111111111111111111'


from pygame.math import Vector2


class Map:

    def __init__(self, data_str: str, width: int, height: int):
        assert len(data_str) == width * height
        self.data_str = data_str # map as string
        self.width = width
        self.height = height
        self.data = [[int(self.data_str[h*self.width+w]) for h in range(self.height)] for w in range(self.width)] # map as 2D array


    def show(self):
        for h in range(self.height):
            for w in range(self.width):
                print(f' {self.data[w][h]} ', end="")
            print()

    def get_tile(self, x, y):
        assert 0 <= x <= self.width - 1
        assert 0 <= y <= self.height - 1
        return self.data[x][y]

    def is_walkable(self, step: Vector2):
        '''Is within map and is walkable (no obstacle)'''
        return (0 <= step.x <= self.width - 1) and (0 <= step.y <= self.height - 1) and self.data[step.x][step.y] == 0

    def draw_path(self, path):
        for i, p in enumerate(path):
            self.data[p.x][p.y] = chr(i+97)
        self.show()


def get_path_bfs(
        map: Map, 
        start: Vector2, 
        end: Vector2,
        inc_start: bool=False, 
        avail_moves: tuple=(
            Vector2(0,-1), #up
            Vector2(0,1), #down
            Vector2(-1,0), #left
            Vector2(1,0) #right
        )
    ) -> list:

    visited = set()
    queue = []
    pre = dict()
    path = []

    # Record where I am
    queue.append(start)

    while queue:

        curr = queue.pop(0)

        # Check if I am on the end - finish
        if curr == end:
            # Print the path
            path.append(end)
            pre_path = pre[tuple(end)]
            while pre_path != start:
                path.append(pre_path)
                pre_path = pre[tuple(pre_path)]

            if inc_start: path.append(start)
            path.reverse() # from start to end
            return path


        else:
            # Mark as visited
            visited.add(tuple(curr))

            for move in avail_moves:
                next = Vector2(curr.x + move.x, curr.y + move.y)
                if map.is_walkable(next) and next not in visited and next not in queue:
                    # Add into the queue
                    queue.append(next)
                    # Remember from which point you are continuing
                    pre[tuple(next)] = tuple(curr)

    return [] # no path found

def get_path_checkpoints(path:list) -> list:
    '''Extract only points from the path where
      direction is changed - checkpoints

    Path needs to include start point and end point.

    Point(x=0, y=1), (0,0) #start
    Point(x=1, y=1), (1,0) #keep - next is changed
    Point(x=1, y=2), (0,1)
    Point(x=1, y=3), (0,1)
    Point(x=1, y=4), (0,1)
    Point(x=1, y=5), (0,1)
    Point(x=1, y=6), (0,1)
    Point(x=1, y=7), (0,1)  #keep - next is changed
    Point(x=2, y=7), (1,0)
    Point(x=3, y=7), (1,0)
    Point(x=4, y=7), (1,0)
    Point(x=5, y=7), (1,0)
    Point(x=6, y=7), (1,0)
    Point(x=7, y=7), (1,0)  #keep - next is changed
    Point(x=7, y=6), (0,-1)
    Point(x=7, y=5), (0,-1)
    Point(x=7, y=4)  (0,-1) #end - always keep
    
        0    1,2 
        1    1,3 ... 0,1 #out
        2    1,4 ... 0,1 #out
        3    1,5 ... 0,1 #out
        4    1,6 ... 0,1 #out
        5    1,7 ... 0,1 #keep
        6    2,7 ... 1,0

    '''

    assert len(path) >= 2 # at least start and end

    movement = None
    checkpoints = []

    for i in range(len(path)-1):
        if (path[i+1].x - path[i].x , path[i+1].y - path[i].y) != movement:
            checkpoints.append(path[i])
            movement = (path[i+1].x - path[i].x , path[i+1].y - path[i].y)

    # Always append end 
    checkpoints.append(path[-1])
    
    # Always remove start
    checkpoints.pop(0)

    return checkpoints

def get_graph(map: Map, 
                avail_moves: tuple=(
                    Vector2(0,-1), #up
                    Vector2(0,1), #down
                    Vector2(-1,0), #left
                    Vector2(1,0) #right
    )) -> dict:
    '''Create graph in a form of a dictionary'''

    graph = dict()

    # Go through the whole map - nodes that are walkable only
    for x in range(map.width):
        for y in range(map.height):
            if map.get_tile(x,y) == 0:
                graph[Vector2(x,y)] = set()
                for move in avail_moves:
                    next = Vector2(x + move.x, y + move.y)
                    if map.is_walkable(next):
                        graph[Vector2(x,y)].add(next)

    return graph

if __name__ == "__main__":
   
    map = Map(data_str=MAP, width=MAP_WIDTH, height=MAP_HEIGHT)
    #print(map.data)
    #map.show()
    #print(f'{map.get_tile(x=3, y=0)}')
    #print(f'{map.get_tile(x=19, y=4)}')
    #map.get_path_dfs(start=Point(x=1, y=1), end=Point(x=10, y=3))
    
    #print(f'Only straight moves:')
    #path = get_path_bfs(map=map, start=Point(x=1, y=1), end=Point(x=7, y=4), inc_start=True)
    #map.draw_path(path)
    #print(f'{path=}')
    #print(f'{get_checkpoints(path)=}')

    print(f'With diagonal moves:')
    path = get_path_bfs(map=map, start=Vector2(x=1, y=1), end=Vector2(x=7, y=4), inc_start=True, avail_moves=(
            Vector2(0,-1), #up
            Vector2(1,-1), # upright
            Vector2(1,0), #right
            Vector2(1,1), #downright
            Vector2(0,1), #down
            Vector2(-1,1), #downleft
            Vector2(-1,0), #left
            Vector2(-1,-1) #upleft
        ))
    print(f'{path=}')
    print(f'{get_path_checkpoints(path)=}')
    print(f'{get_graph(map=map)}')

    map.draw_path(path)
