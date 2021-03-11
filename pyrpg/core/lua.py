''' pyrpg.core.lua module
'''
import lupa
from lupa import LuaRuntime

global lua_runtime
lua_runtime = LuaRuntime(unpack_returned_tuples=True)

# Define Lua function to translate python dict to lua table
_lua_dict_to_table_fnc = lua_runtime.eval('''
     function(d)
         local t = {}
         for key, value in python.iterex(d.items()) do
             t[key] = value
         end
         return t
     end
 ''')

def _dict_to_table(dict):
    ''' Returns Lua table from Python dictionary.
    '''
    return _lua_dict_to_table_fnc(lupa.as_attrgetter(dict))
