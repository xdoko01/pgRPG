"""Allow/deny list filtering for entity sets.

Provides allowlist and denylist filtering used primarily by collision
processors to determine which entities should interact.
"""

def allow_deny_list_filter(input: set, allowlist: set, denylist: set) -> set:
	"""Filter a set using allowlist and denylist rules.

	An empty allowlist permits all items. A denylist of ``{"ALL"}``
	blocks everything.

	Args:
		input: Set of items to filter.
		allowlist: Set of allowed items. Empty means allow all.
		denylist: Set of denied items. ``{"ALL"}`` denies everything.

	Returns:
		Filtered set after applying allow/deny rules.
	"""

	# If allowlist is empty set, allow all entities in the collision_list
	allowlist = allowlist if allowlist else input

	# If denylist is {"all"}, it blocks all collisions
	denylist = input if denylist == {"ALL"} else denylist

	# Result is set difference between allowed and denied entities
	return(allowlist - denylist)

def allow_deny_item_filter(input, allowlist : set={}, denylist : set={}) -> bool:
	"""Check whether a single item passes allow/deny filtering.

	Args:
		input: Item to check.
		allowlist: Set of allowed items. Empty means allow all.
		denylist: Set of denied items. ``{"ALL"}`` denies everything.

	Returns:
		True if the item is allowed, False if denied.
	"""

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
