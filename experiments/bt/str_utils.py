def translate_str(for_trans: str, trans_dict: dict, prefix: str='$') -> str:
	'''Substitute words in for_trans string that start
	with prefix by values from the trans_dict dictionary.

	Tests:
		>>> for_trans = "hello %player. You have scored %score and achieved %level of experience."
		>>> trans_dict = {"player": "O. Dokoupil", "score": 500, "level": 25}
		>>> print(translate_str(for_trans=for_trans, trans_dict=trans_dict, prefix='%'))
		hello O. Dokoupil. You have scored 500 and achieved 25 of experience.
	'''
	trans_str = for_trans

	for k, v in trans_dict.items():
		trans_str = trans_str.replace(prefix + str(k), str(v))
	
	return trans_str

def convert_str(s: str):
	'''Tries to convert expression in the string.
	If not successful, return back the original
	string value.
	
	Tests:
		>>> print(f"{convert_str('1')}, {convert_str('1.52')}, {convert_str('ahoj')}")
		1, 1.52, ahoj
		>>> print(convert_str('{"a": 25}'))
		{'a': 25}
		>>> print(convert_str('[1, 2]'))
		[1, 2]
		>>> print(convert_str('["1", "2"]'))
		['1', '2']
	'''
	try:
		return eval(s)
	except (NameError, SyntaxError):
		return s

def get_kw_from_str(s: str, sep: str='=') -> tuple:
	'''Parse string where on the left side is key and
	after the separator is value and extract it into
	two strings, one containing key and other the value.
	
	Tests:
		>>> get_kw_from_str('$arg=5')
		('$arg', '5')
		>>> get_kw_from_str(' $arg   =   hello')
		('$arg', 'hello')
		>>> get_kw_from_str('$map')
		('$map', '')

		# Get only keys and args from the list
		>>> [get_kw_from_str(i)[0] for i in ["$tileX=0", "$tileY=0", "$map"]]
		['$tileX', '$tileY', '$map']
	'''
	return (s[:s.find(sep)].strip(), s[s.find(sep)+1:].strip()) if s.count(sep) > 0 else (s, '')

def parse_fnc_list(for_parse: list) -> tuple:
	'''Parses function call defined as a list into 
	function name and list of parameters + kwargs.

	Tests:
		>>> print(parse_fnc_list(['sum', [1, 2]]))
		('sum', [1, 2], {})
		>>> print(parse_fnc_list(['sum']))
		('sum', [], {})
		>>> print(parse_fnc_list(['sum', [1, 2], {'a': 23}]))
		('sum', [1, 2], {'a': 23})
		>>> print(parse_fnc_list(['sum', {'a': 23}]))
		('sum', [], {'a': 23})
	'''

	for_parse = for_parse[:3] # we are interested only in the first 3 values
	l = len(for_parse) 

	assert l >= 1, f"function is missing name and arguments"
	assert isinstance(for_parse[0], str), f"Incorect name of the template: {for_parse[0]}"
	
	args = []
	kwargs = {}

	if l == 2:
		if isinstance(for_parse[1], list): 
			args = for_parse[1]
		elif isinstance(for_parse[1], dict): 
			kwargs = for_parse[1]
		else:
			raise ValueError
	elif l >= 3:
		assert isinstance(for_parse[1], list), f'Second item must be list of arguments'
		assert isinstance(for_parse[2], dict), f'Third item must be dict of kwargs'
		args = for_parse[1]
		kwargs = for_parse[2]

	return (for_parse[0], args, kwargs)

