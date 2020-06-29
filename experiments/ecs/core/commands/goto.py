''' Module implementing goto command
'''

def cmd_goto(*args, **kwargs):
    ''' Goto command always returns exception. By doing that
    it always skips to unit defined by index in IF-EXCEPTION-GOTO
    '''
    return -1
