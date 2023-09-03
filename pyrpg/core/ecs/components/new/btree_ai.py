''' Module "pyrpg.core.ecs.components.btree" contains
BTree component implemented as a BTree class.

Use 'python -m pyrpg.core.ecs.components.new.btree_ai -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

from pyrpg.core.commands.generators.btree.btree import BTree, InvalidBehaviorTreeError

from pyrpg.core.config.paths import BTREE_PATH

class BTreeAI(Component):
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
                "cmd_tree": {
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
        >>> import pygame
        >>> pygame.init() # doctest: +ELLIPSIS
        (...)
        >>> c = BTreeAI(tree={"type": "Behavior", "name": "Wait", "command": "dummy_command"})
    '''

    __slots__ = ['generator']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new BTreeAI component.

            Parameters:
                :param btree: Object representing the behavior tree
                :type btree: BTree
        '''

        super().__init__()

        try:
            self.generator = BTree(tree_def=kwargs, template_path=BTREE_PATH, val_check=True)
        except InvalidBehaviorTreeError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
