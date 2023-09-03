''' Module implementing none command
'''

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_none, alias=module_name)

def cmd_none(*args, **kwargs):
    ''' Empty command - Null object pattern.
    It is useful if we want some action keys to do nothing
    '''
    print('Empty command returning SUCCESS')

    return 0
