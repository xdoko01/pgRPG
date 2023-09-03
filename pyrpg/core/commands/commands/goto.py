''' Module implementing goto command
'''

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_goto, alias=module_name)

def cmd_goto(*args, **kwargs):
    ''' Goto command always returns exception. By doing that
    it always skips to unit defined by index in IF-EXCEPTION-GOTO
    '''
    return -1
