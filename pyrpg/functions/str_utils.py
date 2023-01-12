def translate_str(for_trans: str, trans_dict: dict, prefix: str) -> str:
	'''Substitute words in for_trans string that start
	with prefix by values from the trans_dict dictionary.
	'''

	trans_str = for_trans

	for k, v in trans_dict.items():
		trans_str = trans_str.replace(prefix + str(k), str(v))
	
	return trans_str

def parse_fnc_str(for_parse: str) -> tuple:
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

if __name__ == '__main__':

	# Test of translate_str
	for_trans = "hello %player. You have scored %score and achieved %level of experience."
	trans_dict = {"player": "O. Dokoupil", "score": 500, "level": 25}

	print(translate_str(for_trans=for_trans, trans_dict=trans_dict, prefix='%'))

	# Test of parse_fnc_str
	fnc_test_strings = [ 'sum', 'sum()', 'sum(1,2)', 'sum(1,    2,    4)', 'tmp_crate(4, 3)', 'dsfa()sdf']
	
	for fnc_str in fnc_test_strings:
		fnc_name, fnc_vars = parse_fnc_str(fnc_str)
		print(f'Orig: "{fnc_str} -> "fnc name: "{fnc_name}" fnc vars: "{fnc_vars}"')



