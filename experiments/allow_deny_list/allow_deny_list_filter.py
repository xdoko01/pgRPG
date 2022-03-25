
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

# Input sets
collision_list = {1,2,3,4,5,6,7,8,9}
allowlist = set()
denylist = {2,3}

# If allowlist is empty set, allow all entities in the collision_list
allowlist = allowlist if allowlist else collision_list

# If denylist is {"all"}, it blocks all collisions
denylist = collision_list if denylist == {"ALL"} else denylist

# Result is set difference between allowed and denied entities
allow_collision_with = set(allowlist - denylist)
print(allow_collision_with)