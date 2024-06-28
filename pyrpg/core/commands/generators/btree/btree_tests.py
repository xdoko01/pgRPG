'''For tests, run
python -m pyrpg.core.commands.generators.btree.btree_tests -v
'''
import pygame
from pyrpg.core.commands import CommandStatus, Command
from .btree import BTree
from pathlib import Path

from random import randint

res = {
        'R': CommandStatus.RUNNING,
        'S': CommandStatus.SUCCESS,
        'F': CommandStatus.FAILURE
}

def test_btree(btree:BTree, res_generator, steps=True):
    i=0
    while not btree._root_node.is_completed:
        i += 1
        print(f'STEP {i}')
        print(f'A/ Getting Command from Action Node ... ACTION NODE={btree._action_node.name if btree._action_node else None}')
        cmd = btree.get_command()
        print(f'A/ Received dommand from Action Node ... ACTION NODE={btree._action_node.name if btree._action_node else None}, {cmd=}')

        print(f'B/ Notifying Blackboard that command is about to be executed')
        btree.notify_command_start()
        print(f'B/ Blackboard updated ... {btree.bb.init_time = }, {btree.bb.duration = }, {btree.bb.tick_count = }')

        try:
            cmd_result = next(res_generator)
        except StopIteration:
            print(f'Generator out of statuses. Quiting ...')
            break

        print(f'C/ Command executed and returned result {cmd_result=}')

        print(f'D/ Notifying tree about the result and Processing the result in the tree ... ACTION NODE: {btree._action_node.name if btree._action_node else None}')
        btree.process_command_result(result=cmd_result)
        
        print(f'\nTree status at the end of the step ... ACTION NODE: {btree._action_node.name if btree._action_node else None}')
        btree.print_tree()

        if steps: input(f'Press any key to continue ...')

### PUT YOUR TEST TREES HERE ###

b_tree_data_with_templates = {
    "blackboard": {
        "checkpoints": [[0,0],[1,1],[2,2]]
    },

    "cmd_tree": {
            "type": "Selector",
            "name": "AI Root",
            "children": [
                {
                    "template": [
                        "destroy_target",
                        {
                            "$range_in": [[0,0],[1,1],[2,2]]
                        }
                    ]
                },
                {
                    "type": "Behavior",
                    "name": "Wait",
                    "command": "wait_cmd"
                },
                {
                    "template": [
                        "destroy_target",
                        {
                            "$range_in": 300
                        }
                    ]
                }
            ]
        }
    }

b_tree_data = {
    'blackboard': {},
    'cmd_tree': {
        "type": "Selector",
        "name": "AI Root",
        "children": [
            {
                "type": "Sequence",
                "name": "Chase Player",
                "children": [
                    {
                        "type": "Behavior",
                        "name": "Rotate to face BB entry",
                        "command": "Rotate to face BB entry_cmd",
                    },
                    {
                        "type": "Behavior",
                        "name": "BTT_ChasePlayer",
                        "command": "BTT_ChasePlayer_cmd"

                    },
                    {
                        "type": "Behavior",
                        "name": "Move To",
                        "command": "Move_to_cmd"
                    }
                ]
            },
            {
                "type": "Sequence",
                "name": "Patrol",
                "children": [
                    {
                        "type": "Behavior",
                        "name": "BTT_FindRandomPatrol",
                        "command": "BTT_FindRandomPatrol_cmd"
                    },
                    {
                        "type": "Behavior",
                        "name": "Move To",
                        "command": "Move_To_cmd"
                    },
                    {
                        "type": "Behavior",
                        "name": "Wait",
                        "command": "Wait_cmd"
                    }
                ]
            },
            {
                "type": "Behavior",
                "name": "Wait",
                "command": "Wait_cmd"
            }
        ]
    }
}

