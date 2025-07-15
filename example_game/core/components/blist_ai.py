''' Module "pyrpg.core.ecs.components.blist_ai" contains
BListAI component implemented as a BList class.

Use 'python -m core.components.blist_ai -v' to run
module tests.
'''
import logging

# Create logger
logger = logging.getLogger(__name__)

from pyrpg.core.ecs import Component

from pyrpg.core.commands import cmd_factory
from pyrpg.core.commands.generators.blist.blist import BList, InvalidBehaviorListError


class BListAI(Component):
    ''' Entity can perform commands stored in its brain that is represented.
    by the BList component. Conditions and Actions are represented by the list of commands. 

    Using blackboard, commands can share the information between themselves.

    Used by:
        - BListProcessor

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

    Tests:
        >>> import pygame
        >>> pygame.init() # doctest: +ELLIPSIS
        (...)
        >>> c = BListAI(tree={"type": "Behavior", "name": "Wait", "command": "dummy_command"})
    '''

    # In case of incorrect brain structure definition, start to rotate
    FAILSAFE_LIST = {
            'blackboard': {},
            'cmd_list': [
                {'name': 'Move Up', 'command': ['move_dir', {'moves': ['up'], 'absolute': True}]},
                {'name': 'Move Left', 'command': ['move_dir', {'moves': ['left'], 'absolute': True}]},
                {'name': 'Move Down', 'command': ['move_dir', {'moves': ['down'], 'absolute': True}]},
                {'name': 'Move Right', 'command': ['move_dir', {'moves': ['right'], 'absolute': True}]},
                {'type': 'goto', 'jmp_to': 0}
            ]
        }

    __slots__ = ['generator']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new BListAI component.

            Parameters:
                :param blist: Object representing the behavior tree
                :type blist: BTree
        '''

        super().__init__()


        try:

            self.generator = BList(
                list_def=kwargs,
                cmd_factory=cmd_factory # create Commands
            )
        
        except InvalidBehaviorListError:

            # Notify component factory that initiation has failed
            logger.error(f'The Behavior List is invalid. Substituing with default behavior.')
            
            self.generator = BList(
                list_def=BListAI.FAILSAFE_LIST,
                cmd_factory=cmd_factory # create Commands
            )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
