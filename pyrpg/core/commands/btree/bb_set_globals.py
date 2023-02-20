''' Module implementing bb_set_globals command for behavior tree
'''
import logging

# Logger init
logger = logging.getLogger(__name__)

def cmd_bb_set_globals(*args, **kwargs):
    ''' Set/overwrite the value on the behavior tree global blackboard
    '''

    # BTree reference
    bb_globals = kwargs["brain"].blackboard

    # Must be set to RUNNING if it is part of cmd_init
    # Otherwise it will end the whole Behavior node
    res = kwargs.get("result", "SUCCESS")

    # Update blackboard in the Btree entity - do not put the global command keys there
    bb_globals.update({k: v for k, v in kwargs.items() if k not in ['world', 'brain', 'keys', 'events', 'current_time', 'entity']})

    return res
