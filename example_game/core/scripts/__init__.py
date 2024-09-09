''' Scripts package

Contains all the game scripts

Script implements complex game functionalities that can be triggered by events. E.g.
earthquake, fadeouts, changing quests, etc

Every script is implemented as a function.

'''

from .do_nothing import *
from .modify_brain import *
from .exec_python_code import *
from .disable_teleport import *
from .shake_screen import *
from .show_dlg_window import *
from .condition_always_true import *
from .condition_example import *
from .add_msg import *


__all__ = [
    'script_do_nothing',

    # Action scripts
    'script_modify_brain',
    'script_exec_python_code',
    'script_disable_teleport',
    'script_shake_screen',
    'script_show_dlg_window',
    'script_add_msg',

    # Condition scripts
    'script_condition_always_true',
    'script_condition_example'
]

SCRIPT_DICT = {
    'do_nothing' : script_do_nothing,

    # Actions
    'modify_brain' : script_modify_brain,
    'execute_script' : script_exec_python_code,
    'disable_teleport' : script_disable_teleport,
    'shake_screen' : script_shake_screen,
    'show_dlg_window' : script_show_dlg_window,

    'add_msg' : script_add_msg,

    # Conditions
    'condition_always_true' : script_condition_always_true,
    'condition_example' : script_condition_example
}

def get_script_fnc(script_str):
    ''' Returns the function implementing script that is represented by the string.
    '''
    return SCRIPT_DICT.get(script_str, 'do_nothing')