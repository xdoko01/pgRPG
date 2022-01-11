from pyrpg.core.config.lua import LUA_RUNTIME

# Define Lua function to translate python dict to lua table
_lua_dict_to_table_fnc = LUA_RUNTIME.eval('''
     function(d)
         local t = {}
         for key, value in python.iterex(d.items()) do
             t[key] = value
         end
         return t
     end
 ''')

# Function used from lua script to help translate dictionary to the table
def _dict_to_table(dict):
    ''' Returns Lua table from Python dictionary.
    '''
    return _lua_dict_to_table_fnc(lupa.as_attrgetter(dict))

# Define Lua function to translate python list to lua table
_lua_list_to_table_fnc = LUA_RUNTIME.eval('''
     function(L)
         local t, i = {}, 1
         for item in python.iter(L) do
             t[i] = item
             i = i + 1
         end
         return t
     end
 ''')

# Function used from lua script to help translate list to the table
def _list_to_table(list):
    ''' Returns Lua table from Python list.
    '''
    return _lua_list_to_table_fnc(list)
