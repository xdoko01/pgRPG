
''' Demonstrates how to work with allowlists (whitelists) and denylists (blacklists).

	This method is used for filtering the entities to be processed by collision processors.

	Scenarios:
		- Allow collision with only single entity 1
			allowlist = {1}, denylist = {}
		- Allow collision with entities 1 and 2
			allowlist = {1,2}, denylist = {}
		- Allow collision with all entities
			allowlist = {}, denylist = {}
		- Allow collision with no entity
			allowlist = {}, denylist = {"ALL"}
		- Allow collision with all entities except entities 2,3
			allowlist = {}, denylist = {2,3}

'''

def allow_deny_list_filter(input: set, allowlist: set, denylist: set) -> set:
	''' Takes input set and filters its members based on provided
	allowlist and denylist. Function outputs the resulting set.
	'''

	# If allowlist is empty set, allow all entities in the collision_list
	allowlist = allowlist if allowlist else input

	# If denylist is {"all"}, it blocks all collisions
	denylist = input if denylist == {"ALL"} else denylist

	# Result is set difference between allowed and denied entities
	return(allowlist - denylist)

def allow_deny_item_filter(input, allowlist : set={}, denylist : set={}) -> bool:
	'''Takes value on input and checks it against allowlist and denylist
	values. Returns True if the value on the input is allowed and False
	if it is denied.
	'''

	# Deny item if all items should be denied
	if denylist == {"ALL"}: 
		return False

	# Allowlist is defined but the input value is not there
	elif allowlist and input not in allowlist: 
		return False

	elif input in denylist: 
		return False
	
	else:
		return True


if __name__ == '__main__':

	# Input sets
	collision_list = {1,2,3,4,5,6,7,8,9}
	allowlist = {4,5}
	denylist = {2,3,4}

	print(allow_deny_list_filter(collision_list, allowlist, denylist))
	
	print({col_entity for col_entity in collision_list if allow_deny_item_filter(col_entity, allowlist, denylist)})
