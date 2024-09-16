''' Module "pyrpg.core.ecs.components.new.brain_ai" contains
BrainAI component implemented as a BTree or BList class.

Use 'python -m pyrpg.core.ecs.components.new.brain_ai -v' to run
module tests.
'''
from dataclasses import dataclass

import logging

# Create logger
logger = logging.getLogger(__name__)

from pyrpg.core.ecs.components.component import Component

from pyrpg.core.commands import cmd_factory, CommandGeneratorMock
from pyrpg.core.commands.generators.btree.btree import BTree, InvalidBehaviorTreeError
from pyrpg.core.config.filepaths import FILEPATHS # for BTREE_PATH

from pyrpg.core.commands.generators.blist.blist import BList, InvalidBehaviorListError


class BrainAI(Component):
    ''' Entity can perform commands stored in its brain that is represented.
    by the BTree or BList (command genetaror)component.

    Using blackboard, nodes can share the information between themselves.

    Used by:
        - BrainAIProcessor

    Example of JSON definition:
        {
            "type": "BList", 
            "params": {
                'blackboard': {},
                'cmd_list' : [
                    {"line": 0, 'on_fail_jmp': 0, 'command': ["new_guard", {"enemy": "player01", "radius": 200, "update_time_ms": 2000}] },
                    {"line": 1, 'on_fail_jmp': 1, 'command': ["new_move_to_target", {"target" : "player01", "radius": 50, "update_time_ms": 500}]},
                    {"line": 2, 'on_fail_jmp': 2, 'command': ["new_attack_full", {"attack_time_ms": 500}]},
                    {"line": 3, 'jmp_to': 1, "type": "Goto"}
                ]
            }
        }
        
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
        >>> c = BrainAI(cmd_tree={"type": "Behavior", "name": "Wait", "command": "dummy_command"})
        >>> c = BrainAI(cmd_list=[{"line": 0, "type": "Behavior", "name": "Move", "command": "dummy_command", "on_fail_jmp": None}])
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
        ''' Initiate values for the new BrainAI component.

            Parameters:
                :param generator: Object representing the command generator
                :type generator: CommandGenerator
        '''

        super().__init__()

        # Create AI generator
        if kwargs.get('cmd_tree') is not None:
            try:
                self.generator = BTree(tree_def=kwargs, cmd_factory=cmd_factory, template_path=FILEPATHS["BTREE_PATH"], val_check=True)
            except InvalidBehaviorTreeError:
                logger.error(f'The Behavior Tree is invalid. Substituing with default behavior.')
                self.generator = BTree(tree_def=BrainAI.FAILSAFE_TREE, cmd_factory=cmd_factory, template_path=FILEPATHS["BTREE_PATH"], val_check=True)
        elif kwargs.get('cmd_list') is not None:
            try:
                self.generator = BList(list_def=kwargs, cmd_factory=cmd_factory)
            except InvalidBehaviorListError:
                logger.error(f'The Behavior List is invalid. Substituing with default behavior.')
                self.generator = BTree(tree_def=BrainAI.FAILSAFE_TREE, cmd_factory=cmd_factory, template_path=FILEPATHS["BTREE_PATH"], val_check=True)
        else:
            logger.error(f'The Behavior is invalid. Substituing with default behavior.')
            self.generator = BTree(tree_def=BrainAI.FAILSAFE_TREE, cmd_factory=cmd_factory, template_path=FILEPATHS["BTREE_PATH"], val_check=True)

# Mock component for usage in tests
@dataclass
class BrainAIMock:
    generator: CommandGeneratorMock = CommandGeneratorMock()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
