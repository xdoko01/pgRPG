'''
    Aim of this test module is to find a way of creating dictionary
    of all callable methods of an object and call the method based
    on this dictionary and method name in string
'''

class TestObject:
    ''' Just testing object having some method that I will use
    for calling tests
    '''
    def __init__(self):
        self.pos = [0,0]
        print('Init executed')

    def do_something(self):
        ''' Test method that will be called "remotely"
        '''
        return 'Something'

    def do_something_else(self):
        ''' Test method that will be called "remotely"
        '''
        return 'Something Else'

t = TestObject()

# Print list of available methods and properties
print(dir(t))

# Print list of object methods
print([method_name for method_name in dir(t)
                  if callable(getattr(t, method_name))] )

# Process func
print(getattr(t,'do_something'))
print(getattr(t,'do_something')())

print(str(getattr(t,'do_something')))
processFunc = (lambda s: s)
s = processFunc(getattr(t,'do_something')())
print(s)

# COnsole has app object
# In order header to display dynamic data
#   - console passes App to Header
#   - header has name of the function as config parameter
#   - by performing following the function is called
#       - check that the function exists in APP object and it is callable
#       - do this at the moment function is assigned to header, i.e. only once        
#        if 'do_something' in [method_name for method_name in dir(t)
#                  if callable(getattr(t, method_name))]
#            self.func = getattr(t, method_name)
#       - for processing see lines below
# if callable(getattr(t, method_name))
processFunc = (lambda s: s())
print(processFunc(getattr(t,'do_something')))
#s = processFunc(getattr(t,'do_something')())

# Build dictionary that has function name and function from list of functions
fnc_dir = { method_name : getattr(t, method_name) for method_name in dir(t)
                  if callable(getattr(t, method_name)) }

print(fnc_dir)
func = fnc_dir.get('do_something', None)
print(processFunc(func))

processFunc2 = (lambda f: fnc_dir.get(f)())
print('NEW TEST ' + processFunc2('do_something'))

# Use formated string and call the function from there
dynamic_text = 'Return of do_something: {do_something} Return of something else: {do_something_else}'
#dynamic_text2 = f'Return of do_something: {processFunc2("do_something")} Return of something else: {processFunc2("do_something_else")}
dynamic_text3 = 'Return of do_something: {processFunc2("do_something")} Return of something else: {processFunc2("do_something_else")}'

# print(dynamic_text.format(processFunc(func)))
print(dynamic_text.format(**fnc_dir))

# how to extract values 

# HOW IT MIGHT WORK
# *****************
# - Header has reference to console
# - Header init checks, if dynamic text is enabled
#   'Return of do_something: {do_something} Return of something else: {do_something_else}'
#   - If enabled then extract the function names into dictionary self.fnc = {}
#     and fill it with method_name : getattr(self.console, method_name)
# - In Header update function 
#   - create the string from something like this
#           print(dynamic_text.format(**fnc_dir))


d = { method_name : processFunc2(method_name) for method_name in fnc_dir.keys()}

print(dynamic_text.format(**{ method_name : getattr(t, method_name)() for method_name in fnc_dir}))


print('adfasfsadf {}'.format(processFunc(fnc_dir.get('do_something', None))))
print(dynamic_text2)
print(f'{dynamic_text3}')

# How to store dynamic_text2 as a text and then add F to it
