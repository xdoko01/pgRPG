# pip install lupa - Lupa 1.9
import lupa
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

print(lua.eval('1+1'))

lua_func = lua.eval('function(f, n) return f(n) end')

def python_add1(n):
	return n+1

print(lua_func(python_add1, 5))

# Run hello world in lua
lua.eval('print("Hello World!")')

# Define variable in lua
lua.execute('local a')

# Define some variable in lua and use it in lua
lua.execute('local some = "some string" print(some)')
g = lua.globals
print(g)

# Define some variable in python and use it in lua
py_var = 'I am python string'
lua_func = lua.eval('function(py_world) print(py_world) end')
lua_func(py_var)

###########################################
# Define class in python and call it in lua
###########################################
class TestClass():
	def help(self, h):
		print(f'this is help for "{h}".')
		

game = TestClass()

# Define lua script - using both local lua variable and global python code
lua_script = '''local i = 0 for i = 1,10,1 do print(game.help(i)) end'''
#lua_script = '''print(python.buildins.*)'''

# Wrap the script so that it can use python global object 'game'
#lua_script_wrapped = 'function(game) ' + lua_script + 'end'
lua_script_wrapped = 'function(game, print_fnc) print = print_fnc ' + lua_script + ' end'

# Prepare function that executes the script and call it with the python global game reference
lua_func = lua.eval(lua_script_wrapped)
lua_func(game, print)


###########################################
# Define python function that converts python dict to lua table
###########################################

lua_dict_to_table_fnc = lua.eval('''
     function(d)
         local t = {}
         for key, value in python.iterex(d.items()) do
             t[key] = value
         end
         return t
     end
 ''')

def dict_to_table(d):
	return lua_dict_to_table_fnc(lupa.as_attrgetter(d))

def alias_to_entity(): dict_to_table(game.alias_to_entity)

lua local alias_to_entity = lua.alias_to_entity()
