class Node:
    '''Test class representing node of the tree to experiment to yield 
    values from the children.'''
    
    def __init__(self, name, children=[]):

        self.children = children
        self.name = name

    def tick(self):
        
        print(f'Hello, I am {self.name} and you have just ticked me.')
        
        for child in self.children:            
            yield child.tick()

        yield self

if __name__ == "__main__":

    # Create tree
    l3_node_1 = Node("l3_node_1")
    l3_node_2 = Node("l3_node_2")
    l3_node_3 = Node("l3_node_3")
    l3_node_4 = Node("l3_node_4")

    l2_node_1 = Node("l2_node_1", children=[l3_node_1, l3_node_2])
    l2_node_2 = Node("l2_node_2", children=[l3_node_3, l3_node_4])

    l1_node_1 = Node("l1_node_1", children=[l2_node_1, l2_node_2])

    for i in range(5):
        next(l1_node_1.tick())
    
    #call_l2 = next(call_root)
    #call_l3 = next(call_l2)
    # Tick the leaf
    #for child in l1_node_1.tick():
    #    print(f'child: {child.name}')
    #    child.tick()
