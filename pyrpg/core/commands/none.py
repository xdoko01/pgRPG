''' Module implementing none command
'''

def cmd_none(*args, **kwargs):
    ''' Empty command - Null object pattern.
    It is useful if we want some action keys to do nothing
    '''
    print('Empty command returning SUCCESS')

    return 0
