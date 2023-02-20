''' Module implementing dummy command for testing purposes
'''
from pyrpg.core.btrees.btree import TreeNode

def cmd_dummy(*args, **kwargs):
    ''' Dummy testing command, returning the required result
    and printing msg on the terminal
    '''

    res = kwargs.get('result', 'SUCCESS')
    msg = kwargs.get('msg', '')

    print(f'Dummy command: "{msg}". Returning "{TreeNode.Status(res)}"')

    return TreeNode.Status(res)
