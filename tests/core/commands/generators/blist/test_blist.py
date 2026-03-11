"""Tests for pgrpg.core.commands.generators.blist.blist — BList behavior list."""

from pgrpg.core.commands import CommandStatus, Command
from pgrpg.core.commands.generators.blist.blist import BList


# --- Test data fixtures (from original blist_tests.py) ---

b_list_data1 = {
    "blackboard": {},
    "cmd_list": [
        {"line": 0, "type": "Behavior", "name": "Cmd1", "command": ["test_cmd_1", {"key": "val"}], "on_fail_jmp": None},
        {"line": 1, "type": "Behavior", "name": "Cmd2", "command": ["test_cmd_2", {"key": "val"}], "on_fail_jmp": None},
        {"line": 2, "type": "Loop", "name": "Looper1", "repeat": 2, "jmp_to": 0},
        {"line": 3, "type": "Goto", "name": "goto", "jmp_to": -1},
    ],
}

b_list_data2 = {
    "blackboard": {},
    "cmd_list": [
        {"line": 0, "on_fail_jmp": 0, "command": ["guard", {"enemy": "player01"}]},
        {"line": 1, "on_fail_jmp": 1, "command": ["move_to", {"target": "player01"}]},
        {"line": 2, "on_fail_jmp": 2, "command": ["attack", {"time": 500}]},
        {"line": 3, "jmp_to": 1, "type": "Goto"},
    ],
}

b_list_data3 = {
    "blackboard": {},
    "cmd_list": [],
}


def _factory(cmd):
    """Create Command namedtuple from a list."""
    if cmd is None:
        return None
    return Command(name=cmd[0], params=cmd[1], entity_id=None)


# --- Tests ---


def test_blist_empty_is_finished():
    """A BList with empty cmd_list is immediately finished."""
    blist = BList(list_def=b_list_data3, cmd_factory=_factory)
    assert blist._is_finished


def test_blist_advance_on_success():
    """On SUCCESS, the blist advances to the next line."""
    blist = BList(list_def=b_list_data2, cmd_factory=_factory)
    assert blist._line_idx == 0

    cmd = blist.get_command()
    assert cmd is not None

    blist.notify_command_start()
    blist.process_command_result(CommandStatus.SUCCESS)
    assert blist._line_idx == 1


def test_blist_on_fail_jmp():
    """On FAILURE, the blist jumps to on_fail_jmp line."""
    blist = BList(list_def=b_list_data2, cmd_factory=_factory)
    # Line 0 has on_fail_jmp=0, so failure should keep it at line 0
    blist.get_command()
    blist.notify_command_start()
    blist.process_command_result(CommandStatus.FAILURE)
    assert blist._line_idx == 0


def test_blist_running_stays_on_same_line():
    """On RUNNING, the blist stays on the current line."""
    blist = BList(list_def=b_list_data2, cmd_factory=_factory)
    blist.get_command()
    blist.notify_command_start()
    blist.process_command_result(CommandStatus.RUNNING)
    assert blist._line_idx == 0


def test_blist_goto_jumps():
    """A Goto line jumps to the specified jmp_to line."""
    blist = BList(list_def=b_list_data2, cmd_factory=_factory)
    # Advance to line 3 (Goto with jmp_to=1)
    for _ in range(3):
        blist.get_command()
        blist.notify_command_start()
        blist.process_command_result(CommandStatus.SUCCESS)

    # Now at line 3 (Goto), get_command should process the Goto
    assert blist._line_idx == 3
    blist.get_command()
    # After Goto, should be at line 1
    assert blist._line_idx == 1


def test_blist_loop_repeats():
    """A Loop line repeats the specified number of times."""
    blist = BList(list_def=b_list_data1, cmd_factory=_factory)
    # Lines 0,1 are Behavior, line 2 is Loop(repeat=2, jmp_to=0)
    # First pass: cmd1 SUCCESS, cmd2 SUCCESS -> Loop counter 1
    for _ in range(2):
        blist.get_command()
        blist.notify_command_start()
        blist.process_command_result(CommandStatus.SUCCESS)

    # Now at line 2 (Loop), get_command should jump back to 0
    blist.get_command()
    assert blist._line_idx == 0

    # Second pass
    for _ in range(2):
        blist.get_command()
        blist.notify_command_start()
        blist.process_command_result(CommandStatus.SUCCESS)

    # Loop again
    blist.get_command()
    assert blist._line_idx == 0

    # Third pass — loop counter exhausted, should advance past loop
    for _ in range(2):
        blist.get_command()
        blist.notify_command_start()
        blist.process_command_result(CommandStatus.SUCCESS)

    blist.get_command()
    # Should now be at line 3 (Goto with jmp_to=-1 means finish)
    assert blist._line_idx == 3
