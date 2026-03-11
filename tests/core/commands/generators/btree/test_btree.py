"""Tests for pgrpg.core.commands.generators.btree.btree — BTree behavior tree."""

from pathlib import Path

from pgrpg.core.commands import CommandStatus, Command
from pgrpg.core.commands.generators.btree.btree import BTree


# --- Test data fixtures (from original btree_tests.py) ---

b_tree_data = {
    "blackboard": {},
    "cmd_tree": {
        "type": "Selector",
        "name": "AI Root",
        "children": [
            {
                "type": "Sequence",
                "name": "Chase Player",
                "children": [
                    {"type": "Behavior", "name": "Rotate", "command": "rotate_cmd"},
                    {"type": "Behavior", "name": "Chase", "command": "chase_cmd"},
                    {"type": "Behavior", "name": "MoveTo", "command": "moveto_cmd"},
                ],
            },
            {
                "type": "Sequence",
                "name": "Patrol",
                "children": [
                    {"type": "Behavior", "name": "FindPatrol", "command": "findpatrol_cmd"},
                    {"type": "Behavior", "name": "MoveTo2", "command": "moveto2_cmd"},
                    {"type": "Behavior", "name": "Wait", "command": "wait_cmd"},
                ],
            },
            {"type": "Behavior", "name": "FallbackWait", "command": "fallbackwait_cmd"},
        ],
    },
}

b_tree_repeater = {
    "blackboard": {},
    "cmd_tree": {
        "type": "Repeater",
        "name": "Repeat 3 times",
        "repeat": 3,
        "children": [
            {
                "type": "Sequence",
                "name": "Simple Seq",
                "children": [
                    {"type": "Behavior", "name": "Step1", "command": "step1_cmd"},
                    {"type": "Behavior", "name": "Step2", "command": "step2_cmd"},
                ],
            }
        ],
    },
}

b_tree_repeater_infinite = {
    "blackboard": {},
    "cmd_tree": {
        "type": "Repeater",
        "name": "Repeat forever",
        "repeat": 0,
        "children": [
            {"type": "Behavior", "name": "Action", "command": "action_cmd"},
        ],
    },
}

b_tree_repeat_until_fail = {
    "blackboard": {},
    "cmd_tree": {
        "type": "RepeatUntilFail",
        "name": "Repeat until fail",
        "children": [
            {"type": "Behavior", "name": "Action", "command": "action_cmd"},
        ],
    },
}


def _factory(cmd):
    """Create Command namedtuple from a list or pass through strings."""
    if cmd is None:
        return None
    if isinstance(cmd, list):
        return Command(name=cmd[0], params=cmd[1], entity_id=None)
    return Command(name=cmd, params={}, entity_id=None)


def _make_tree(tree_data):
    return BTree(tree_def=tree_data, cmd_factory=_factory, val_check=False)


def _run_steps(btree, results):
    """Run the tree for len(results) steps, feeding the given CommandStatus values."""
    for r in results:
        if btree._root_node.is_completed:
            break
        btree.get_command()
        btree.notify_command_start()
        btree.process_command_result(result=r)


# --- Tests ---


def test_btree_sequence_all_success():
    """Selector -> first Sequence succeeds when all children succeed."""
    btree = _make_tree(b_tree_data)
    results = [CommandStatus.SUCCESS] * 3  # Rotate, Chase, MoveTo
    _run_steps(btree, results)
    assert btree._root_node.is_completed


def test_btree_selector_falls_through_on_failure():
    """First Sequence fails -> Selector tries second Sequence."""
    btree = _make_tree(b_tree_data)
    # Rotate fails -> Chase Player Sequence fails -> Selector tries Patrol
    results = [
        CommandStatus.FAILURE,  # Rotate fails -> Chase fails
        CommandStatus.SUCCESS,  # FindPatrol
        CommandStatus.SUCCESS,  # MoveTo2
        CommandStatus.SUCCESS,  # Wait -> Patrol succeeds
    ]
    _run_steps(btree, results)
    assert btree._root_node.is_completed


def test_btree_selector_fallback_to_last():
    """Both Sequences fail -> Selector reaches FallbackWait behavior."""
    btree = _make_tree(b_tree_data)
    results = [
        CommandStatus.FAILURE,  # Rotate fails -> Chase fails
        CommandStatus.FAILURE,  # FindPatrol fails -> Patrol fails
        CommandStatus.SUCCESS,  # FallbackWait succeeds
    ]
    _run_steps(btree, results)
    assert btree._root_node.is_completed


def test_btree_get_command_returns_command():
    """get_command() returns a non-None Command on first call."""
    btree = _make_tree(b_tree_data)
    cmd = btree.get_command()
    assert cmd is not None


def test_btree_restart_brain():
    """restart_brain() resets the tree so it can run again."""
    btree = _make_tree(b_tree_data)
    _run_steps(btree, [CommandStatus.SUCCESS] * 3)
    assert btree._root_node.is_completed

    btree.restart_brain()
    assert not btree._root_node.is_completed

    cmd = btree.get_command()
    assert cmd is not None


def test_btree_repeater_finite():
    """Repeater with repeat=3 runs child 3 times then completes."""
    btree = _make_tree(b_tree_repeater)
    # Each iteration: Step1 SUCCESS, Step2 SUCCESS = 2 steps per repeat, 3 repeats = 6
    results = [CommandStatus.SUCCESS] * 6
    _run_steps(btree, results)
    assert btree._root_node.is_completed


def test_btree_repeater_infinite_does_not_complete():
    """Repeater with repeat=0 (infinite) never completes on its own."""
    btree = _make_tree(b_tree_repeater_infinite)
    results = [CommandStatus.SUCCESS] * 10
    _run_steps(btree, results)
    # Should not be completed — it repeats forever
    assert not btree._root_node.is_completed


def test_btree_repeat_until_fail_stops_on_failure():
    """RepeatUntilFail completes when child returns FAILURE."""
    btree = _make_tree(b_tree_repeat_until_fail)
    results = [
        CommandStatus.SUCCESS,
        CommandStatus.SUCCESS,
        CommandStatus.FAILURE,  # This should cause completion
    ]
    _run_steps(btree, results)
    assert btree._root_node.is_completed
