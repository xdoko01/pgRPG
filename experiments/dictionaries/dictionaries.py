def _create_dict_list(path: list, value) -> dict:
	'''Create a dictionary(tree) specified by the list of
	embeded keys. The value is put to the deepest key.'''

	new_dict = {path[-1] : value}

	for p in reversed(path[:-1]):
		new_dict = { p : new_dict}
	
	return new_dict

def _create_dict_str(path: str, value) -> dict:
	'''Create a dictionary(tree) specified by path and
	put the value to the deepest key.'''

	return _create_dict_list(path.split("."), value)


def set_dict_value(d: dict, path: str, value):
	'''Create a new path in the dictionary and
	put the required value there.
	'''
	# For narrowed down dictionary
	parse_dict = d

	# For tracing the path
	parse_path = path.split(".")

	# For keeping track how deep we made it in the dict, starting in the root
	depth = 0

	try:
		# Dive deep into the dictionary
		for p in parse_path[:-1]:
			parse_dict = parse_dict[p]
			depth += 1

		# Set the value on the leaf
		parse_dict[parse_path[-1]] = value

	except KeyError:
		# If path no longer exists
		parse_dict.update(_create_dict_list(parse_path[depth:], value))

def get_dict_value(d: dict, path: str, not_found=None):
	'''Get the value from the dictionary that
	is on the path specified by the path string.'''

	# For narrowed down dictionary
	parse_dict = d
	try:
		# Dive deep into the dictionary
		for p in path.split("."):
			parse_dict = parse_dict[p]
		
		return parse_dict
	except KeyError:
		return not_found

def add_dict_value(d: dict, path: str, value) -> int:
	'''Add new value to the dictionary. Do not overwrite
	the existing value but convert to set and add it to
	the set.
	'''
	try:
		assert isinstance(value, int), f'Value must be integer.'

		current_value = get_dict_value(d, path)

		# If there is currently already some value stored
		if current_value:
			assert (isinstance(current_value, list) or isinstance(current_value, set) or isinstance(current_value, tuple)), f'Current Value must be iterable.'
			new_value = set(current_value)
			new_value.add(value)
			set_dict_value(d, path, new_value)
			return len(new_value)
		else:
			set_dict_value(d, path, set([value]))
			return 1
	except AssertionError:
		raise

def get_all_dict_values(d: dict):
	'''Parse the dictionary and get all the values as
	generator.
	By calling list(get_all_dict_values(d)) or
	set(get_all_dict_values(d)) the result can be obtained
	in form of the set or the list.
	'''

	for val in d.values():
		if isinstance(val, dict):
			yield from get_all_dict_values(val)
		elif isinstance(val, list) or isinstance(val, set):
			for v in val:
				yield v
		else:
			yield val


if __name__ == '__main__':

	# Test dictionary
	d={
		"items": {
			"weapons": {
				"sword": {
					"weapon" :[2,3],
					"ammo": [5,6]
				},
				"bow": {
					"weapon": [6,7]
				}
			},
			"coins": {
				"golden" : [10,22,33],
				"copper": [1,2,3]
			}
		}
	}

	# Get all available sword weapon
	print(f"{get_dict_value(d, 'items.weapons.sword.weapon')}")

	# Get number of golden coins available
	print(f"Number of golden coins: {len(get_dict_value(d, 'items.coins.golden', not_found=[]))}")

	# Get number of silver coins available
	print(f"Number of silver coins: {len(get_dict_value(d, 'items.coins.silver', not_found=[]))}")

	set_dict_value(d, 'items.coins.silver', 'value')

	print(d)

	print(f'New dictionary: {_create_dict_str("one.two.three", 75121)}')
	print(f'New dictionary: {_create_dict_list(["one", "two", "three", "four"], 75121)}')

	new = _create_dict_str('items.weapons.bow', 1)
	get_dict_value(new, 'items.weapons.sword', 5)
	get_dict_value(new, 'items.weapons.spear', 15)

	print(new)

	get_dict_value(new, 'items.weapons.sword', 6)

	print(new)

	add_dict_value(d, 'items.coins.golden', 34)
	add_dict_value(d, 'items.coins.golden', 35)
	add_dict_value(d, 'items.coins.golden', 38)

	add_dict_value(d, 'items.coins.iron', 555)
	add_dict_value(d, None, 777)

	print(f"Len: {len(get_dict_value(d, 'items.coins.golden'))}")
	print(d)

	print(f'All dict values: {set(get_all_dict_values(d))}')