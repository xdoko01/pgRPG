"""String parsing and conversion utilities.

Provides functions for string variable substitution, type conversion,
keyword argument extraction, and function call parsing from strings
and lists.
"""

def translate_str(for_trans: str, trans_dict: dict, prefix: str='$') -> str:
	"""Substitute prefixed words in a string using a translation dictionary.

	Args:
		for_trans: String containing words prefixed with ``prefix``
			to be substituted.
		trans_dict: Mapping of unprefixed keys to replacement values.
		prefix: Character prefix identifying words to substitute.

	Returns:
		String with all matching prefixed words replaced.

	Examples:
		>>> for_trans = "hello %player. You have scored %score and achieved %level of experience."
		>>> trans_dict = {"player": "O. Dokoupil", "score": 500, "level": 25}
		>>> print(translate_str(for_trans=for_trans, trans_dict=trans_dict, prefix='%'))
		hello O. Dokoupil. You have scored 500 and achieved 25 of experience.
	"""
	trans_str = for_trans

	for k, v in trans_dict.items():
		trans_str = trans_str.replace(prefix + str(k), str(v))

	return trans_str

def convert_str(s: str):
	"""Try to evaluate a string as a Python literal.

	Returns the original string if evaluation fails.

	Args:
		s: String to convert.

	Returns:
		Evaluated value (int, float, list, dict, etc.) or the original
		string if conversion is not possible.

	Examples:
		>>> print(f"{convert_str('1')}, {convert_str('1.52')}, {convert_str('ahoj')}")
		1, 1.52, ahoj
		>>> print(convert_str('{"a": 25}'))
		{'a': 25}
		>>> print(convert_str('[1, 2]'))
		[1, 2]
		>>> print(convert_str('["1", "2"]'))
		['1', '2']
	"""
	try:
		return eval(s)
	except (NameError, SyntaxError):
		return s

def get_kw_from_str(s: str, sep: str='=') -> tuple:
	"""Parse a ``key=value`` string into a (key, value) tuple.

	Args:
		s: String containing a key-value pair separated by ``sep``.
		sep: Separator between key and value.

	Returns:
		Tuple of (key, value) with whitespace stripped. If no separator
		is found, returns (s, '').

	Examples:
		>>> get_kw_from_str('$arg=5')
		('$arg', '5')
		>>> get_kw_from_str(' $arg   =   hello')
		('$arg', 'hello')
		>>> get_kw_from_str('$map')
		('$map', '')

		# Get only keys and args from the list
		>>> [get_kw_from_str(i)[0] for i in ["$tileX=0", "$tileY=0", "$map"]]
		['$tileX', '$tileY', '$map']
	"""
	return (s[:s.find(sep)].strip(), s[s.find(sep)+1:].strip()) if s.count(sep) > 0 else (s, '')

def parse_fnc_list(for_parse: list) -> tuple:
	"""Parse a function call defined as a list into name, args, and kwargs.

	Expected format: ``["name", [args], {kwargs}]`` where args and kwargs
	are optional.

	Args:
		for_parse: List of ``[name]``, ``[name, args]``,
			``[name, kwargs]``, or ``[name, args, kwargs]``.

	Returns:
		Tuple of (function_name, args_list, kwargs_dict).

	Examples:
		>>> print(parse_fnc_list(['sum', [1, 2]]))
		('sum', [1, 2], {})
		>>> print(parse_fnc_list(['sum']))
		('sum', [], {})
		>>> print(parse_fnc_list(['sum', [1, 2], {'a': 23}]))
		('sum', [1, 2], {'a': 23})
		>>> print(parse_fnc_list(['sum', {'a': 23}]))
		('sum', [], {'a': 23})
	"""

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
	"""Parse a function call string into name, args, and kwargs.

	Handles strings like ``"sum(1, 2)"`` or ``"sum(a=1; b=2)"`` with
	a configurable argument separator.

	Args:
		for_parse: Function call as a string, e.g. ``"name(arg1, arg2)"``.
		sep: Separator between arguments. Use ``';'`` if arguments
			contain commas (e.g. lists or dicts).

	Returns:
		Tuple of (function_name, args_list, kwargs_dict).

	Examples:
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
		"""

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
	"""Parse a list of string tokens into positional args and keyword args.

	Each token is stripped of whitespace, then classified as either a
	keyword argument (contains ``=``) or a positional argument.

	Args:
		for_parse: List of string tokens to parse.

	Returns:
		Tuple of (all_keys, positional_args, kwargs_dict).

	Examples:
		>>> print(get_args_kwargs_from_list(["1","2"]))
		([1, 2], [1, 2], {})
		>>> print(get_args_kwargs_from_list(['$tilex=0', '$tiley=0', '$map']))
		(['$tilex', '$tiley', '$map'], ['$map'], {'$tilex': 0, '$tiley': 0})
	"""
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

if __name__ == '__main__':
	import doctest
	doctest.testmod()


