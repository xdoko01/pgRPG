''' Module implementing bb_set_locals command for behavior tree's
running Behavior node.
'''
import logging

# Logger init
logger = logging.getLogger(__name__)

def cmd_bb_set_locals(*args, **kwargs):
    ''' Set/overwrite the values of the local blackboard for currenty
    running behavior.
    Must be called from cmd_init, not from cmd_process
    '''

    # BTree reference
    bb_locals = kwargs["brain"].blackboard.running_behavior.bb

    # Must be set to RUNNING if it is part of cmd_init
    # Otherwise it will end the whole Behavior node.
    # This command does not make sence anywhere else than cmd_init
    res = kwargs.get("result", "RUNNING")

    # Save the key-value to the local blackboard of the running behavior
    bb_locals.update({**bb_locals, **{k: v for k, v in kwargs if k not in ['world', 'brain', 'keys', 'events', 'current_time', 'entity']}})

    return res
