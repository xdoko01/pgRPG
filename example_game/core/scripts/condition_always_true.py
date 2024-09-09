def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=script_condition_always_true, alias=module_name)

def script_condition_always_true(event, *args, **kwargs):
    return True
