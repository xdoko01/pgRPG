''' Commands package

Contains all the commands from the game.

Every command is implemented as a function.

Every command function must return 0 value on success or negative value on exception. 
This is important for managing the proper sequence of commands stored in Brain component. 
'''

from .loop import *
from .wait import *
from .wait_key import *
from .goto import *
from .none import *

from .new_move_add import *
from .new_move_noadd import *
from .new_move_vect_noadd import *
from .new_move_auto import *
from .new_move_to import *
from .new_move_to_target import *
from .new_move_to_target_range import *

from .new_attack import *
from .new_attack_full import *
from .new_guard import *


from .new_modify_brain import *

from .btree.move_to import cmd_move_to as cmd_btree_move_to
from .btree.dummy import cmd_dummy
from .btree.bb_set_globals import cmd_bb_set_globals
from .btree.bb_set_comp_globals import cmd_bb_set_comp_globals
from .btree.bb_set_locals import cmd_bb_set_locals
from .btree.move_to_target_range import cmd_move_to_target_range
from .btree.attack_full import cmd_attack_full


__all__ = [
    'cmd_loop',
    'cmd_wait',
    'cmd_wait_key',
    'cmd_goto',
    'cmd_none',

    'cmd_new_move_add',
    'cmd_new_move_noadd',
    'cmd_new_move_vect_noadd',
    'cmd_new_move_auto',
    'cmd_new_move_to',
    'cmd_new_move_to_target',
    'cmd_new_move_to_target_range',

    'cmd_new_attack',
    'cmd_new_attack_full',
    'cmd_new_guard',

    'cmd_new_modify_brain',

    'cmd_btree_move_to',
    'cmd_dummy',
    'cmd_bb_set_globals',
    'cmd_bb_set_comp_globals',
    'cmd_bb_set_locals',
    'cmd_move_to_target_range',
    'cmd_attack_full'

]

CMD_DICT = {
    'loop' : cmd_loop,
    'wait' : cmd_wait,
    'wait_key' : cmd_wait_key,
    'goto' : cmd_goto,
    'none' : cmd_none,

    'new_move_noadd' : cmd_new_move_noadd,
    'new_move_add' : cmd_new_move_add,
    'new_move_vect_noadd' : cmd_new_move_vect_noadd,
    'new_move_auto' : cmd_new_move_auto,
    'new_move_to' : cmd_new_move_to,
    'new_move_to_target' : cmd_new_move_to_target,
    'new_move_to_target_range' : cmd_new_move_to_target_range,

    'new_attack' : cmd_new_attack,
    'new_attack_full' : cmd_new_attack_full,
    'new_guard' : cmd_new_guard,

    'new_modify_brain' : cmd_new_modify_brain,

    'btree.move_to': cmd_btree_move_to,
    'dummy': cmd_dummy,
    'bb_set_globals': cmd_bb_set_globals,
    'bb_set_comp_globals': cmd_bb_set_comp_globals,
    'bb_set_locals': cmd_bb_set_locals,
    'btree.move_to_target_range': cmd_move_to_target_range,
    'btree.attack_full': cmd_attack_full

}

def get_cmd_fnc(cmd_str):
    ''' Returns the function implementing command that is represented by the string.
    In case the command is not recognized, empty command is returned
    '''
    return CMD_DICT.get(cmd_str, cmd_none)
