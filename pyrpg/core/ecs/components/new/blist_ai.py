''' Module "pyrpg.core.ecs.components.blist_ai" contains
BListAI component implemented as a BList class.

Use 'python -m pyrpg.core.ecs.components.new.blist_ai -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

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

    __slots__ = ['generator']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new BListAI component.

            Parameters:
                :param blist: Object representing the behavior tree
                :type blist: BTree
        '''

        super().__init__()

        try:
            self.generator = BList(list_def=kwargs)
        except InvalidBehaviorListError:
            # Notify component factory that initiation has failed
            raise ValueError

if __name__ == '__main__':
    import doctest
    doctest.testmod()
