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

		for_parse = 'sum' ... ValueError

		for parse = 'sum()'
	'''

	try:
		start_var = for_parse.index("(")
		end_var = for_parse.index(")")
	except ValueError:
		raise ValueError(f'Function string "{for_parse}" has incorrect format.')

	vars = []

	for v in for_parse[start_var+1:end_var].split(","):

		v = v.strip() # Get rid of wite-spaces
		if len(v) == 0: continue # Skip empty strings
		v = int(v) if v.isdigit() else v # Convert numbers if number
		vars.append(v)

	return (for_parse[:start_var], vars)

if __name__ == '__main__':

	# Test of translate_str
	for_trans = "hello %player. You have scored %score and achieved %level of experience."
	trans_dict = {"player": "O. Dokoupil", "score": 500, "level": 25}

	print(translate_str(for_trans=for_trans, trans_dict=trans_dict, prefix='%'))

	# Test of parse_fnc_str
	for_parse = 'sum(1,2)'
	for_parse = 'sum(1,    2,    4)'
	for_parse = 'sum()'
	for_parse = 'sum'
	for_parse = 'sum)('
	for_parse = 'tmp_crate(4, 3)'

	fnc_name, fnc_vars = parse_fnc_str(for_parse)
	print(f'Fnc name: {fnc_name}, fnc vars: {fnc_vars}')

	'''
	start_var = for_parse.index("(")
	end_var = for_parse.index(")")
	print(f'Name part: "{for_parse[:start_var]}", \
		Variable part: "{for_parse[start_var+1:end_var]}" \
		List of values: {for_parse[start_var+1:end_var].split(",")} \
		Cleared values: {[ v.strip() for v in for_parse[start_var+1:end_var].split(",") if len(v) > 0]}')
	'''