def parse_fnc_str(for_parse: str, sep: str=',') -> tuple:
	'''Parses function call defined as a string into 
	function name and list of parameters.

	IMPORTANT: Separator is ',' by default. If you want to 
	have objects such as lists or dicts to be handled correctly,
	separator must be changed to something else, for example ';'

	Tests:
		>>> print(parse_fnc_str('sum(1, 2)'))
		('sum', [1, 2], {})
		>>> print(parse_fnc_str('sum'))
		('sum', [], {})
		>>> print(parse_fnc_str('sum()'))
		('sum', [], {})
		>>> print(parse_fnc_str('sum(1;2;3; map=unknown; position=[3,5])', sep=';'))
		('sum', [1, 2, 3], {'map': 'unknown', 'position': [3, 5]})
		>>> print(parse_fnc_str('sum(name="Ota"; 1;2;3; map=unknown; position=["3","5"])', sep=';'))
		('sum', [1, 2, 3], {'name': 'Ota', 'map': 'unknown', 'position': ['3', '5']})
		'''

	start_pos = None
	end_pos = None

	args_as_str = ''

	for pos, c in enumerate(for_parse):
		if c == '(':
			start_pos = pos
			assert end_pos is None, f'Closing bracket preceeds opening bracket'
			assert start_pos > 0, f'Name cannot start with opening bracket'
		elif c == ')':
			end_pos = pos
			assert start_pos is not None, f'Closing bracket preceeds opening bracket'
			assert end_pos > 0, f'Name cannot start with closing bracket'
			args_as_str = for_parse[start_pos+1:end_pos]
			break

	# Now, the parameters including all spaces are stored in args variable as a str

	# Now we have exactly determined the function name
	fnc_name = for_parse[:start_pos]

	# Now we need to get all argumet from args_as_str string as a list and as a dict
	_, args, kwargs = get_args_kwargs_from_list(for_parse=args_as_str.split(sep))

	return (fnc_name, args, kwargs)

def get_args_kwargs_from_list(for_parse: list) -> tuple:
	'''Takes parameters as a list of strings on the input,
	parse it an returns all args, non kwargs and kwargs.
	
	Tests:
		>>> print(get_args_kwargs_from_list(["1","2"]))
		([1, 2], [1, 2], {})
		>>> print(get_args_kwargs_from_list(['$tilex=0', '$tiley=0', '$map']))
		(['$tilex', '$tiley', '$map'], ['$map'], {'$tilex': 0, '$tiley': 0})
	'''
	args = []
	kwargs = {}
	all = []
	
	for v in for_parse:

		v = v.strip() # Get rid of wite-spaces
		if len(v) == 0: continue # Skip empty strings

		# Normal arg, not kwarg
		if '=' not in v:
			v = convert_str(v) # Convert to the proper type
			args.append(v) # add to the args list
			all.append(v) # add it to the list of all arguments

		# Kwarg, not arg
		else:
			key, value = get_kw_from_str(v, sep='=')
			key=key.replace(' ','') # Key cannot contain any space
			kwargs.update({key: convert_str(value)}) # Convert value to the proper type and store
			all.append(key) # add it to the list of all arguments


	return (all, args, kwargs)

"""
def parse_fnc_str_obsolete(for_parse: str) -> tuple:
	'''Parses function call defined as a string into 
	function name and list of parameters.

	Examples:
		for_parse = 'sum(1, 2)'
		returns ('sum', [1, 2])

		for_parse = 'sum'
		returns ('sum', [])

		for parse = 'sum()'
		returns ('sum', [])
	'''

	start_pos = None
	end_pos = None
	args = ''

	for pos, c in enumerate(for_parse):
		if c == '(':
			start_pos = pos
			assert end_pos is None, f'Closing bracket preceeds opening bracket'
			assert start_pos > 0, f'Name cannot start with opening bracket'
		elif c == ')':
			end_pos = pos
			assert start_pos is not None, f'Closing bracket preceeds opening bracket'
			assert end_pos > 0, f'Name cannot start with closing bracket'
			args = for_parse[start_pos+1:end_pos]
			break
	
	vars = []

	for v in args.split(","):

		v = v.strip() # Get rid of wite-spaces
		if len(v) == 0: continue # Skip empty strings
		v = int(v) if v.isdigit() else v # Convert numbers if number
		vars.append(v)

	return (for_parse[:start_pos], vars)
"""

if __name__ == '__main__':
	import doctest
	doctest.testmod()


