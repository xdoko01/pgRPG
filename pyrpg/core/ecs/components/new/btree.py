''' Module "pyrpg.core.ecs.components.btree" contains
BTree component implemented as a BTree class.

Use 'python -m pyrpg.core.ecs.components.new.btree -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component
from pyrpg.core.btrees.btree import Blackboard, create_tree, print_tree

class BTree(Component):
    ''' Entity can perform commands stored in its brain that is represented.
    by the BTree component. Conditions and Actions are represented by the leaf
    nodes, so called behaviours. The functionality itself is performed by the
    scripts that are called by the leaf nodes.

    The decision logic is represented by the parent nodes.

    Using blackboard, nodes can share the information between themselves.

    Used by:
        - BTreeProcessor

    Example of JSON definition:
        {
            "type": "BTree", 
            "params": {
                "blackboard": {
                    "$target": "player01"
                },
                "tree": {
                    "type": "Selector",
                    "name": "AI Root",
                    "children": [
                        "experiments/bt/chase_player($target)",
                        "experiments/bt/patrol()",
                        {
                            "type": "Behavior",
                            "name": "Wait"
                        }
                    ]
                }
            }
        }

    Tests:
        >>> c = BTree(tree={"type": "Behavior", "name": "Wait"})
    '''

    __slots__ = ['blackboard', 'root', 'running_behavior']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new BTree component.

            Parameters:
                :param blackboard: List of commands to execute
                :type blackboard: list

                :param tree: Definition of the tree in the form of dict.
                :type tree: dict
        '''

        super().__init__()

        try:
            self.blackboard = Blackboard(bb=kwargs.get('blackboard', {}))
            self.running_behavior = self.blackboard.running_behavior
            self.root = create_tree(parent=None, json_tree=kwargs['tree'], blackboard=self.blackboard)
            print_tree(self.root)
        except ValueError:
            # Notify component factory that initiation has failed
            raise ValueError

    def process_result(self, result):
        ''' Processes the result of processed command and updates 
        the tree node statuses.

        Overview:
            Function is called by command manager.

        Parameters:
            :param result: In case of successfull cmd finish returns 0
            :type result: int

        Called from:
            command manager -> process_game_commands function
        '''
        # Notify the running node about the result
        self.blackboard.running_behavior.set_result(result)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
