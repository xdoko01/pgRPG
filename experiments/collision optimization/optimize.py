'''
Experimentation with collision optimization. 

It is not needed to perform N^2 comparisons between entities. It should
be sufficient to perform (N^2 - N)/2 comparisons

Currently, with N=5, following checks are performed

	11 12 13 14 15
	21 22 23 24 25
	31 32 33 34 35
	41 42 43 44 45
	51 52 53 54 55

Newly, only following checks are necessary

	12 13 14 15
	   23 24 25
	      34 35
		     45
'''

from collections import namedtuple

# simulate entity with ignore collisions list
Entity = namedtuple('Entity', ['id', 'ignore'])

entities = [
	Entity(id=1, ignore={2,3}),
	Entity(id=2, ignore={3,4}),
	Entity(id=3, ignore={1,4}),
	Entity(id=4, ignore={1,2}),
	Entity(id=5, ignore={2})
]

# Prepare list where results will be stored for every entity
data = [{'hits': set(), 'vectors' : []} for _ in entities] #{1: {'hits' : {}}

# Prepare list where whitelists will be stored for every entity
blacklist = [ent.ignore for ent in entities]

print(data)

# use enumarate
for ent_moved_idx, ent_moved in enumerate(entities):
	for ent_other_idx, ent_other in enumerate(entities[ent_moved_idx+1:]):
		print(f' Testing entities {ent_moved.id}-{ent_other.id} for collision')
		ent_other_idx = ent_moved_idx + 1 + ent_other_idx
		
		# Ignore if on blacklist
		if ent_other.id not in blacklist[ent_moved_idx]:
			data[ent_moved_idx]['hits'].add(ent_other.id)
		
		if ent_moved.id not in blacklist[ent_other_idx]:
			data[ent_other_idx]['hits'].add(ent_moved.id)
	
	print(f'Writing to entity {ent_moved} new component with content: {data[ent_moved_idx]}.')

print(data)