b_tree_repeat = {
                    "blackboard": {}, 
                    "cmd_tree": {
                                "type": "Sequence",
                                "name": "Make square movement",
                                "children": [
                                    {"name": "Turn Left", "type": "Behavior", "command": ["move_vect", {"vector" : [-1,0], "absolute": True}]},
                                    {"name": "Move Left", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                    {"name": "Turn Down", "type": "Behavior", "command": ["move_vect", {"vector" : [0,1], "absolute": True}]},
                                    {"name": "Move Down", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                    {"name": "Turn Right", "type": "Behavior", "command": ["move_vect", {"vector" : [1,0], "absolute": True}]},
                                    {"name": "Move Right", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                    {"name": "Turn Up", "type": "Behavior", "command": ["move_vect", {"vector" : [0,-1], "absolute": True}]},
                                    {"name": "Move Up", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                    {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]}
                                ]
                            }
}

b_tree_repeat_until_fail = {
                        "blackboard": {}, 
                        "cmd_tree": {
                            "type": "RepeatUntilFail",
                            "name": "Repeat Indefinetelly",
                            "children": [
                                {
                                    "type": "Sequence",
                                    "name": "Make square movement",
                                    "children": [
                                        {"name": "Turn Left", "type": "Behavior", "command": ["move_vect", {"vector" : [-1,0], "absolute": True}]},
                                        {"name": "Move Left", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Turn Down", "type": "Behavior", "command": ["move_vect", {"vector" : [0,1], "absolute": True}]},
                                        {"name": "Move Down", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Turn Right", "type": "Behavior", "command": ["move_vect", {"vector" : [1,0], "absolute": True}]},
                                        {"name": "Move Right", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Turn Up", "type": "Behavior", "command": ["move_vect", {"vector" : [0,-1], "absolute": True}]},
                                        {"name": "Move Up", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]}
                                    ]
                                }
                            ]
                        }
                    }

b_tree_repeater = {
                        "blackboard": {}, 
                        "cmd_tree": {
                            "type": "Repeater",
                            "name": "Repeat 3 times",
                            "repeat": 0,
                            "children": [
                                {
                                    "type": "Sequence",
                                    "name": "Make square movement",
                                    "children": [
                                        {"name": "Turn Left", "type": "Behavior", "command": ["move_vect", {"vector" : [-1,0], "absolute": True}]},
                                        {"name": "Move Left", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Turn Down", "type": "Behavior", "command": ["move_vect", {"vector" : [0,1], "absolute": True}]},
                                        {"name": "Move Down", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Turn Right", "type": "Behavior", "command": ["move_vect", {"vector" : [1,0], "absolute": True}]},
                                        {"name": "Move Right", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Turn Up", "type": "Behavior", "command": ["move_vect", {"vector" : [0,-1], "absolute": True}]},
                                        {"name": "Move Up", "type": "Behavior", "command": ["move_auto", {"duration_ms" : 250}]},

                                        {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]}
                                    ]
                                }
                            ]
                        }
                    }

b_tree_repeater_easy =  {
                        "blackboard": {}, 
                        "cmd_tree": {
                            "type": "Repeater",
                            "name": "Repeat Indefinetelly",
                            "children": [
                                {
                                    "type": "Sequence",
                                    "name": "Make square movement",
                                    "children": [
                                        {"name": "Turn Left", "type": "Behavior", "command": ["move_vect", {"vector" : [-1,0], "absolute": True}]},
                                        {"name": "Wait", "type": "Behavior", "command": ["wait", {"duration_ms" : 1000}]}
                                    ]
                                }
                            ]
                        }
                    }

def factory(cmd):
    '''Create Command named tuple from the list.'''
    return Command(name=cmd[0], params=cmd[1]) if cmd is not None else cmd

if __name__ == '__main__':

    pygame.init() # for blackboard times correctly calculated

    btree = BTree(
        tree_def=b_tree_data_with_templates, # put the tree here
        cmd_factory=lambda x: x, #factory, # create from list with 2 items Command namedtuple
        template_path=Path('pyrpg/resources/btrees'), 
        val_check=False
    )

    btree.print_tree() # print the tree at the beginning

    test_btree(btree, res_generator=(res[r] for r in 'SRSRSRSRSRSRSRSRSRSRSR'), steps=False)

    btree.restart_brain()
    print('AFTER RESTART')
    btree.print_tree()
    test_btree(btree, res_generator=(res[r] for r in 'SSS'), steps=False)

