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
from .move_to import *
from .face_entity import *
from .disable_talk import *
from .add_screen import *
from .remove_screen import *
from .toggle_control import *
from .toggle_brain import *
from .toggle_motion import *
from .show_dialog import *
from .move import *
from .attack import *
from .disable_collision import *
from .remove_from_inventory import *
from .add_to_inventory import *
from .set_quest_phase import *

__all__ = [
    'cmd_loop',
    'cmd_wait',
    'cmd_wait_key',
    'cmd_goto',
    'cmd_none',
    'cmd_move_to',
    'cmd_face_entity',
    'cmd_disable_talk',
    'cmd_add_screen',
    'cmd_remove_screen',
    'cmd_toggle_control',
    'cmd_toggle_brain',
    'cmd_toggle_motion',
    'cmd_show_dialog',
    'cmd_move',
    'cmd_attack',
    'cmd_disable_collision',
    'cmd_remove_from_inventory',
    'cmd_add_to_inventory',
    'cmd_set_quest_phase'
]

CMD_DICT = {
    'loop' : cmd_loop,
    'wait' : cmd_wait,
    'wait_key' : cmd_wait_key,
    'goto' : cmd_goto,
    'none' : cmd_none,
    'move_to' : cmd_move_to,
    'face_entity' : cmd_face_entity,
    'disable_talk' : cmd_disable_talk,
    'add_screen' : cmd_add_screen,
    'remove_screen' : cmd_remove_screen,
    'toggle_control' : cmd_toggle_control,
    'toggle_brain' : cmd_toggle_brain,
    'toggle_motion' : cmd_toggle_motion,
    'show_dialog' : cmd_show_dialog,
    'move' : cmd_move,
    'attack' : cmd_attack,
    'disable_collision' : cmd_disable_collision,
    'remove_from_inventory' : cmd_remove_from_inventory,
    'add_to_inventory' : cmd_add_to_inventory,
    'set_quest_phase' : cmd_set_quest_phase
}

def get_cmd_fnc(cmd_str):
    ''' Returns the function implementing command that is represented by the string.
    In case the command is not recognized, empty command is returned
    '''
    return CMD_DICT.get(cmd_str, cmd_none)
