"""
    Calculate dictionary representing an oriented graph from the map
    data represented as 2D field
"""

map_data = [1,1,1,1,1,1,
            1,0,0,0,0,1,
            1,0,0,0,0,1,
            1,1,1,1,1,1]

map_width = 6

map_dirs = ((1,0), (-1,0), (0,1), (0,-1))



def idx_to_coords(i: int, map_width: int) -> tuple:
    return (i % map_width, i // map_width)

def coords_to_idx(coords: tuple, map_width: int) -> int:
    return coords[0] + (coords[1]*map_width)

def map_to_graph(map_data: list, map_width: int, map_dirs: tuple) -> dict:

    graph = dict()

    for i, m in enumerate(map_data):
        if m == 0: # can be stepped on
            node = idx_to_coords(i, map_width)
            neighbours = []
            for d in map_dirs:
                dir_idx = i + coords_to_idx(d, map_width)
                if map_data[dir_idx] == 0: # can be stepped on
                    # record in the dictionary
                    neighbours.append((idx_to_coords(dir_idx, map_width), 1)) # coordinates and cost
            graph.update({node: neighbours})
    
    return graph

import pprint

pprint.pprint(map_to_graph(map_data, map_width, map_dirs))
