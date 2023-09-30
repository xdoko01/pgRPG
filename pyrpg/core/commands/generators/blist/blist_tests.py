'''For tests, run
python -m pyrpg.core.commands.generators.blist.blist_tests -v
'''
import pygame
from pyrpg.core.commands import CommandStatus, Command

from .blist import BList
from random import randint

res = {
        'R': CommandStatus.RUNNING,
        'S': CommandStatus.SUCCESS,
        'F': CommandStatus.FAILURE
}

def test_blist(blist:BList, res_generator, steps=True):
    i=1
    while not blist._is_finished:
        print(f'STEP {i}')
        print(f'A/ Getting the command from the blist {blist.get_command()=}')
        print(f'B/ Notifying about the command execution start')
        blist.notify_command_start()
        print(f'B.1/ Blackboard updated ... {blist.bb.init_time = }, {blist.bb.duration = }, {blist.bb.tick_count = }')
        print(f'C/ Executing the command.')
        cmd_result = next(res_generator)
        print(f'C.1/ Returning result from the command {cmd_result=}')
        print(f'D/ Processing the command result')
        blist.process_command_result(result=cmd_result)
        print(f'E/ Printing the blist at the end of the cycle')
        blist.print()

        if steps: input(f'Press any key to continue ...')


'''On SUCCESS, continue to the next line'''
'''If not finished, switch to RUNNING status'''
'''On FAILURE, jump to exception line if defined. If not defined, continue'''
# line and name and type are optional on Behavior but manddatory on Looper
b_list_data1 = {
	'blackboard': {},
	'cmd_list': [
		{"line": 0, "type": "Behavior", "name": "Move", "command": ["test_cmd_1", {"bb_key": "bb_target_pos_comp", "bb_entity": "$target_in", "component": "new.position:Position"}], "on_fail_jmp": None},
		{"line": 1, "type": "Behavior", "name": "Move", "command": ["test_cmd_2", {"bb_key": "bb_target_pos_comp", "bb_entity": "$target_in", "component": "new.position:Position"}], "on_fail_jmp": None},
		{"line": 2, "type": "Loop", "name": "Looper1", "repeat": 2, "jmp_to": 0},
		{"line": 3, "type": "Goto", "name": "goto", "jmp_to": -1}
	]
}

b_list_data2 = {
	'blackboard': {},
	'cmd_list' : [
		{"line": 0, 'on_fail_jmp': 0, 'command': ["new_guard", {"enemy": "player01", "radius": 200, "update_time_ms": 2000}] },
		{"line": 1, 'on_fail_jmp': 1, 'command': ["new_move_to_target", {"target" : "player01", "radius": 50, "update_time_ms": 500}]},
		{"line": 2, 'on_fail_jmp': 2, 'command': ["new_attack_full", {"attack_time_ms": 500}]},
		{"line": 3, 'jmp_to': 1, "type": "Goto"}
	]
}

b_list_data3 = {
	'blackboard': {},
	'cmd_list' : []
}

def factory(cmd):
    '''Create Command named tuple from the list.'''
    return Command(name=cmd[0], params=cmd[1]) if cmd is not None else cmd


if __name__ == '__main__':
    pygame.init()

    blist = BList(list_def=b_list_data2, cmd_factory=factory)

    test_blist(blist, res_generator=(res[r] for r in 'SSRRRRRSRRRS'), steps=True)


