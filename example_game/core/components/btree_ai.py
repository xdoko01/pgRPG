''' Module "pyrpg.core.ecs.components.btree" contains
BTree component implemented as a BTree class.

Use 'python -m pyrpg.core.ecs.components.new.btree_ai -v' to run
module tests.
'''
import logging

# Create logger
logger = logging.getLogger(__name__)

from pyrpg.core.ecs.components.component import Component

from pyrpg.core.commands import cmd_factory
from pyrpg.core.commands.generators.btree.btree import BTree, InvalidBehaviorTreeError

from pyrpg.core.config.filepaths import FILEPATHS # for BTREE_PATH


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

    # In case of incorrect brain structure definition, start to rotate
    FAILSAFE_TREE = {
            'blackboard': {},
            'cmd_tree': {
                'type': 'Repeater',
                'name': 'Repeat',
                'children': [
                    {
                        'type': 'Sequence',
                        'name': 'Move Around',
                        'children': [
                            {'type': 'Behavior', 'name': 'Move Up', 'command': ['move_dir', {'moves': ['up'], 'absolute': True}]},
                            {'type': 'Behavior', 'name': 'Move Left', 'command': ['move_dir', {'moves': ['left'], 'absolute': True}]},
                            {'type': 'Behavior', 'name': 'Move Down', 'command': ['move_dir', {'moves': ['down'], 'absolute': True}]},
                            {'type': 'Behavior', 'name': 'Move Right', 'command': ['move_dir', {'moves': ['right'], 'absolute': True}]}
                        ]
                    }
                ]
            }
        }


    __slots__ = ['generator']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new BTreeAI component.
 
            Parameters:
                :param btree: Object representing the behavior tree
                :type btree: BTree
        '''

        super().__init__()


        try:

            self.generator = BTree(
                tree_def=kwargs, 
                cmd_factory=cmd_factory, 
                template_path=FILEPATHS["BTREE_PATH"], 
                val_check=True
            )

        except InvalidBehaviorTreeError:
            
            logger.error(f'The Behavior Tree is invalid. Substituing with default behavior.')
            self.generator = BTree(
                tree_def=BTreeAI.FAILSAFE_TREE, 
                cmd_factory=cmd_factory, 
                template_path=FILEPATHS["BTREE_PATH"], 
                val_check=True
            )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
